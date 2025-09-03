import base64
import functools
import logging
import os
import re
import shutil
import stat
import tempfile
import warnings
from datetime import datetime
from itertools import chain
from mimetypes import guess_extension, guess_type
from pathlib import Path
from typing import Collection, Optional, Sequence, Union
from urllib.parse import quote as urlquote
from uuid import uuid4
from xml.etree import ElementTree as ET

import thumbhash
from PIL import Image, ImageOps
from slixmpp import JID, Message
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.plugins.xep_0264.stanza import Thumbnail
from slixmpp.plugins.xep_0363 import FileUploadError
from slixmpp.plugins.xep_0447.stanza import StatelessFileSharing

from ...db.avatar import avatar_cache
from ...db.models import Attachment
from ...util.types import (
    LegacyAttachment,
    LegacyMessageType,
    LegacyThreadType,
    MessageReference,
)
from ...util.util import fix_suffix
from .. import config
from .message_text import TextMessageMixin


class AttachmentMixin(TextMessageMixin):
    is_group: bool

    async def __upload(
        self,
        file_path: Path,
        file_name: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> str | None:
        if file_name and file_path.name != file_name:
            d = Path(tempfile.mkdtemp())
            temp = d / file_name
            temp.symlink_to(file_path)
            file_path = temp
        else:
            d = None
        if config.UPLOAD_SERVICE:
            domain = None
        else:
            domain = re.sub(r"^.*?\.", "", self.xmpp.boundjid.bare)
        try:
            new_url = await self.xmpp.plugin["xep_0363"].upload_file(
                filename=file_path,
                content_type=content_type,
                ifrom=config.UPLOAD_REQUESTER or self.xmpp.boundjid,
                domain=JID(domain),
            )
        except (FileUploadError, IqError, IqTimeout) as e:
            warnings.warn(f"Something is wrong with the upload service: {e!r}")
            return None
        finally:
            if d is not None:
                file_path.unlink()
                d.rmdir()

        return new_url

    @staticmethod
    async def __no_upload(
        file_path: Path,
        file_name: Optional[str] = None,
        legacy_file_id: Optional[Union[str, int]] = None,
    ):
        file_id = str(uuid4()) if legacy_file_id is None else str(legacy_file_id)
        assert config.NO_UPLOAD_PATH is not None
        assert config.NO_UPLOAD_URL_PREFIX is not None
        destination_dir = Path(config.NO_UPLOAD_PATH) / file_id

        if destination_dir.exists():
            log.debug("Dest dir exists: %s", destination_dir)
            files = list(f for f in destination_dir.glob("**/*") if f.is_file())
            if len(files) == 1:
                log.debug(
                    "Found the legacy attachment '%s' at '%s'",
                    legacy_file_id,
                    files[0],
                )
                name = files[0].name
                uu = files[0].parent.name  # anti-obvious url trick, see below
                return files[0], "/".join([file_id, uu, name])
            else:
                log.warning(
                    (
                        "There are several or zero files in %s, "
                        "slidge doesn't know which one to pick among %s. "
                        "Removing the dir."
                    ),
                    destination_dir,
                    files,
                )
                shutil.rmtree(destination_dir)

        log.debug("Did not find a file in: %s", destination_dir)
        # let's use a UUID to avoid URLs being too obvious
        uu = str(uuid4())
        destination_dir = destination_dir / uu
        destination_dir.mkdir(parents=True)

        name = file_name or file_path.name
        destination = destination_dir / name
        method = config.NO_UPLOAD_METHOD
        if method == "copy":
            shutil.copy2(file_path, destination)
        elif method == "hardlink":
            os.link(file_path, destination)
        elif method == "symlink":
            os.symlink(file_path, destination, target_is_directory=True)
        elif method == "move":
            shutil.move(file_path, destination)
        else:
            raise RuntimeError("No upload method not recognized", method)

        if config.NO_UPLOAD_FILE_READ_OTHERS:
            log.debug("Changing perms of %s", destination)
            destination.chmod(destination.stat().st_mode | stat.S_IROTH)
        uploaded_url = "/".join([file_id, uu, name])

        return destination, uploaded_url

    async def __valid_url(self, url: str) -> bool:
        async with self.session.http.head(url) as r:
            return r.status < 400

    async def __get_stored(self, attachment: LegacyAttachment) -> Attachment:
        if attachment.legacy_file_id is not None and self.session is not NotImplemented:
            with self.xmpp.store.session() as orm:
                stored = (
                    orm.query(Attachment)
                    .filter_by(
                        legacy_file_id=str(attachment.legacy_file_id),
                        user_account_id=self.session.user_pk,
                    )
                    .one_or_none()
                )
                if stored is not None:
                    if not await self.__valid_url(stored.url):
                        stored.url = None  # type:ignore
                    return stored
        return Attachment(
            user_account_id=None
            if self.session is NotImplemented
            else self.session.user_pk,
            legacy_file_id=None
            if attachment.legacy_file_id is None
            else str(attachment.legacy_file_id),
            url=attachment.url,
        )

    async def __get_url(
        self, attachment: LegacyAttachment, stored: Attachment
    ) -> tuple[bool, Optional[Path], str]:
        if attachment.url and config.USE_ATTACHMENT_ORIGINAL_URLS:
            return False, None, attachment.url

        file_name = attachment.name
        content_type = attachment.content_type
        file_path = attachment.path

        if file_name and len(file_name) > config.ATTACHMENT_MAXIMUM_FILE_NAME_LENGTH:
            log.debug("Trimming long filename: %s", file_name)
            base, ext = os.path.splitext(file_name)
            file_name = (
                base[: config.ATTACHMENT_MAXIMUM_FILE_NAME_LENGTH - len(ext)] + ext
            )

        if file_path is None:
            if file_name is None:
                file_name = str(uuid4())
                if content_type is not None:
                    ext = guess_extension(content_type, strict=False)  # type:ignore
                    if ext is not None:
                        file_name += ext
            temp_dir = Path(tempfile.mkdtemp())
            file_path = temp_dir / file_name
            if attachment.url:
                async with self.session.http.get(attachment.url) as r:
                    r.raise_for_status()
                    with file_path.open("wb") as f:
                        f.write(await r.read())

            elif attachment.stream is not None:
                data = attachment.stream.read()
                if data is None:
                    raise RuntimeError

                with file_path.open("wb") as f:
                    f.write(data)
            elif attachment.aio_stream is not None:
                # TODO: patch slixmpp to allow this as data source for
                #       upload_file() so we don't even have to write anything
                #       to disk.
                with file_path.open("wb") as f:
                    async for chunk in attachment.aio_stream:
                        f.write(chunk)
            elif attachment.data is not None:
                with file_path.open("wb") as f:
                    f.write(attachment.data)

            is_temp = not bool(config.NO_UPLOAD_PATH)
        else:
            is_temp = False

        assert isinstance(file_path, Path)
        if config.FIX_FILENAME_SUFFIX_MIME_TYPE:
            file_name = str(fix_suffix(file_path, content_type, file_name))

        if config.NO_UPLOAD_PATH:
            local_path, new_url = await self.__no_upload(
                file_path, file_name, stored.legacy_file_id
            )
            new_url = (config.NO_UPLOAD_URL_PREFIX or "") + "/" + urlquote(new_url)
        else:
            local_path = file_path
            new_url = await self.__upload(file_path, file_name, content_type)
        if stored.legacy_file_id and new_url is not None:
            stored.url = new_url

        return is_temp, local_path, new_url

    async def __set_sims(
        self,
        msg: Message,
        uploaded_url: str,
        path: Optional[Path],
        attachment: LegacyAttachment,
        stored: Attachment,
    ) -> Thumbnail | None:
        if stored.sims is not None:
            ref = self.xmpp["xep_0372"].stanza.Reference(xml=ET.fromstring(stored.sims))
            msg.append(ref)
            if ref["sims"]["file"].get_plugin("thumbnail", check=True):
                return ref["sims"]["file"]["thumbnail"]
            else:
                return None

        if not path:
            return None

        ref = self.xmpp["xep_0385"].get_sims(
            path, [uploaded_url], attachment.content_type, attachment.caption
        )
        if attachment.name:
            ref["sims"]["file"]["name"] = attachment.name
        thumbnail = None
        if attachment.content_type is not None and attachment.content_type.startswith(
            "image"
        ):
            try:
                h, x, y = await self.xmpp.loop.run_in_executor(
                    avatar_cache._thread_pool, get_thumbhash, path
                )
            except Exception as e:
                log.debug("Could not generate a thumbhash", exc_info=e)
            else:
                thumbnail = ref["sims"]["file"]["thumbnail"]
                thumbnail["width"] = x
                thumbnail["height"] = y
                thumbnail["media-type"] = "image/thumbhash"
                thumbnail["uri"] = "data:image/thumbhash;base64," + urlquote(h)

        stored.sims = str(ref)
        msg.append(ref)

        return thumbnail

    def __set_sfs(
        self,
        msg: Message,
        uploaded_url: str,
        path: Optional[Path],
        attachment: LegacyAttachment,
        stored: Attachment,
        thumbnail: Optional[Thumbnail] = None,
    ) -> None:
        if stored.sfs is not None:
            msg.append(StatelessFileSharing(xml=ET.fromstring(stored.sfs)))
            return

        if not path:
            return

        sfs = self.xmpp["xep_0447"].get_sfs(
            path, [uploaded_url], attachment.content_type, attachment.caption
        )
        if attachment.name:
            sfs["file"]["name"] = attachment.name
        if thumbnail is not None:
            sfs["file"].append(thumbnail)
        stored.sfs = str(sfs)
        msg.append(sfs)

    def __send_url(
        self,
        msg: Message,
        legacy_msg_id: LegacyMessageType,
        uploaded_url: str,
        caption: Optional[str] = None,
        carbon: bool = False,
        when: Optional[datetime] = None,
        correction: bool = False,
        **kwargs,
    ) -> list[Message]:
        msg["oob"]["url"] = uploaded_url
        msg["body"] = uploaded_url
        if caption:
            m1 = self._send(msg, carbon=carbon, **kwargs)
            m2 = self.send_text(
                caption,
                legacy_msg_id=legacy_msg_id,
                when=when,
                carbon=carbon,
                correction=correction,
                **kwargs,
            )
            return [m1, m2] if m2 else [m1]
        else:
            if correction:
                msg["replace"]["id"] = self._replace_id(legacy_msg_id)
            else:
                self._set_msg_id(msg, legacy_msg_id)
            return [self._send(msg, carbon=carbon, **kwargs)]

    def __get_base_message(
        self,
        legacy_msg_id: Optional[LegacyMessageType] = None,
        reply_to: Optional[MessageReference] = None,
        when: Optional[datetime] = None,
        thread: Optional[LegacyThreadType] = None,
        carbon: bool = False,
        correction: bool = False,
        mto: Optional[JID] = None,
    ) -> Message:
        if correction and (original_xmpp_id := self._legacy_to_xmpp(legacy_msg_id)):
            with self.xmpp.store.session() as orm:
                xmpp_ids = self.xmpp.store.id_map.get_xmpp(
                    orm, self._recipient_pk(), str(legacy_msg_id), self.is_group
                )

            for xmpp_id in xmpp_ids:
                if xmpp_id == original_xmpp_id:
                    continue
                self.retract(xmpp_id, thread)

        if reply_to is not None and reply_to.body:
            # We cannot have a "quote fallback" for attachments since most (all?)
            # XMPP clients will only treat a message as an attachment if the
            # body is the URL and nothing else.
            reply_to_for_attachment: MessageReference | None = MessageReference(
                reply_to.legacy_id, reply_to.author
            )
        else:
            reply_to_for_attachment = reply_to

        return self._make_message(
            when=when,
            reply_to=reply_to_for_attachment,
            carbon=carbon,
            mto=mto,
            thread=thread,
        )

    async def send_file(
        self,
        attachment: LegacyAttachment | Path | str,
        legacy_msg_id: Optional[LegacyMessageType] = None,
        *,
        reply_to: Optional[MessageReference] = None,
        when: Optional[datetime] = None,
        thread: Optional[LegacyThreadType] = None,
        **kwargs,
    ) -> tuple[Optional[str], list[Message]]:
        """
        Send a single file from this :term:`XMPP Entity`.

        :param attachment: The file to send.
            Ideally, a :class:`.LegacyAttachment` with a unique ``legacy_file_id``
            attribute set, to optimise potential future reuses.
            It can also be:
            - a :class:`pathlib.Path` instance to point to a local file, or
            - a ``str``, representing a fetchable HTTP URL.
        :param legacy_msg_id: If you want to be able to transport read markers from the gateway
            user to the legacy network, specify this
        :param reply_to: Quote another message (:xep:`0461`)
        :param when: when the file was sent, for a "delay" tag (:xep:`0203`)
        :param thread:
        """
        coro = self.__send_file(
            attachment,
            legacy_msg_id,
            reply_to=reply_to,
            when=when,
            thread=thread,
            **kwargs,
        )
        if self.session is NotImplemented:
            return await coro
        elif not isinstance(attachment, LegacyAttachment):
            return await coro
        elif attachment.legacy_file_id is None:
            return await coro
        else:
            # prevents race conditions where we download the same thing several time
            # and end up attempting to insert it twice in the DB, raising an
            # IntegrityError.
            async with self.session.lock(("attachment", attachment.legacy_file_id)):
                return await coro

    async def __send_file(
        self,
        attachment: LegacyAttachment | Path | str,
        legacy_msg_id: Optional[LegacyMessageType] = None,
        *,
        reply_to: Optional[MessageReference] = None,
        when: Optional[datetime] = None,
        thread: Optional[LegacyThreadType] = None,
        **kwargs,
    ) -> tuple[Optional[str], list[Message]]:
        store_multi = kwargs.pop("store_multi", True)
        carbon = kwargs.pop("carbon", False)
        mto = kwargs.pop("mto", None)
        correction = kwargs.get("correction", False)

        msg = self.__get_base_message(
            legacy_msg_id, reply_to, when, thread, carbon, correction, mto
        )

        if isinstance(attachment, str):
            attachment = LegacyAttachment(url=attachment)
        elif isinstance(attachment, Path):
            attachment = LegacyAttachment(path=attachment)

        stored = await self.__get_stored(attachment)

        if attachment.content_type is None and (
            name := (attachment.name or attachment.url or attachment.path)
        ):
            attachment.content_type, _ = guess_type(name)

        if stored.url:
            is_temp = False
            local_path = None
            new_url = stored.url
        else:
            is_temp, local_path, new_url = await self.__get_url(attachment, stored)
            if new_url is None:
                msg["body"] = (
                    "I tried to send a file, but something went wrong. "
                    "Tell your slidge admin to check the logs."
                )
                self._set_msg_id(msg, legacy_msg_id)
                return None, [self._send(msg, **kwargs)]

        stored.url = new_url
        thumbnail = await self.__set_sims(msg, new_url, local_path, attachment, stored)
        self.__set_sfs(msg, new_url, local_path, attachment, stored, thumbnail)

        if self.session is not NotImplemented:
            with self.xmpp.store.session(expire_on_commit=False) as orm:
                orm.add(stored)
                orm.commit()

        if is_temp and isinstance(local_path, Path):
            local_path.unlink()
            local_path.parent.rmdir()

        msgs = self.__send_url(
            msg, legacy_msg_id, new_url, attachment.caption, carbon, when, **kwargs
        )
        if self.session is not NotImplemented:
            if store_multi:
                self.__store_multi(legacy_msg_id, msgs)
        return new_url, msgs

    def __send_body(
        self,
        body: Optional[str] = None,
        legacy_msg_id: Optional[LegacyMessageType] = None,
        reply_to: Optional[MessageReference] = None,
        when: Optional[datetime] = None,
        thread: Optional[LegacyThreadType] = None,
        **kwargs,
    ) -> Optional[Message]:
        if body:
            return self.send_text(
                body,
                legacy_msg_id,
                reply_to=reply_to,
                when=when,
                thread=thread,
                **kwargs,
            )
        else:
            return None

    async def send_files(
        self,
        attachments: Collection[LegacyAttachment],
        legacy_msg_id: Optional[LegacyMessageType] = None,
        body: Optional[str] = None,
        *,
        reply_to: Optional[MessageReference] = None,
        when: Optional[datetime] = None,
        thread: Optional[LegacyThreadType] = None,
        body_first: bool = False,
        correction: bool = False,
        correction_event_id: Optional[LegacyMessageType] = None,
        **kwargs,
    ) -> None:
        # TODO: once the epic XEP-0385 vs XEP-0447 battle is over, pick
        #       one and stop sending several attachments this way
        # we attach the legacy_message ID to the last message we send, because
        # we don't want several messages with the same ID (especially for MUC MAM)
        if not attachments and not body:
            # ignoring empty message
            return
        send_body = functools.partial(
            self.__send_body,
            body=body,
            reply_to=reply_to,
            when=when,
            thread=thread,
            correction=correction,
            legacy_msg_id=legacy_msg_id,
            correction_event_id=correction_event_id,
            **kwargs,
        )
        all_msgs = []
        if body_first:
            all_msgs.append(send_body())
        last_attachment_i = len(attachments) - 1
        for i, attachment in enumerate(attachments):
            last = i == last_attachment_i
            if last and not body:
                legacy = legacy_msg_id
            else:
                legacy = None
            _url, msgs = await self.send_file(
                attachment,
                legacy,
                reply_to=reply_to,
                when=when,
                thread=thread,
                store_multi=False,
                **kwargs,
            )
            all_msgs.extend(msgs)
        if not body_first:
            all_msgs.append(send_body())
        self.__store_multi(legacy_msg_id, all_msgs)

    def __store_multi(
        self,
        legacy_msg_id: Optional[LegacyMessageType],
        all_msgs: Sequence[Optional[Message]],
    ) -> None:
        if legacy_msg_id is None:
            return
        ids = []
        for msg in all_msgs:
            if not msg:
                continue
            if stanza_id := msg.get_plugin("stanza_id", check=True):
                ids.append(stanza_id["id"])
            else:
                ids.append(msg.get_id())
        with self.xmpp.store.session() as orm:
            self.xmpp.store.id_map.set_msg(
                orm, self._recipient_pk(), str(legacy_msg_id), ids, self.is_group
            )
            orm.commit()


def get_thumbhash(path: Path) -> tuple[str, int, int]:
    with path.open("rb") as fp:
        img = Image.open(fp)
        width, height = img.size
        img = img.convert("RGBA")
        if width > 100 or height > 100:
            img.thumbnail((100, 100))
    img = ImageOps.exif_transpose(img)
    rgba_2d = list(img.getdata())
    rgba = list(chain(*rgba_2d))
    ints = thumbhash.rgba_to_thumb_hash(img.width, img.height, rgba)
    return base64.b64encode(bytes(ints)).decode(), width, height


log = logging.getLogger(__name__)
