import logging
from copy import copy
from xml.etree import ElementTree

from slixmpp import JID, Message
from slixmpp.exceptions import XMPPError

from ....contact.contact import LegacyContact
from ....group.participant import LegacyParticipant
from ....group.room import LegacyMUC
from ....util.types import LinkPreview, Recipient
from ....util.util import dict_to_named_tuple, remove_emoji_variation_selector_16
from ... import config
from ...session import BaseSession
from ..util import DispatcherMixin, exceptions_to_xmpp_errors


class MessageContentMixin(DispatcherMixin):
    __slots__: list[str] = []

    def __init__(self, xmpp) -> None:
        super().__init__(xmpp)
        xmpp.add_event_handler("legacy_message", self.on_legacy_message)
        xmpp.add_event_handler("message_correction", self.on_message_correction)
        xmpp.add_event_handler("message_retract", self.on_message_retract)
        xmpp.add_event_handler("groupchat_message", self.on_groupchat_message)
        xmpp.add_event_handler("reactions", self.on_reactions)

    async def on_groupchat_message(self, msg: Message) -> None:
        await self.on_legacy_message(msg)

    @exceptions_to_xmpp_errors
    async def on_legacy_message(self, msg: Message) -> None:
        """
        Meant to be called from :class:`BaseGateway` only.

        :param msg:
        :return:
        """
        # we MUST not use `if m["replace"]["id"]` because it adds the tag if not
        # present. this is a problem for MUC echoed messages
        if msg.get_plugin("replace", check=True) is not None:
            # ignore last message correction (handled by a specific method)
            return
        if msg.get_plugin("apply_to", check=True) is not None:
            # ignore message retraction (handled by a specific method)
            return
        if msg.get_plugin("reactions", check=True) is not None:
            # ignore message reaction fallback.
            # the reaction itself is handled by self.react_from_msg().
            return
        if msg.get_plugin("retract", check=True) is not None:
            # ignore message retraction fallback.
            # the retraction itself is handled by self.on_retract
            return
        cid = None
        if msg.get_plugin("html", check=True) is not None:
            body = ElementTree.fromstring("<body>" + msg["html"].get_body() + "</body>")
            p = body.findall("p")
            if p is not None and len(p) == 1:
                if p[0].text is None or not p[0].text.strip():
                    images = p[0].findall("img")
                    if len(images) == 1:
                        # no text, single img ⇒ this is a sticker
                        # other cases should be interpreted as "custom emojis" in text
                        src = images[0].get("src")
                        if src is not None and src.startswith("cid:"):
                            cid = src.removeprefix("cid:")

        session, recipient, thread = await self._get_session_recipient_thread(msg)

        if msg.get_plugin("oob", check=True) is not None:
            url = msg["oob"]["url"]
        elif (
            "reference" in msg
            and "sims" in msg["reference"]
            and "sources" in msg["reference"]["sims"]
        ):
            for source in msg["reference"]["sims"]["sources"]["substanzas"]:
                if source["uri"].startswith("http"):
                    url = source["uri"]
                    break
            else:
                url = None
        else:
            url = None

        if msg.get_plugin("reply", check=True):
            text, reply_to_msg_id, reply_to, reply_fallback = await self.__get_reply(
                msg, session, recipient
            )
        else:
            text = msg["body"]
            reply_to_msg_id = None
            reply_to = None
            reply_fallback = None

        if msg.get_plugin("link_previews", check=True):
            link_previews = [
                dict_to_named_tuple(p, LinkPreview) for p in msg["link_previews"]
            ]
        else:
            link_previews = []

        if url:
            legacy_msg_id = await self.__send_url(
                url,
                session,
                recipient,
                reply_to_msg_id=reply_to_msg_id,
                reply_to_fallback_text=reply_fallback,
                reply_to=reply_to,
                thread=thread,
            )
        elif cid:
            legacy_msg_id = await self.__send_bob(
                msg.get_from(),
                cid,
                session,
                recipient,
                reply_to_msg_id=reply_to_msg_id,
                reply_to_fallback_text=reply_fallback,
                reply_to=reply_to,
                thread=thread,
            )
        elif text:
            if isinstance(recipient, LegacyMUC):
                mentions = {"mentions": await recipient.parse_mentions(text)}
            else:
                mentions = {}
            legacy_msg_id = await session.on_text(
                recipient,
                text,
                reply_to_msg_id=reply_to_msg_id,
                reply_to_fallback_text=reply_fallback,
                reply_to=reply_to,
                thread=thread,
                link_previews=link_previews,
                **mentions,
            )
        else:
            log.debug("Ignoring %s", msg.get_id())
            return

        if isinstance(recipient, LegacyMUC):
            await recipient.echo(msg, legacy_msg_id)
        else:
            self.__ack(msg)

        if legacy_msg_id is None:
            return

        with self.xmpp.store.session() as orm:
            self.xmpp.store.id_map.set_msg(
                orm,
                recipient.stored.id,
                str(legacy_msg_id),
                [msg.get_id()],
                recipient.is_group,
            )
            if session.MESSAGE_IDS_ARE_THREAD_IDS and (t := msg["thread"]):
                self.xmpp.store.id_map.set_thread(
                    orm, recipient.stored.id, t, str(legacy_msg_id), recipient.is_group
                )
            orm.commit()

    @exceptions_to_xmpp_errors
    async def on_message_correction(self, msg: Message) -> None:
        if msg.get_plugin("retract", check=True) is not None:
            # ignore message retraction fallback (fallback=last msg correction)
            return
        session, recipient, thread = await self._get_session_recipient_thread(msg)
        xmpp_id = msg["replace"]["id"]
        if isinstance(recipient, LegacyMUC):
            with self.xmpp.store.session() as orm:
                legacy_id_str = self.xmpp.store.id_map.get_legacy(
                    orm, recipient.stored.id, xmpp_id, True
                )
            if legacy_id_str is None:
                legacy_id = self._xmpp_msg_id_to_legacy(session, xmpp_id, recipient)
            else:
                legacy_id = self.xmpp.LEGACY_MSG_ID_TYPE(legacy_id_str)
        else:
            legacy_id = self._xmpp_msg_id_to_legacy(session, xmpp_id, recipient)

        if isinstance(recipient, LegacyMUC):
            mentions = await recipient.parse_mentions(msg["body"])
        else:
            mentions = None

        if previews := msg["link_previews"]:
            link_previews = [dict_to_named_tuple(p, LinkPreview) for p in previews]
        else:
            link_previews = []

        if legacy_id is None:
            log.debug("Did not find legacy ID to correct")
            new_legacy_msg_id = await session.on_text(
                recipient,
                "Correction:" + msg["body"],
                thread=thread,
                mentions=mentions,
                link_previews=link_previews,
            )
        elif not msg["body"].strip() and recipient.RETRACTION:
            await session.on_retract(recipient, legacy_id, thread=thread)
            new_legacy_msg_id = None
        elif recipient.CORRECTION:
            new_legacy_msg_id = await session.on_correct(
                recipient,
                msg["body"],
                legacy_id,
                thread=thread,
                mentions=mentions,
                link_previews=link_previews,
            )
        else:
            session.send_gateway_message(
                "Last message correction is not supported by this legacy service. "
                "Slidge will send your correction as new message."
            )
            if recipient.RETRACTION and legacy_id is not None:
                if legacy_id is not None:
                    session.send_gateway_message(
                        "Slidge will attempt to retract the original message you wanted"
                        " to edit."
                    )
                    await session.on_retract(recipient, legacy_id, thread=thread)

            new_legacy_msg_id = await session.on_text(
                recipient,
                "Correction: " + msg["body"],
                thread=thread,
                mentions=mentions,
                link_previews=link_previews,
            )

        if isinstance(recipient, LegacyMUC):
            await recipient.echo(msg, new_legacy_msg_id)
        else:
            self.__ack(msg)
        if new_legacy_msg_id is None:
            return
        with self.xmpp.store.session() as orm:
            self.xmpp.store.id_map.set_msg(
                orm,
                recipient.stored.id,
                new_legacy_msg_id,
                msg.get_id(),
                recipient.is_group,
            )
            orm.commit()

    @exceptions_to_xmpp_errors
    async def on_message_retract(self, msg: Message):
        session, recipient, thread = await self._get_session_recipient_thread(msg)
        if not recipient.RETRACTION:
            raise XMPPError(
                "bad-request",
                "This legacy service does not support message retraction.",
            )
        xmpp_id: str = msg["retract"]["id"]
        legacy_id = self._xmpp_msg_id_to_legacy(session, xmpp_id, recipient)
        if legacy_id:
            await session.on_retract(recipient, legacy_id, thread=thread)
            if isinstance(recipient, LegacyMUC):
                await recipient.echo(msg, None)
        else:
            log.debug("Ignored retraction from user")
        self.__ack(msg)

    @exceptions_to_xmpp_errors
    async def on_reactions(self, msg: Message):
        session, recipient, thread = await self._get_session_recipient_thread(msg)
        react_to: str = msg["reactions"]["id"]

        special_msg = session.SPECIAL_MSG_ID_PREFIX and react_to.startswith(
            session.SPECIAL_MSG_ID_PREFIX
        )

        if special_msg:
            legacy_id = react_to
        else:
            legacy_id = self._xmpp_msg_id_to_legacy(session, react_to, recipient)

        if not legacy_id:
            log.debug("Ignored reaction from user")
            raise XMPPError(
                "internal-server-error",
                "Could not convert the XMPP msg ID to a legacy ID",
            )

        emojis = [
            remove_emoji_variation_selector_16(r["value"]) for r in msg["reactions"]
        ]
        error_msg = None
        recipient = recipient

        if not special_msg:
            if recipient.REACTIONS_SINGLE_EMOJI and len(emojis) > 1:
                error_msg = "Maximum 1 emoji/message"

            if not error_msg and (
                subset := await recipient.available_emojis(legacy_id)
            ):
                if not set(emojis).issubset(subset):
                    error_msg = f"You can only react with the following emojis: {''.join(subset)}"

        if error_msg:
            session.send_gateway_message(error_msg)
            if not isinstance(recipient, LegacyMUC):
                # no need to carbon for groups, we just don't echo the stanza
                recipient.react(legacy_id, carbon=True)
            await session.on_react(recipient, legacy_id, [], thread=thread)
            raise XMPPError(
                "policy-violation",
                text=error_msg,
            )

        await session.on_react(recipient, legacy_id, emojis, thread=thread)
        if isinstance(recipient, LegacyMUC):
            await recipient.echo(msg, None)
        else:
            self.__ack(msg)

        with self.xmpp.store.session() as orm:
            multi = self.xmpp.store.id_map.get_xmpp(
                orm, recipient.stored.id, legacy_id, recipient.is_group
            )
        if not multi:
            return
        multi = [m for m in multi if react_to != m]

        if isinstance(recipient, LegacyMUC):
            for xmpp_id in multi:
                mc = copy(msg)
                mc["reactions"]["id"] = xmpp_id
                await recipient.echo(mc)
        elif isinstance(recipient, LegacyContact):
            for xmpp_id in multi:
                recipient.react(legacy_id, emojis, xmpp_id=xmpp_id, carbon=True)

    def __ack(self, msg: Message) -> None:
        if not self.xmpp.PROPER_RECEIPTS:
            self.xmpp.delivery_receipt.ack(msg)

    async def __get_reply(
        self, msg: Message, session: BaseSession, recipient: Recipient
    ) -> tuple[
        str, str | int | None, LegacyContact | LegacyParticipant | None, str | None
    ]:
        try:
            reply_to_msg_id = self._xmpp_msg_id_to_legacy(
                session, msg["reply"]["id"], recipient
            )
        except XMPPError:
            session.log.debug(
                "Could not determine reply-to legacy msg ID, sending quote instead."
            )
            return msg["body"], None, None, None

        reply_to_jid = JID(msg["reply"]["to"])
        reply_to = None
        if msg["type"] == "chat":
            if reply_to_jid.bare != session.user_jid.bare:
                try:
                    reply_to = await session.contacts.by_jid(reply_to_jid)
                except XMPPError:
                    pass
        elif msg["type"] == "groupchat":
            nick = reply_to_jid.resource
            try:
                muc = await session.bookmarks.by_jid(reply_to_jid)
            except XMPPError:
                pass
            else:
                if nick != muc.user_nick:
                    reply_to = await muc.get_participant(
                        reply_to_jid.resource, store=False
                    )

        if msg.get_plugin("fallback", check=True) and (
            isinstance(recipient, LegacyMUC) or recipient.REPLIES
        ):
            text = msg["fallback"].get_stripped_body(self.xmpp["xep_0461"].namespace)
            try:
                reply_fallback = msg["reply"].get_fallback_body()
            except AttributeError:
                reply_fallback = None
        else:
            text = msg["body"]
            reply_fallback = None

        return text, reply_to_msg_id, reply_to, reply_fallback

    async def __send_url(
        self, url: str, session: BaseSession, recipient: Recipient, **kwargs
    ) -> int | str | None:
        async with self.xmpp.http.get(url) as response:
            if response.status >= 400:
                session.log.warning(
                    "OOB url cannot be downloaded: %s, sending the URL as text"
                    " instead.",
                    response,
                )
                return await session.on_text(recipient, url, **kwargs)

            return await session.on_file(
                recipient, url, http_response=response, **kwargs
            )

    async def __send_bob(
        self, from_: JID, cid: str, session: BaseSession, recipient: Recipient, **kwargs
    ) -> int | str | None:
        with self.xmpp.store.session() as orm:
            sticker = self.xmpp.store.bob.get_sticker(orm, cid)
        if sticker is None:
            await self.xmpp.plugin["xep_0231"].get_bob(from_, cid)
            with self.xmpp.store.session() as orm:
                sticker = self.xmpp.store.bob.get_sticker(orm, cid)
        assert sticker is not None
        return await session.on_sticker(recipient, sticker, **kwargs)


log = logging.getLogger(__name__)
