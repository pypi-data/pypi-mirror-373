import asyncio
import unittest.mock
from datetime import datetime, timezone
from typing import Optional

import pytest
from slixmpp.exceptions import XMPPError

from conftest import AvatarFixtureMixin
from slixmpp import JID, Iq
from slixmpp import __version__ as slix_version

from slidge import BaseGateway, BaseSession, MucType, GatewayUser
from slidge.contact import LegacyContact
from slidge.core.session import _sessions
from slidge.group import LegacyBookmarks, LegacyMUC
from slidge.util.test import SlidgeTest
from slidge.util.types import HoleBound


class Gateway(BaseGateway):
    COMPONENT_NAME = "A test"
    GROUPS = True


class Session(BaseSession):
    async def login(self):
        return "YUP"


class Contact(LegacyContact):
    async def update_info(self):
        if self.legacy_id.startswith("room"):
            raise XMPPError
        if self.legacy_id != "juliet":
            return
        self.is_friend = True
        self.added_to_roster = True
        self.name = "A name"
        self.online("status msg")
        await self.set_avatar("AVATAR_URL")


class MUC(LegacyMUC):
    async def update_info(self):
        if self.legacy_id in ("room-noinfo", "room-duplicate-participant"):
            return
        self.name = "Cool name"
        self.description = "Cool description"
        self.type = MucType.CHANNEL_NON_ANONYMOUS
        self.subject = "Cool subject"
        self.subject_setter = await self.get_participant_by_legacy_id("juliet")
        self.subject_date = datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc)
        self.n_participants = 666
        self.user_nick = "Cool nick"
        await self.set_avatar("AVATAR_URL")

    async def backfill(
        self,
        after: Optional[HoleBound] = None,
        before: Optional[HoleBound] = None,
    ):
        if self.legacy_id == "room-history":
            juliet = await self.get_participant_by_legacy_id("juliet")
            juliet.send_text("history")

    async def fill_participants(self):
        if "duplicate-participant" in self.legacy_id:
            yield await self.get_participant_by_legacy_id("duplicate")
            yield await self.get_participant_by_legacy_id("duplicate")

class Bookmarks(LegacyBookmarks):
    async def fill(self):
        return


