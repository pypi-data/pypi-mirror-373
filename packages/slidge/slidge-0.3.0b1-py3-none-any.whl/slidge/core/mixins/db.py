import logging
import typing
from contextlib import contextmanager

from ...db.models import Base, Contact, Participant, Room

if typing.TYPE_CHECKING:
    from slidge import BaseGateway


class DBMixin:
    stored: Base
    xmpp: "BaseGateway"
    log: logging.Logger

    def merge(self) -> None:
        with self.xmpp.store.session() as orm:
            self.stored = orm.merge(self.stored)

    def commit(self, merge: bool = False) -> None:
        with self.xmpp.store.session(expire_on_commit=False) as orm:
            if merge:
                self.log.debug("Merging %s", self.stored)
                self.stored = orm.merge(self.stored)
                self.log.debug("Merged %s", self.stored)
            orm.add(self.stored)
            self.log.debug("Committing to DB")
            orm.commit()


class UpdateInfoMixin(DBMixin):
    """
    This mixin just adds a context manager that prevents commiting to the DB
    on every attribute change.
    """

    stored: Contact | Room
    xmpp: "BaseGateway"
    log: logging.Logger

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._updating_info = False
        if self.stored.extra_attributes is not None:
            self.deserialize_extra_attributes(self.stored.extra_attributes)

    def serialize_extra_attributes(self) -> dict | None:
        return None

    def deserialize_extra_attributes(self, data: dict) -> None:
        pass

    @contextmanager
    def updating_info(self):
        self._updating_info = True
        yield
        self._updating_info = False
        self.stored.updated = True
        self.commit()

    def commit(self, merge: bool = False) -> None:
        if self._updating_info:
            self.log.debug("Not updating %s right now", self.stored)
        else:
            self.stored.extra_attributes = self.serialize_extra_attributes()
            super().commit(merge=merge)
