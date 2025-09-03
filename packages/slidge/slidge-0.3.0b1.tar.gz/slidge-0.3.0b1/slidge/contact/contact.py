import datetime
import logging
import warnings
from datetime import date
from typing import TYPE_CHECKING, Generic, Iterable, Iterator, Optional, Union
from xml.etree import ElementTree as ET

from slixmpp import JID, Message, Presence
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.plugins.xep_0292.stanza import VCard4
from slixmpp.types import MessageTypes
from sqlalchemy.exc import IntegrityError

from ..core.mixins import AvatarMixin, FullCarbonMixin
from ..core.mixins.disco import ContactAccountDiscoMixin
from ..core.mixins.recipient import ReactionRecipientMixin, ThreadRecipientMixin
from ..db.models import Contact, ContactSent, Participant
from ..util import SubclassableOnce
from ..util.types import ClientType, LegacyUserIdType, MessageOrPresenceTypeVar

if TYPE_CHECKING:
    from ..core.session import BaseSession
    from ..group.participant import LegacyParticipant


class LegacyContact(
    Generic[LegacyUserIdType],
    AvatarMixin,
    ContactAccountDiscoMixin,
    FullCarbonMixin,
    ReactionRecipientMixin,
    ThreadRecipientMixin,
    metaclass=SubclassableOnce,
):
    """
    This class centralizes actions in relation to a specific legacy contact.

    You shouldn't create instances of contacts manually, but rather rely on
    :meth:`.LegacyRoster.by_legacy_id` to ensure that contact instances are
    singletons. The :class:`.LegacyRoster` instance of a session is accessible
    through the :attr:`.BaseSession.contacts` attribute.

    Typically, your plugin should have methods hook to the legacy events and
    call appropriate methods here to transmit the "legacy action" to the xmpp
    user. This should look like this:

    .. code-block:python

        class Session(BaseSession):
            ...

            async def on_cool_chat_network_new_text_message(self, legacy_msg_event):
                contact = self.contacts.by_legacy_id(legacy_msg_event.from)
                contact.send_text(legacy_msg_event.text)

            async def on_cool_chat_network_new_typing_event(self, legacy_typing_event):
                contact = self.contacts.by_legacy_id(legacy_msg_event.from)
                contact.composing()
            ...

    Use ``carbon=True`` as a keyword arg for methods to represent an action FROM
    the user TO the contact, typically when the user uses an official client to
    do an action such as sending a message or marking as message as read.
    This will use :xep:`0363` to impersonate the XMPP user in order.
    """

    session: "BaseSession"

    RESOURCE: str = "slidge"
    """
    A full JID, including a resource part is required for chat states (and maybe other stuff)
    to work properly. This is the name of the resource the contacts will use.
    """
    PROPAGATE_PRESENCE_TO_GROUPS = True

    mtype: MessageTypes = "chat"
    _can_send_carbon = True
    is_group = False

    _ONLY_SEND_PRESENCE_CHANGES = True

    STRIP_SHORT_DELAY = True
    _NON_FRIEND_PRESENCES_FILTER = {"subscribe", "unsubscribed"}

    INVITATION_RECIPIENT = True

    stored: Contact
    model: Contact

    def __init__(self, session: "BaseSession", stored: Contact) -> None:
        self.session = session
        self.xmpp = session.xmpp
        self.stored = stored
        self._set_logger()
        super().__init__()

    @property
    def jid(self):  # type:ignore[override]
        jid = JID(self.stored.jid)
        jid.resource = self.RESOURCE
        return jid

    @property
    def legacy_id(self):
        return self.xmpp.LEGACY_CONTACT_ID_TYPE(self.stored.legacy_id)

    async def get_vcard(self, fetch: bool = True) -> VCard4 | None:
        if fetch and not self.stored.vcard_fetched:
            await self.fetch_vcard()
        if self.stored.vcard is None:
            return None

        return VCard4(xml=ET.fromstring(self.stored.vcard))

    @property
    def is_friend(self) -> bool:
        return self.stored.is_friend

    @is_friend.setter
    def is_friend(self, value: bool) -> None:
        if value == self.is_friend:
            return
        self.stored.is_friend = value
        self.commit()

    @property
    def added_to_roster(self) -> bool:
        return self.stored.added_to_roster

    @added_to_roster.setter
    def added_to_roster(self, value: bool) -> None:
        if value == self.added_to_roster:
            return
        self.stored.added_to_roster = value
        self.commit()

    @property
    def participants(self) -> Iterator["LegacyParticipant"]:
        with self.xmpp.store.session() as orm:
            self.stored = orm.merge(self.stored)
            participants = self.stored.participants
        for p in participants:
            with self.xmpp.store.session() as orm:
                orm.add(p)
                muc = self.session.bookmarks.from_store(p.room)
                yield muc.participant_from_store(p, contact=self)

    @property
    def user_jid(self):
        return self.session.user_jid

    @property  # type:ignore
    def DISCO_TYPE(self) -> ClientType:
        return self.client_type

    @DISCO_TYPE.setter
    def DISCO_TYPE(self, value: ClientType) -> None:
        self.client_type = value

    @property
    def client_type(self) -> ClientType:
        """
        The client type of this contact, cf https://xmpp.org/registrar/disco-categories.html#client

        Default is "pc".
        """
        return self.stored.client_type

    @client_type.setter
    def client_type(self, value: ClientType) -> None:
        if self.stored.client_type == value:
            return
        self.stored.client_type = value
        self.commit()

    def _set_logger(self) -> None:
        self.log = logging.getLogger(f"{self.user_jid.bare}:contact:{self}")

    def __repr__(self) -> str:
        return f"<Contact #{self.stored.id} '{self.name}' ({self.legacy_id} - {self.jid.user})'>"

    def __get_subscription_string(self) -> str:
        if self.is_friend:
            return "both"
        return "none"

    def __propagate_to_participants(self, stanza: Presence) -> None:
        if not self.PROPAGATE_PRESENCE_TO_GROUPS:
            return

        ptype = stanza["type"]
        if ptype in ("available", "chat"):
            func_name = "online"
        elif ptype in ("xa", "unavailable"):
            # we map unavailable to extended_away, because offline is
            # "participant leaves the MUC"
            # TODO: improve this with a clear distinction between participant
            #       and member list
            func_name = "extended_away"
        elif ptype == "busy":
            func_name = "busy"
        elif ptype == "away":
            func_name = "away"
        else:
            return

        last_seen: Optional[datetime.datetime] = (
            stanza["idle"]["since"] if stanza.get_plugin("idle", check=True) else None
        )

        kw = dict(status=stanza["status"], last_seen=last_seen)

        for part in self.participants:
            func = getattr(part, func_name)
            func(**kw)

    def _send(
        self,
        stanza: MessageOrPresenceTypeVar,
        carbon: bool = False,
        nick: bool = False,
        **send_kwargs,
    ) -> MessageOrPresenceTypeVar:
        if carbon and isinstance(stanza, Message):
            stanza["to"] = self.jid.bare
            stanza["from"] = self.user_jid
            self._privileged_send(stanza)
            return stanza  # type:ignore

        if isinstance(stanza, Presence):
            if not self._updating_info:
                self.__propagate_to_participants(stanza)
            if (
                not self.is_friend
                and stanza["type"] not in self._NON_FRIEND_PRESENCES_FILTER
            ):
                return stanza  # type:ignore
        if self.name and (nick or not self.is_friend):
            n = self.xmpp.plugin["xep_0172"].stanza.UserNick()
            n["nick"] = self.name
            stanza.append(n)
        if (
            not self._updating_info
            and self.xmpp.MARK_ALL_MESSAGES
            and is_markable(stanza)
        ):
            try:
                with self.xmpp.store.session(expire_on_commit=False) as orm:
                    self.stored = orm.merge(self.stored)
                    new = ContactSent(contact=self.stored, msg_id=stanza["id"])
                    orm.add(new)
                    self.stored.sent_order.append(new)
                    orm.commit()
            except IntegrityError:
                self.log.warning("Contact  has already sent message %s", stanza["id"])
        stanza["to"] = self.user_jid
        stanza.send()
        return stanza

    def get_msg_xmpp_id_up_to(self, horizon_xmpp_id: str) -> list[str]:
        """
        Return XMPP msg ids sent by this contact up to a given XMPP msg id.

        Plugins have no reason to use this, but it is used by slidge core
        for legacy networks that need to mark all messages as read (most XMPP
        clients only send a read marker for the latest message).

        This has side effects, if the horizon XMPP id is found, messages up to
        this horizon are not cleared, to avoid sending the same read mark twice.

        :param horizon_xmpp_id: The latest message
        :return: A list of XMPP ids or None if horizon_xmpp_id was not found
        """
        with self.xmpp.store.session() as orm:
            assert self.stored.id is not None
            ids = self.xmpp.store.contacts.pop_sent_up_to(
                orm, self.stored.id, horizon_xmpp_id
            )
            orm.commit()
            return ids

    @property
    def name(self) -> str:
        """
        Friendly name of the contact, as it should appear in the user's roster
        """
        return self.stored.nick or ""

    @name.setter
    def name(self, n: Optional[str]) -> None:
        if self.stored.nick == n:
            return
        self.stored.nick = n
        self._set_logger()
        if self.is_friend and self.added_to_roster:
            self.xmpp.pubsub.broadcast_nick(
                user_jid=self.user_jid, jid=self.jid.bare, nick=n
            )
        self.commit()
        for p in self.participants:
            p.nickname = n or str(self.legacy_id)

    def _post_avatar_update(self, cached_avatar) -> None:
        if self.is_friend and self.added_to_roster:
            self.session.create_task(
                self.session.xmpp.pubsub.broadcast_avatar(
                    self.jid.bare, self.session.user_jid, cached_avatar
                )
            )
        for p in self.participants:
            self.log.debug("Propagating new avatar to %s", p.muc)
            p.send_last_presence(force=True, no_cache_online=True)

    def set_vcard(
        self,
        /,
        full_name: Optional[str] = None,
        given: Optional[str] = None,
        surname: Optional[str] = None,
        birthday: Optional[date] = None,
        phone: Optional[str] = None,
        phones: Iterable[str] = (),
        note: Optional[str] = None,
        url: Optional[str] = None,
        email: Optional[str] = None,
        country: Optional[str] = None,
        locality: Optional[str] = None,
    ) -> None:
        vcard = VCard4()
        vcard.add_impp(f"xmpp:{self.jid.bare}")

        if n := self.name:
            vcard.add_nickname(n)
        if full_name:
            vcard["full_name"] = full_name
        elif n:
            vcard["full_name"] = n

        if given:
            vcard["given"] = given
        if surname:
            vcard["surname"] = surname
        if birthday:
            vcard["birthday"] = birthday

        if note:
            vcard.add_note(note)
        if url:
            vcard.add_url(url)
        if email:
            vcard.add_email(email)
        if phone:
            vcard.add_tel(phone)
        for p in phones:
            vcard.add_tel(p)
        if country and locality:
            vcard.add_address(country, locality)
        elif country:
            vcard.add_address(country, locality)

        self.stored.vcard = str(vcard)
        self.stored.vcard_fetched = True
        self.session.create_task(
            self.xmpp.pubsub.broadcast_vcard_event(self.jid, self.user_jid, vcard)
        )

        self.commit()

    def get_roster_item(self):
        item = {
            "subscription": self.__get_subscription_string(),
            "groups": [self.xmpp.ROSTER_GROUP],
        }
        if (n := self.name) is not None:
            item["name"] = n
        return {self.jid.bare: item}

    async def add_to_roster(self, force: bool = False) -> None:
        """
        Add this contact to the user roster using :xep:`0356`

        :param force: add even if the contact was already added successfully
        """
        if self.added_to_roster and not force:
            return
        if not self.session.user.preferences.get("roster_push", True):
            log.debug("Roster push request by plugin ignored (--no-roster-push)")
            return
        try:
            await self.xmpp["xep_0356"].set_roster(
                jid=self.user_jid, roster_items=self.get_roster_item()
            )
        except PermissionError:
            from slidge import __version__

            warnings.warn(
                "Slidge does not have the privilege to manage rosters. See "
                f"https://slidge.im/docs/slidge/{__version__}/admin/privilege.html"
            )
            self.send_friend_request(
                f"I'm already your friend on {self.xmpp.COMPONENT_TYPE}, but "
                "slidge is not allowed to manage your roster."
            )
            return
        except (IqError, IqTimeout) as e:
            self.log.warning("Could not add to roster", exc_info=e)
        else:
            # we only broadcast pubsub events for contacts added to the roster
            # so if something was set before, we need to push it now
            self.added_to_roster = True
            self.send_last_presence()

    async def __broadcast_pubsub_items(self) -> None:
        if not self.is_friend:
            return
        if not self.added_to_roster:
            return
        cached_avatar = self.get_cached_avatar()
        if cached_avatar is not None:
            await self.xmpp.pubsub.broadcast_avatar(
                self.jid.bare, self.session.user_jid, cached_avatar
            )
        nick = self.name

        if nick is not None:
            self.xmpp.pubsub.broadcast_nick(
                self.session.user_jid,
                self.jid.bare,
                nick,
            )

    def send_friend_request(self, text: Optional[str] = None) -> None:
        presence = self._make_presence(ptype="subscribe", pstatus=text, bare=True)
        self._send(presence, nick=True)

    async def accept_friend_request(self, text: Optional[str] = None) -> None:
        """
        Call this to signify that this Contact has accepted to be a friend
        of the user.

        :param text: Optional message from the friend to the user
        """
        self.is_friend = True
        self.added_to_roster = True
        self.log.debug("Accepting friend request")
        presence = self._make_presence(ptype="subscribed", pstatus=text, bare=True)
        self._send(presence, nick=True)
        self.send_last_presence()
        await self.__broadcast_pubsub_items()
        self.log.debug("Accepted friend request")

    def reject_friend_request(self, text: Optional[str] = None) -> None:
        """
        Call this to signify that this Contact has refused to be a contact
        of the user (or that they don't want to be friends anymore)

        :param text: Optional message from the non-friend to the user
        """
        presence = self._make_presence(ptype="unsubscribed", pstatus=text, bare=True)
        self.offline()
        self._send(presence, nick=True)
        self.is_friend = False

    async def on_friend_request(self, text: str = "") -> None:
        """
        Called when receiving a "subscribe" presence, ie, "I would like to add
        you to my contacts/friends", from the user to this contact.

        In XMPP terms: "I would like to receive your presence updates"

        This is only called if self.is_friend = False. If self.is_friend = True,
        slidge will automatically "accept the friend request", ie, reply with
        a "subscribed" presence.

        When called, a 'friend request event' should be sent to the legacy
        service, and when the contact responds, you should either call
        self.accept_subscription() or self.reject_subscription()
        """
        pass

    async def on_friend_delete(self, text: str = "") -> None:
        """
        Called when receiving an "unsubscribed" presence, ie, "I would like to
        remove you to my contacts/friends" or "I refuse your friend request"
        from the user to this contact.

        In XMPP terms: "You won't receive my presence updates anymore (or you
        never have)".
        """
        pass

    async def on_friend_accept(self) -> None:
        """
        Called when receiving a "subscribed"  presence, ie, "I accept to be
        your/confirm that you are my friend" from the user to this contact.

        In XMPP terms: "You will receive my presence updates".
        """
        pass

    def unsubscribe(self) -> None:
        """
        (internal use by slidge)

        Send an "unsubscribe", "unsubscribed", "unavailable" presence sequence
        from this contact to the user, ie, "this contact has removed you from
        their 'friends'".
        """
        for ptype in "unsubscribe", "unsubscribed", "unavailable":
            self.xmpp.send_presence(pfrom=self.jid, pto=self.user_jid.bare, ptype=ptype)

    async def update_info(self) -> None:
        """
        Fetch information about this contact from the legacy network

        This is awaited on Contact instantiation, and should be overridden to
        update the nickname, avatar, vcard [...] of this contact, by making
        "legacy API calls".

        To take advantage of the slidge avatar cache, you can check the .avatar
        property to retrieve the "legacy file ID" of the cached avatar. If there
        is no change, you should not call
        :py:meth:`slidge.core.mixins.avatar.AvatarMixin.set_avatar` or attempt
        to modify the ``.avatar`` property.
        """
        pass

    async def fetch_vcard(self) -> None:
        """
        It the legacy network doesn't like that you fetch too many profiles on startup,
        it's also possible to fetch it here, which will be called when XMPP clients
        of the user request the vcard, if it hasn't been fetched before
        :return:
        """
        pass

    def _make_presence(
        self,
        *,
        last_seen: Optional[datetime.datetime] = None,
        status_codes: Optional[set[int]] = None,
        user_full_jid: Optional[JID] = None,
        **presence_kwargs,
    ):
        p = super()._make_presence(last_seen=last_seen, **presence_kwargs)
        caps = self.xmpp.plugin["xep_0115"]
        if p.get_from().resource and self.stored.caps_ver:
            p["caps"]["node"] = caps.caps_node
            p["caps"]["hash"] = caps.hash
            p["caps"]["ver"] = self.stored.caps_ver
        return p


def is_markable(stanza: Union[Message, Presence]):
    if isinstance(stanza, Presence):
        return False
    return bool(stanza["body"])


log = logging.getLogger(__name__)