@pytest.mark.usefixtures("avatar")
class TestSession2(AvatarFixtureMixin, SlidgeTest):
    plugin = globals()
    xmpp: Gateway

    def setUp(self):
        super().setUp()
        with self.xmpp.store.session() as orm:
            user = GatewayUser(
                jid=JID("romeo@montague.lit/gajim").bare,
                legacy_module_data={"username": "romeo", "city": ""},
                preferences={"sync_avatar": True, "sync_presence": True},
            )
            orm.add(user)
            orm.commit()
        self.run_coro(
            self.xmpp._BaseGateway__dispatcher._on_user_register(
                Iq(sfrom="romeo@montague.lit/gajim")
            )
        )
        welcome = self.next_sent()
        assert welcome["body"]
        stanza = self.next_sent()
        assert "logging in" in stanza["status"].lower(), stanza
        stanza = self.next_sent()
        assert "syncing contacts" in stanza["status"].lower(), stanza
        stanza = self.next_sent()
        assert "syncing groups" in stanza["status"].lower(), stanza
        probe = self.next_sent()
        assert probe.get_type() == "probe"
        stanza = self.next_sent()
        assert "yup" in stanza["status"].lower(), stanza

        self.send(  # language=XML
            """
            <iq type="get"
                to="romeo@montague.lit"
                id="1"
                from="aim.shakespeare.lit">
              <pubsub xmlns="http://jabber.org/protocol/pubsub">
                <items node="urn:xmpp:avatar:metadata" />
              </pubsub>
            </iq>
            """
        )

    def tearDown(self):
        super().tearDown()
        _sessions.clear()

    @property
    def romeo_session(self) -> Session:
        return BaseSession.get_self_or_unique_subclass().from_jid(
            JID("romeo@montague.lit")
        )

    def test_contact_init(self):
        self.run_coro(self.romeo_session.contacts.by_legacy_id("juliet"))
        self.send(  # language=XML
            f"""
            <presence from="juliet@aim.shakespeare.lit/slidge"
                      to="romeo@montague.lit">
              <c xmlns="http://jabber.org/protocol/caps"
                 node="http://slixmpp.com/ver/{slix_version}"
                 hash="sha-1"
                 ver="OErK4nBtx6JV2uK05xyCf47ioT0=" />
              <status>status msg</status>
            </presence>
            """
        )
        self.send(  # language=XML
            """
            <message type="headline"
                     from="juliet@aim.shakespeare.lit"
                     to="romeo@montague.lit">
              <event xmlns="http://jabber.org/protocol/pubsub#event">
                <items node="http://jabber.org/protocol/nick">
                  <item>
                    <nick xmlns="http://jabber.org/protocol/nick">A name</nick>
                  </item>
                </items>
              </event>
            </message>
            """,
            use_values=False,
        )
        self.send(  # language=XML
            f"""
            <message type="headline"
                     from="juliet@aim.shakespeare.lit"
                     to="romeo@montague.lit">
              <event xmlns="http://jabber.org/protocol/pubsub#event">
                <items node="urn:xmpp:avatar:metadata">
                  <item id="{self.avatar_sha1}">
                    <metadata xmlns="urn:xmpp:avatar:metadata">
                      <info id="{self.avatar_sha1}"
                            type="image/png"
                            bytes="{len(self.avatar_bytes)}"
                            height="5"
                            width="5" />
                    </metadata>
                  </item>
                </items>
              </event>
            </message>
            """,
            use_values=False,  # I do not understand why this is necessary, related on test run order?!?
        )
        assert self.next_sent() is None
        juliet: Contact = self.run_coro(
            self.romeo_session.contacts.by_legacy_id("juliet")
        )
        assert juliet.name == "A name"
        assert juliet.is_friend
        cached_presence = juliet._get_last_presence()
        assert cached_presence is not None
        assert cached_presence.pstatus == "status msg"
        assert juliet.avatar is not None

    def test_group_init(self):
        self.run_coro(self.romeo_session.bookmarks.by_legacy_id("room"))
        self.next_sent()  # juliet presence
        self.next_sent()  # juliet nick
        self.next_sent()  # juliet avatar
        muc = self.run_coro(self.romeo_session.bookmarks.by_legacy_id("room"))
        assert self.next_sent() is None
        # self.run_coro(muc._set)
        assert muc.name == "Cool name"
        assert muc.description == "Cool description"
        assert muc.type == MucType.CHANNEL_NON_ANONYMOUS
        assert muc.n_participants == 666
        assert muc.user_nick == "Cool nick"
        assert muc.avatar is not None
        assert muc.subject == "Cool subject"
        assert muc.subject_date == datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc)
        assert (
            muc.subject_setter
            == self.run_coro(self.romeo_session.contacts.by_legacy_id("juliet")).name
        )

    def test_set_user_nick_outside_update_info(self):
        muc = self.run_coro(self.romeo_session.bookmarks.by_legacy_id("room"))
        assert muc.user_nick == "Cool nick"
        muc.user_nick = "Cooler nick"
        muc = self.run_coro(self.romeo_session.bookmarks.by_legacy_id("room"))
        assert muc.user_nick == "Cooler nick"

    def test_user_available(self):
        self.run_coro(self.romeo_session.contacts.by_legacy_id("juliet"))
        for _ in range(3):
            assert self.next_sent() is not None
        self.recv(  # language=XML
            f"""
            <presence from="romeo@montague.lit/movim"
                      to="juliet@{self.xmpp.boundjid.bare}" />
            """
        )
        assert self.next_sent() is not None
        assert self.next_sent() is None

    def test_leave_group(self):
        muc: LegacyMUC = self.run_coro(
            self.romeo_session.bookmarks.by_legacy_id("room")
        )
        self.next_sent()  # juliet presence
        self.next_sent()  # juliet nick
        self.next_sent()  # juliet avatar
        assert self.next_sent() is None
        assert muc.jid in list([m.jid for m in self.romeo_session.bookmarks])

        muc.add_user_resource("gajim")
        self.run_coro(self.romeo_session.bookmarks.remove(muc))
        self.send(  # language=XML
            """
            <presence xmlns="jabber:component:accept"
                      type="unavailable"
                      from="room@aim.shakespeare.lit/Cool nick"
                      to="romeo@montague.lit/gajim">
              <x xmlns="http://jabber.org/protocol/muc#user">
                <item affiliation="member"
                      role="participant"
                      jid="romeo@montague.lit">
                  <reason>You left this group from the official client.</reason>
                </item>
                <status code="307" />
                <status code="100" />
                <status code="110" />
              </x>
              <occupant-id xmlns="urn:xmpp:occupant-id:0"
                           id="slidge-user" />
              <priority>0</priority>
            </presence>
            """
        )
        assert muc.jid not in list([m.jid for m in self.romeo_session.bookmarks])

    def test_correction(self):
        with unittest.mock.patch("slidge.BaseSession.on_text", return_value="legacy-msg-id") as on_text:
            self.recv(  # language=XML
                """
            <message from='romeo@montague.lit/gajim'
                     type='chat'
                     to='juliet@aim.shakespeare.lit'
                     id="msg-id">
              <body>body</body>
            </message>
            """
            )
            on_text.assert_awaited_once()
        with unittest.mock.patch("slidge.BaseSession.on_correct") as on_correct:
            self.recv(  # language=XML
                """
            <message from='romeo@montague.lit/gajim'
                     type='chat'
                     to='juliet@aim.shakespeare.lit'
                     id="msg-id">
              <body>new body</body>
              <replace id='msg-id'
                       xmlns='urn:xmpp:message-correct:0' />
            </message>
            """
            )
            on_correct.assert_awaited_once()
            contact, body, msg_id, *_ = on_correct.call_args[0]
            assert contact.name == "A name"
            assert body == "new body"
            assert msg_id == "legacy-msg-id"

    def test_participant_avatar_race_condition(self):
        muc: LegacyMUC = self.run_coro(
            self.romeo_session.bookmarks.by_legacy_id("room")
        )
        self.next_sent()  # juliet presence
        self.next_sent()  # juliet nick
        self.next_sent()  # juliet avatar
        contact1: Contact = self.run_coro(self.romeo_session.contacts.by_legacy_id("slow"))
        contact1.online()
        _participant1 = self.run_coro(muc.get_participant_by_contact(contact1))
        contact1.avatar = "SLOW"
        self.run_coro(asyncio.wait_for(contact1._set_avatar_task, 2))

        contact2: Contact = self.run_coro(self.romeo_session.contacts.by_legacy_id("slow"))
        assert contact2.avatar.url == "AVATAR_URL"

    def test_conflict_on_join(self):
        muc: LegacyMUC = self.run_coro(
            self.romeo_session.bookmarks.by_legacy_id("room-noinfo")
        )
        assert self.next_sent() is None
        self.recv(  # language=XML
            f"""
            <presence from="romeo@montague.lit/movim"
                      to="{muc.jid}/nick">
              <x xmlns='http://jabber.org/protocol/muc' />
            </presence>
            """
        )
        self.send(  # language=XML
            """
            <presence from="room-noinfo@aim.shakespeare.lit/romeo"
                      to="romeo@montague.lit/movim">
              <x xmlns="http://jabber.org/protocol/muc#user">
                <item affiliation="member"
                      role="participant" />
                <status code="210" />
                <status code="110" />
              </x>
              <occupant-id xmlns="urn:xmpp:occupant-id:0"
                           id="slidge-user" />
            </presence>
            """
        )
        subject = self.next_sent()
        assert subject["subject"] == "unnamed-room"
        self.send(  # language=XML
            """
            <presence to="romeo@montague.lit/movim"
                      from="room-noinfo@aim.shakespeare.lit">
              <x xmlns="vcard-temp:x:update">
                <photo />
              </x>
            </presence>
            """,
            use_values=False
        )
        assert self.next_sent() is None

    def test_fill_participant_duplicate(self):
        muc: LegacyMUC = self.run_coro(
            self.romeo_session.bookmarks.by_legacy_id("room-duplicate-participant")
        )
        assert self.next_sent() is None
        self.recv(  # language=XML
            f"""
            <presence from="romeo@montague.lit/movim"
                      to="{muc.jid}/nick">
              <x xmlns='http://jabber.org/protocol/muc' />
            </presence>
            """
        )
        assert self.next_sent().get_from().resource == "duplicate"
        assert self.next_sent().get_from().resource == muc.user_nick
