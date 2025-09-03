import logging
from typing import TYPE_CHECKING, Any, Optional

import sqlalchemy as sa
from slixmpp.exceptions import XMPPError
from slixmpp.plugins.xep_0030.stanza.items import DiscoItems
from slixmpp.types import OptJid

from ...db.models import Room
from .util import DispatcherMixin

if TYPE_CHECKING:
    from slidge.core.gateway import BaseGateway


class DiscoMixin(DispatcherMixin):
    __slots__: list[str] = []

    def __init__(self, xmpp: "BaseGateway") -> None:
        super().__init__(xmpp)

        xmpp.plugin["xep_0030"].set_node_handler(
            "get_info",
            jid=None,
            node=None,
            handler=self.get_info,
        )

        xmpp.plugin["xep_0030"].set_node_handler(
            "get_items",
            jid=None,
            node=None,
            handler=self.get_items,
        )

    async def get_info(
        self, jid: OptJid, node: Optional[str], ifrom: OptJid, data: Any
    ):
        if ifrom == self.xmpp.boundjid.bare or jid in (self.xmpp.boundjid.bare, None):
            return self.xmpp.plugin["xep_0030"].static.get_info(jid, node, ifrom, data)

        if ifrom is None:
            raise XMPPError("subscription-required")

        assert jid is not None
        session = await self._get_session_from_jid(jid=ifrom)

        log.debug("Looking for entity: %s", jid)

        entity = await session.get_contact_or_group_or_participant(jid)

        if entity is None:
            raise XMPPError("item-not-found")

        return await entity.get_disco_info(jid, node)

    async def get_items(
        self, jid: OptJid, node: Optional[str], ifrom: OptJid, data: Any
    ):
        if ifrom is None:
            raise XMPPError("bad-request")

        if jid != self.xmpp.boundjid.bare:
            return DiscoItems()

        assert ifrom is not None
        session = await self._get_session_from_jid(ifrom)

        d = DiscoItems()
        with self.xmpp.store.session() as orm:
            for room in orm.execute(
                sa.select(Room)
                .options(sa.orm.load_only(Room.jid, Room.name))
                .filter_by(user=session.user)
                .order_by(Room.name)
            ).scalars():
                d.add_item(room.jid, name=room.name)

        return d


log = logging.getLogger(__name__)
