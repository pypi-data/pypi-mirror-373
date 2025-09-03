import abc
import logging
from typing import TYPE_CHECKING, Generic, Iterator, Optional, Type

from slixmpp import JID
from slixmpp.exceptions import XMPPError

from ..db.models import Room
from ..util import SubclassableOnce
from ..util.jid_escaping import ESCAPE_TABLE, unescape_node
from ..util.lock import NamedLockMixin
from ..util.types import LegacyGroupIdType, LegacyMUCType
from .room import LegacyMUC

if TYPE_CHECKING:
    from slidge.core.session import BaseSession


class LegacyBookmarks(
    Generic[LegacyGroupIdType, LegacyMUCType],
    NamedLockMixin,
    metaclass=SubclassableOnce,
):
    """
    This is instantiated once per :class:`~slidge.BaseSession`
    """

    _muc_cls: Type[LegacyMUCType]

    def __init__(self, session: "BaseSession") -> None:
        self.session = session
        self.xmpp = session.xmpp
        self.user_jid = session.user_jid

        self._user_nick: str = self.session.user_jid.node

        super().__init__()
        self.log = logging.getLogger(f"{self.user_jid.bare}:bookmarks")
        self.ready = self.session.xmpp.loop.create_future()
        if not self.xmpp.GROUPS:
            self.ready.set_result(True)

    @property
    def user_nick(self):
        return self._user_nick

    @user_nick.setter
    def user_nick(self, nick: str) -> None:
        self._user_nick = nick

    def from_store(self, stored: Room) -> LegacyMUCType:
        return self._muc_cls(self.session, stored)

    def __iter__(self) -> Iterator[LegacyMUC]:
        with self.xmpp.store.session() as orm:
            for stored in orm.query(Room).filter_by(user=self.session.user).all():
                if stored.updated:
                    yield self.from_store(stored)

    def __repr__(self) -> str:
        return f"<Bookmarks of {self.user_jid}>"

    async def legacy_id_to_jid_local_part(self, legacy_id: LegacyGroupIdType) -> str:
        return await self.legacy_id_to_jid_username(legacy_id)

    async def jid_local_part_to_legacy_id(self, local_part: str) -> LegacyGroupIdType:
        return await self.jid_username_to_legacy_id(local_part)

    async def legacy_id_to_jid_username(self, legacy_id: LegacyGroupIdType) -> str:
        """
        The default implementation calls ``str()`` on the legacy_id and
        escape characters according to :xep:`0106`.

        You can override this class and implement a more subtle logic to raise
        an :class:`~slixmpp.exceptions.XMPPError` early

        :param legacy_id:
        :return:
        """
        return str(legacy_id).translate(ESCAPE_TABLE)

    async def jid_username_to_legacy_id(self, username: str):
        """

        :param username:
        :return:
        """
        return unescape_node(username)

    async def by_jid(self, jid: JID) -> LegacyMUCType:
        if jid.resource:
            jid = JID(jid.bare)
        async with self.lock(("bare", jid.bare)):
            legacy_id = await self.jid_local_part_to_legacy_id(jid.node)
            if self.get_lock(("legacy_id", legacy_id)):
                self.session.log.debug("Already updating %s via by_legacy_id()", jid)
                return await self.by_legacy_id(legacy_id)

            with self.session.xmpp.store.session() as orm:
                stored = (
                    orm.query(Room)
                    .filter_by(user_account_id=self.session.user_pk, jid=jid)
                    .one_or_none()
                )
            if stored is None:
                stored = Room(
                    user_account_id=self.session.user_pk,
                    jid=jid,
                    legacy_id=legacy_id,
                )
            return await self.__update_if_needed(stored)

    def by_jid_only_if_exists(self, jid: JID) -> Optional[LegacyMUCType]:
        with self.xmpp.store.session() as orm:
            stored = (
                orm.query(Room).filter_by(user=self.session.user, jid=jid).one_or_none()
            )
            if stored is not None and stored.updated:
                return self.from_store(stored)
        return None

    async def by_legacy_id(self, legacy_id: LegacyGroupIdType) -> LegacyMUCType:
        async with self.lock(("legacy_id", legacy_id)):
            local = await self.legacy_id_to_jid_local_part(legacy_id)
            jid = JID(f"{local}@{self.xmpp.boundjid}")
            if self.get_lock(("bare", jid.bare)):
                self.session.log.debug("Already updating %s via by_jid()", jid)
                return await self.by_jid(jid)

            with self.xmpp.store.session() as orm:
                stored = (
                    orm.query(Room)
                    .filter_by(
                        user_account_id=self.session.user_pk,
                        legacy_id=str(legacy_id),
                    )
                    .one_or_none()
                )
            if stored is None:
                stored = Room(
                    user_account_id=self.session.user_pk,
                    jid=jid,
                    legacy_id=legacy_id,
                )
            return await self.__update_if_needed(stored)

    async def __update_if_needed(self, stored: Room) -> LegacyMUCType:
        muc = self.from_store(stored)
        if muc.stored.updated:
            return muc

        with muc.updating_info():
            try:
                await muc.update_info()
            except NotImplementedError:
                pass
            except XMPPError:
                raise
            except Exception as e:
                raise XMPPError("internal-server-error", str(e))

        return muc

    @abc.abstractmethod
    async def fill(self):
        """
        Establish a user's known groups.

        This has to be overridden in plugins with group support and at the
        minimum, this should ``await self.by_legacy_id(group_id)`` for all
        the groups a user is part of.

        Slidge internals will call this on successful :meth:`BaseSession.login`

        """
        if self.xmpp.GROUPS:
            raise NotImplementedError(
                "The plugin advertised support for groups but"
                " LegacyBookmarks.fill() was not overridden."
            )

    async def remove(
        self,
        muc: LegacyMUC,
        reason: str = "You left this group from the official client.",
        kick: bool = True,
    ) -> None:
        """
        Delete everything about a specific group.

        This should be called when the user leaves the group from the official
        app.

        :param muc: The MUC to remove.
        :param reason: Optionally, a reason why this group was removed.
        :param kick: Whether the user should be kicked from this group. Set this
            to False in case you do this somewhere else in your code, eg, on
            receiving the confirmation that the group was deleted.
        """
        if kick:
            user_participant = await muc.get_user_participant()
            user_participant.kick(reason)
        with self.xmpp.store.session() as orm:
            orm.delete(muc.stored)
            orm.commit()
