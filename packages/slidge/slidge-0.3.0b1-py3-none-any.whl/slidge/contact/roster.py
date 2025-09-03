import asyncio
import logging
import warnings
from typing import TYPE_CHECKING, AsyncIterator, Generic, Iterator, Optional, Type

from slixmpp import JID
from slixmpp.exceptions import IqError, IqTimeout
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session as OrmSession

from ..db.models import Contact, GatewayUser
from ..util import SubclassableOnce
from ..util.jid_escaping import ESCAPE_TABLE, unescape_node
from ..util.lock import NamedLockMixin
from ..util.types import LegacyContactType, LegacyUserIdType
from ..util.util import timeit
from .contact import LegacyContact

if TYPE_CHECKING:
    from ..core.session import BaseSession


class ContactIsUser(Exception):
    pass


class LegacyRoster(
    Generic[LegacyUserIdType, LegacyContactType],
    NamedLockMixin,
    metaclass=SubclassableOnce,
):
    """
    Virtual roster of a gateway user that allows to represent all
    of their contacts as singleton instances (if used properly and not too bugged).

    Every :class:`.BaseSession` instance will have its own :class:`.LegacyRoster` instance
    accessible via the :attr:`.BaseSession.contacts` attribute.

    Typically, you will mostly use the :meth:`.LegacyRoster.by_legacy_id` function to
    retrieve a contact instance.

    You might need to override :meth:`.LegacyRoster.legacy_id_to_jid_username` and/or
    :meth:`.LegacyRoster.jid_username_to_legacy_id` to incorporate some custom logic
    if you need some characters when translation JID user parts and legacy IDs.
    """

    _contact_cls: Type[LegacyContactType]

    def __init__(self, session: "BaseSession") -> None:
        super().__init__()

        self.log = logging.getLogger(f"{session.user_jid.bare}:roster")
        self.user_legacy_id: Optional[LegacyUserIdType] = None
        self.ready: asyncio.Future[bool] = session.xmpp.loop.create_future()

        self.session = session
        self.__filling = False

    @property
    def user(self) -> GatewayUser:
        return self.session.user

    def orm(self) -> Session:
        return self.session.xmpp.store.session()

    def from_store(self, stored: Contact) -> LegacyContactType:
        return self._contact_cls(self.session, stored=stored)

    def __repr__(self) -> str:
        return f"<Roster of {self.session.user_jid}>"

    def __iter__(self) -> Iterator[LegacyContactType]:
        with self.orm() as orm:
            for stored in orm.query(Contact).filter_by(user=self.user).all():
                if stored.updated:
                    yield self.from_store(stored)

    def known_contacts(self, only_friends: bool = True) -> dict[str, LegacyContactType]:
        if only_friends:
            return {c.jid.bare: c for c in self if c.is_friend}
        return {c.jid.bare: c for c in self}

    async def by_jid(self, contact_jid: JID) -> LegacyContactType:
        # """
        # Retrieve a contact by their JID
        #
        # If the contact was not instantiated before, it will be created
        # using :meth:`slidge.LegacyRoster.jid_username_to_legacy_id` to infer their
        # legacy user ID.
        #
        # :param contact_jid:
        # :return:
        # """
        username = contact_jid.node
        contact_jid = JID(contact_jid.bare)
        async with self.lock(("username", username)):
            legacy_id = await self.jid_username_to_legacy_id(username)
            if self.get_lock(("legacy_id", legacy_id)):
                self.log.debug("Already updating %s via by_legacy_id()", contact_jid)
                return await self.by_legacy_id(legacy_id)

            with self.orm() as orm:
                stored = (
                    orm.query(Contact)
                    .filter_by(user=self.user, jid=contact_jid)
                    .one_or_none()
                )
            if stored is None:
                stored = Contact(
                    user_account_id=self.session.user_pk,
                    legacy_id=legacy_id,
                    jid=contact_jid,
                )
            return await self.__update_if_needed(stored)

    async def __update_if_needed(self, stored: Contact) -> LegacyContactType:
        contact = self.from_store(stored)
        if contact.stored.updated:
            return contact

        with contact.updating_info():
            await contact.update_info()

        if contact.cached_presence is not None:
            contact._store_last_presence(contact.cached_presence)
        return contact

    def by_jid_only_if_exists(self, contact_jid: JID) -> LegacyContactType | None:
        with self.orm() as orm:
            stored = (
                orm.query(Contact)
                .filter_by(user=self.user, jid=contact_jid)
                .one_or_none()
            )
            if stored is not None and stored.updated:
                return self.from_store(stored)
        return None

    @timeit
    async def by_legacy_id(self, legacy_id: LegacyUserIdType) -> LegacyContactType:
        """
        Retrieve a contact by their legacy_id

        If the contact was not instantiated before, it will be created
        using :meth:`slidge.LegacyRoster.legacy_id_to_jid_username` to infer their
        legacy user ID.

        :param legacy_id:
        :return:
        """
        if legacy_id == self.user_legacy_id:
            raise ContactIsUser
        async with self.lock(("legacy_id", legacy_id)):
            username = await self.legacy_id_to_jid_username(legacy_id)
            if self.get_lock(("username", username)):
                self.log.debug("Already updating %s via by_jid()", username)

                jid = JID()
                jid.node = username
                jid.domain = self.session.xmpp.boundjid.bare
                return await self.by_jid(jid)

            with self.orm() as orm:
                stored = (
                    orm.query(Contact)
                    .filter_by(user=self.user, legacy_id=str(legacy_id))
                    .one_or_none()
                )
            if stored is None:
                stored = Contact(
                    user_account_id=self.session.user_pk,
                    legacy_id=str(legacy_id),
                    jid=JID(f"{username}@{self.session.xmpp.boundjid.bare}"),
                )
            return await self.__update_if_needed(stored)

    async def legacy_id_to_jid_username(self, legacy_id: LegacyUserIdType) -> str:
        """
        Convert a legacy ID to a valid 'user' part of a JID

        Should be overridden for cases where the str conversion of
        the legacy_id is not enough, e.g., if it is case-sensitive or contains
        forbidden characters not covered by :xep:`0106`.

        :param legacy_id:
        """
        return str(legacy_id).translate(ESCAPE_TABLE)

    async def jid_username_to_legacy_id(self, jid_username: str) -> LegacyUserIdType:
        """
        Convert a JID user part to a legacy ID.

        Should be overridden in case legacy IDs are not strings, or more generally
        for any case where the username part of a JID (unescaped with to the mapping
        defined by :xep:`0106`) is not enough to identify a contact on the legacy network.

        Default implementation is an identity operation

        :param jid_username: User part of a JID, ie "user" in "user@example.com"
        :return: An identifier for the user on the legacy network.
        """
        return unescape_node(jid_username)  # type:ignore

    @timeit
    async def _fill(self, orm: OrmSession):
        try:
            if hasattr(self.session.xmpp, "TEST_MODE"):
                # dirty hack to avoid mocking xmpp server replies to this
                # during tests
                raise PermissionError
            iq = await self.session.xmpp["xep_0356"].get_roster(
                self.session.user_jid.bare
            )
            user_roster = iq["roster"]["items"]
        except (PermissionError, IqError, IqTimeout):
            user_roster = None

        self.__filling = True
        async for contact in self.fill():
            if user_roster is None:
                continue
            item = contact.get_roster_item()
            old = user_roster.get(contact.jid.bare)
            if old is not None and all(
                old[k] == item[contact.jid.bare].get(k)
                for k in ("subscription", "groups", "name")
            ):
                self.log.debug("No need to update roster")
                continue
            self.log.debug("Updating roster")
            try:
                await self.session.xmpp["xep_0356"].set_roster(
                    self.session.user_jid.bare,
                    item,
                )
            except (PermissionError, IqError, IqTimeout) as e:
                warnings.warn(f"Could not add to roster: {e}")
            else:
                contact.added_to_roster = True
        orm.commit()
        self.__filling = False

    async def fill(self) -> AsyncIterator[LegacyContact]:
        """
        Populate slidge's "virtual roster".

        This should yield contacts that are meant to be added to the user's
        roster, typically by using ``await self.by_legacy_id(contact_id)``.
        Setting the contact nicknames, avatar, etc. should be in
        :meth:`LegacyContact.update_info()`

        It's not mandatory to override this method, but it is recommended way
        to populate "friends" of the user. Calling
        ``await (await self.by_legacy_id(contact_id)).add_to_roster()``
        accomplishes the same thing, but doing it in here allows to batch
        DB queries and is better performance-wise.

        """
        return
        yield


log = logging.getLogger(__name__)
