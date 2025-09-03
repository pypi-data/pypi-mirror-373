from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone
from mimetypes import guess_extension
from typing import Collection, Iterator, Optional, Type

from slixmpp.exceptions import XMPPError
from slixmpp.plugins.xep_0231.stanza import BitsOfBinary
from sqlalchemy import Engine, delete, select, update
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session, attributes, sessionmaker

from ..core import config
from ..util.archive_msg import HistoryMessage
from ..util.types import MamMetadata, Sticker
from .meta import Base
from .models import (
    ArchivedMessage,
    ArchivedMessageSource,
    Bob,
    Contact,
    ContactSent,
    DirectMessages,
    DirectThreads,
    GatewayUser,
    GroupMessages,
    GroupThreads,
    Participant,
    Room,
)


class UpdatedMixin:
    model: Type[Base] = NotImplemented

    def __init__(self, session: Session) -> None:
        session.execute(update(self.model).values(updated=False))

    def get_by_pk(self, session: Session, pk: int) -> Type[Base]:
        stmt = select(self.model).where(self.model.id == pk)  # type:ignore
        return session.scalar(stmt)


class SlidgeStore:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self.session = sessionmaker(engine)

        self.users = UserStore(self.session)
        self.avatars = AvatarStore(self.session)
        self.id_map = IdMapStore()
        self.bob = BobStore()
        with self.session() as session:
            self.contacts = ContactStore(session)
            self.mam = MAMStore(session, self.session)
            self.rooms = RoomStore(session)
            self.participants = ParticipantStore(session)
            session.commit()


class UserStore:
    def __init__(self, session_maker) -> None:
        self.session = session_maker

    def update(self, user: GatewayUser) -> None:
        with self.session(expire_on_commit=False) as session:
            # https://github.com/sqlalchemy/sqlalchemy/discussions/6473
            try:
                attributes.flag_modified(user, "legacy_module_data")
                attributes.flag_modified(user, "preferences")
            except InvalidRequestError:
                pass
            session.add(user)
            session.commit()


class AvatarStore:
    def __init__(self, session_maker) -> None:
        self.session = session_maker


LegacyToXmppType = (
    Type[DirectMessages]
    | Type[DirectThreads]
    | Type[GroupMessages]
    | Type[GroupThreads]
)


class IdMapStore:
    @staticmethod
    def _set(
        session: Session,
        foreign_key: int,
        legacy_id: str,
        xmpp_ids: list[str],
        type_: LegacyToXmppType,
    ) -> None:
        kwargs = dict(foreign_key=foreign_key, legacy_id=legacy_id)
        ids = session.scalars(
            select(type_.id).filter(
                type_.foreign_key == foreign_key, type_.legacy_id == legacy_id
            )
        )
        if ids:
            log.debug("Resetting legacy ID %s", legacy_id)
        session.execute(delete(type_).where(type_.id.in_(ids)))
        for xmpp_id in xmpp_ids:
            msg = type_(xmpp_id=xmpp_id, **kwargs)
            session.add(msg)

    def set_thread(
        self,
        session: Session,
        foreign_key: int,
        legacy_id: str,
        xmpp_id: str,
        group: bool,
    ) -> None:
        self._set(
            session,
            foreign_key,
            legacy_id,
            [xmpp_id],
            GroupThreads if group else DirectThreads,
        )

    def set_msg(
        self,
        session: Session,
        foreign_key: int,
        legacy_id: str,
        xmpp_ids: list[str],
        group: bool,
    ) -> None:
        self._set(
            session,
            foreign_key,
            legacy_id,
            xmpp_ids,
            GroupMessages if group else DirectMessages,
        )

    @staticmethod
    def _get(
        session: Session, foreign_key: int, legacy_id: str, type_: LegacyToXmppType
    ) -> list[str]:
        return list(
            session.scalars(
                select(type_.xmpp_id).filter_by(
                    foreign_key=foreign_key, legacy_id=legacy_id
                )
            )
        )

    def get_xmpp(
        self, session: Session, foreign_key: int, legacy_id: str, group: bool
    ) -> list[str]:
        return self._get(
            session,
            foreign_key,
            legacy_id,
            GroupMessages if group else DirectMessages,
        )

    @staticmethod
    def _get_legacy(
        session: Session, foreign_key: int, xmpp_id: str, type_: LegacyToXmppType
    ) -> Optional[str]:
        return session.scalar(
            select(type_.legacy_id).filter_by(foreign_key=foreign_key, xmpp_id=xmpp_id)
        )

    def get_legacy(
        self, session: Session, foreign_key: int, xmpp_id: str, group: bool
    ) -> Optional[str]:
        return self._get_legacy(
            session,
            foreign_key,
            xmpp_id,
            GroupMessages if group else DirectMessages,
        )

    def get_thread(
        self, session: Session, foreign_key: int, xmpp_id: str, group: bool
    ) -> Optional[str]:
        return self._get_legacy(
            session,
            foreign_key,
            xmpp_id,
            GroupThreads if group else DirectThreads,
        )

    @staticmethod
    def was_sent_by_user(
        session: Session, foreign_key: int, legacy_id: str, group: bool
    ) -> bool:
        type_ = GroupMessages if group else DirectMessages
        return (
            session.scalar(
                select(type_.id).filter_by(foreign_key=foreign_key, legacy_id=legacy_id)
            )
            is not None
        )


class ContactStore(UpdatedMixin):
    model = Contact

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        session.execute(update(Contact).values(cached_presence=False))

    @staticmethod
    def add_to_sent(session: Session, contact_pk: int, msg_id: str) -> None:
        if (
            session.query(ContactSent.id)
            .where(ContactSent.contact_id == contact_pk)
            .where(ContactSent.msg_id == msg_id)
            .first()
        ) is not None:
            log.warning("Contact %s has already sent message %s", contact_pk, msg_id)
            return
        new = ContactSent(contact_id=contact_pk, msg_id=msg_id)
        session.add(new)

    @staticmethod
    def pop_sent_up_to(session: Session, contact_pk: int, msg_id: str) -> list[str]:
        result = []
        to_del = []
        for row in session.execute(
            select(ContactSent)
            .where(ContactSent.contact_id == contact_pk)
            .order_by(ContactSent.id)
        ).scalars():
            to_del.append(row.id)
            result.append(row.msg_id)
            if row.msg_id == msg_id:
                break
        session.execute(delete(ContactSent).where(ContactSent.id.in_(to_del)))
        return result


class MAMStore:
    def __init__(self, session: Session, session_maker) -> None:
        self.session = session_maker
        session.execute(
            update(ArchivedMessage).values(source=ArchivedMessageSource.BACKFILL)
        )

    @staticmethod
    def nuke_older_than(session: Session, days: int) -> None:
        session.execute(
            delete(ArchivedMessage).where(
                ArchivedMessage.timestamp < datetime.now() - timedelta(days=days)
            )
        )

    @staticmethod
    def add_message(
        session: Session,
        room_pk: int,
        message: HistoryMessage,
        archive_only: bool,
        legacy_msg_id: Optional[str],
    ) -> None:
        source = (
            ArchivedMessageSource.BACKFILL
            if archive_only
            else ArchivedMessageSource.LIVE
        )
        existing = session.execute(
            select(ArchivedMessage)
            .where(ArchivedMessage.room_id == room_pk)
            .where(ArchivedMessage.stanza_id == message.id)
        ).scalar()
        if existing is None and legacy_msg_id is not None:
            existing = session.execute(
                select(ArchivedMessage)
                .where(ArchivedMessage.room_id == room_pk)
                .where(ArchivedMessage.legacy_id == legacy_msg_id)
            ).scalar()
        if existing is not None:
            log.debug("Updating message %s in room %s", message.id, room_pk)
            existing.timestamp = message.when
            existing.stanza = str(message.stanza)
            existing.author_jid = message.stanza.get_from()
            existing.source = source
            existing.legacy_id = legacy_msg_id
            session.add(existing)
            return
        mam_msg = ArchivedMessage(
            stanza_id=message.id,
            timestamp=message.when,
            stanza=str(message.stanza),
            author_jid=message.stanza.get_from(),
            room_id=room_pk,
            source=source,
            legacy_id=legacy_msg_id,
        )
        session.add(mam_msg)

    @staticmethod
    def get_messages(
        session: Session,
        room_pk: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        before_id: Optional[str] = None,
        after_id: Optional[str] = None,
        ids: Collection[str] = (),
        last_page_n: Optional[int] = None,
        sender: Optional[str] = None,
        flip: bool = False,
    ) -> Iterator[HistoryMessage]:
        q = select(ArchivedMessage).where(ArchivedMessage.room_id == room_pk)
        if start_date is not None:
            q = q.where(ArchivedMessage.timestamp >= start_date)
        if end_date is not None:
            q = q.where(ArchivedMessage.timestamp <= end_date)
        if before_id is not None:
            stamp = session.execute(
                select(ArchivedMessage.timestamp).where(
                    ArchivedMessage.stanza_id == before_id,
                    ArchivedMessage.room_id == room_pk,
                )
            ).scalar_one_or_none()
            if stamp is None:
                raise XMPPError(
                    "item-not-found",
                    f"Message {before_id} not found",
                )
            q = q.where(ArchivedMessage.timestamp < stamp)
        if after_id is not None:
            stamp = session.execute(
                select(ArchivedMessage.timestamp).where(
                    ArchivedMessage.stanza_id == after_id,
                    ArchivedMessage.room_id == room_pk,
                )
            ).scalar_one_or_none()
            if stamp is None:
                raise XMPPError(
                    "item-not-found",
                    f"Message {after_id} not found",
                )
            q = q.where(ArchivedMessage.timestamp > stamp)
        if ids:
            q = q.filter(ArchivedMessage.stanza_id.in_(ids))
        if sender is not None:
            q = q.where(ArchivedMessage.author_jid == sender)
        if flip:
            q = q.order_by(ArchivedMessage.timestamp.desc())
        else:
            q = q.order_by(ArchivedMessage.timestamp.asc())
        msgs = list(session.execute(q).scalars())
        if ids and len(msgs) != len(ids):
            raise XMPPError(
                "item-not-found",
                "One of the requested messages IDs could not be found "
                "with the given constraints.",
            )
        if last_page_n is not None:
            if flip:
                msgs = msgs[:last_page_n]
            else:
                msgs = msgs[-last_page_n:]
        for h in msgs:
            yield HistoryMessage(
                stanza=str(h.stanza), when=h.timestamp.replace(tzinfo=timezone.utc)
            )

    @staticmethod
    def get_first(
        session: Session, room_pk: int, with_legacy_id: bool = False
    ) -> Optional[ArchivedMessage]:
        q = (
            select(ArchivedMessage)
            .where(ArchivedMessage.room_id == room_pk)
            .order_by(ArchivedMessage.timestamp.asc())
        )
        if with_legacy_id:
            q = q.filter(ArchivedMessage.legacy_id.isnot(None))
        return session.execute(q).scalar()

    @staticmethod
    def get_last(
        session: Session, room_pk: int, source: Optional[ArchivedMessageSource] = None
    ) -> Optional[ArchivedMessage]:
        q = select(ArchivedMessage).where(ArchivedMessage.room_id == room_pk)

        if source is not None:
            q = q.where(ArchivedMessage.source == source)

        return session.execute(q.order_by(ArchivedMessage.timestamp.desc())).scalar()

    def get_first_and_last(self, session: Session, room_pk: int) -> list[MamMetadata]:
        r = []
        first = self.get_first(session, room_pk)
        if first is not None:
            r.append(MamMetadata(first.stanza_id, first.timestamp))
        last = self.get_last(session, room_pk)
        if last is not None:
            r.append(MamMetadata(last.stanza_id, last.timestamp))
        return r

    @staticmethod
    def get_most_recent_with_legacy_id(
        session: Session, room_pk: int, source: Optional[ArchivedMessageSource] = None
    ) -> Optional[ArchivedMessage]:
        q = (
            select(ArchivedMessage)
            .where(ArchivedMessage.room_id == room_pk)
            .where(ArchivedMessage.legacy_id.isnot(None))
        )
        if source is not None:
            q = q.where(ArchivedMessage.source == source)
        return session.execute(q.order_by(ArchivedMessage.timestamp.desc())).scalar()

    @staticmethod
    def get_least_recent_with_legacy_id_after(
        session: Session,
        room_pk: int,
        after_id: str,
        source: ArchivedMessageSource = ArchivedMessageSource.LIVE,
    ) -> Optional[ArchivedMessage]:
        after_timestamp = (
            session.query(ArchivedMessage.timestamp)
            .filter(ArchivedMessage.room_id == room_pk)
            .filter(ArchivedMessage.legacy_id == after_id)
            .scalar()
        )
        q = (
            select(ArchivedMessage)
            .where(ArchivedMessage.room_id == room_pk)
            .where(ArchivedMessage.legacy_id.isnot(None))
            .where(ArchivedMessage.source == source)
            .where(ArchivedMessage.timestamp > after_timestamp)
        )
        return session.execute(q.order_by(ArchivedMessage.timestamp.asc())).scalar()

    @staticmethod
    def get_by_legacy_id(
        session: Session, room_pk: int, legacy_id: str
    ) -> Optional[ArchivedMessage]:
        return (
            session.query(ArchivedMessage)
            .filter(ArchivedMessage.room_id == room_pk)
            .filter(ArchivedMessage.legacy_id == legacy_id)
            .first()
        )


class RoomStore(UpdatedMixin):
    model = Room

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        session.execute(
            update(Room).values(
                subject_setter=None,
                user_resources=None,
                history_filled=False,
                participants_filled=False,
            )
        )

    @staticmethod
    def get_all(session: Session, user_pk: int) -> Iterator[Room]:
        yield from session.scalars(select(Room).where(Room.user_account_id == user_pk))


class ParticipantStore:
    def __init__(self, session: Session) -> None:
        session.execute(delete(Participant))

    @staticmethod
    def get_all(
        session, room_pk: int, user_included: bool = True
    ) -> Iterator[Participant]:
        query = select(Participant).where(Participant.room_id == room_pk)
        if not user_included:
            query = query.where(~Participant.is_user)
        yield from session.scalars(query).unique()


class BobStore:
    _ATTR_MAP = {
        "sha-1": "sha_1",
        "sha1": "sha_1",
        "sha-256": "sha_256",
        "sha256": "sha_256",
        "sha-512": "sha_512",
        "sha512": "sha_512",
    }

    _ALG_MAP = {
        "sha_1": hashlib.sha1,
        "sha_256": hashlib.sha256,
        "sha_512": hashlib.sha512,
    }

    def __init__(self) -> None:
        self.root_dir = config.HOME_DIR / "slidge_stickers"
        self.root_dir.mkdir(exist_ok=True)

    @staticmethod
    def __split_cid(cid: str) -> list[str]:
        return cid.removesuffix("@bob.xmpp.org").split("+")

    def __get_condition(self, cid: str):
        alg_name, digest = self.__split_cid(cid)
        attr = self._ATTR_MAP.get(alg_name)
        if attr is None:
            log.warning("Unknown hash algorithm: %s", alg_name)
            return None
        return getattr(Bob, attr) == digest

    def get(self, session: Session, cid: str) -> Bob | None:
        try:
            return session.query(Bob).filter(self.__get_condition(cid)).scalar()
        except ValueError:
            log.warning("Cannot get Bob with CID: %s", cid)
            return None

    def get_sticker(self, session: Session, cid: str) -> Sticker | None:
        bob = self.get(session, cid)
        if bob is None:
            return None
        return Sticker(
            self.root_dir / bob.file_name,
            bob.content_type,
            {h: getattr(bob, h) for h in self._ALG_MAP},
        )

    def get_bob(
        self, session: Session, _jid, _node, _ifrom, cid: str
    ) -> BitsOfBinary | None:
        stored = self.get(session, cid)
        if stored is None:
            return None
        bob = BitsOfBinary()
        bob["data"] = (self.root_dir / stored.file_name).read_bytes()
        if stored.content_type is not None:
            bob["type"] = stored.content_type
        bob["cid"] = cid
        return bob

    def del_bob(self, session: Session, _jid, _node, _ifrom, cid: str) -> None:
        try:
            file_name = session.scalar(
                delete(Bob).where(self.__get_condition(cid)).returning(Bob.file_name)
            )
        except ValueError:
            log.warning("Cannot delete Bob with CID: %s", cid)
            return None
        if file_name is None:
            log.warning("No BoB with CID: %s", cid)
            return None
        (self.root_dir / file_name).unlink()

    def set_bob(self, session: Session, _jid, _node, _ifrom, bob: BitsOfBinary) -> None:
        cid = bob["cid"]
        try:
            alg_name, digest = self.__split_cid(cid)
        except ValueError:
            log.warning("Invalid CID provided: %s", cid)
            return
        attr = self._ATTR_MAP.get(alg_name)
        if attr is None:
            log.warning("Cannot set Bob: Unknown algorithm type: %s", alg_name)
            return
        existing = self.get(session, bob["cid"])
        if existing:
            log.debug("Bob already exists")
            return
        bytes_ = bob["data"]
        path = self.root_dir / uuid.uuid4().hex
        if bob["type"]:
            path = path.with_suffix(guess_extension(bob["type"]) or "")
        path.write_bytes(bytes_)
        hashes = {k: v(bytes_).hexdigest() for k, v in self._ALG_MAP.items()}
        if hashes[attr] != digest:
            path.unlink(missing_ok=True)
            raise ValueError("Provided CID does not match calculated hash")
        row = Bob(file_name=path.name, content_type=bob["type"] or None, **hashes)
        session.add(row)


log = logging.getLogger(__name__)
