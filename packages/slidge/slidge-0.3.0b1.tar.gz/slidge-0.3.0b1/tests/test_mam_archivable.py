from slixmpp import register_stanza_plugin, Message
from slixmpp.plugins.xep_0333.stanza import Displayed
from slixmpp.plugins.xep_0334 import Store, NoStore, NoPermanentStore
from slixmpp.plugins.xep_0424.stanza import Retract

from slidge.group.archive import archivable
from slixmpp.test import SlixTest

class TestArchivable(SlixTest):
    def setUp(self):
        register_stanza_plugin(Message, Displayed)
        register_stanza_plugin(Message, Retract)
        register_stanza_plugin(Message, Store)
        register_stanza_plugin(Message, NoStore)
        register_stanza_plugin(Message, NoPermanentStore)

    def test_marker(self):
        msg = Message()
        assert not archivable(msg)
        msg.enable("displayed")
        assert archivable(msg)

    def test_retract(self):
        msg = Message()
        assert not archivable(msg)
        msg.enable("retract")
        assert archivable(msg)

    def test_hint_store(self):
        msg = Message()
        assert not archivable(msg)
        msg.enable("store")
        assert archivable(msg)

    def test_hint_no_store(self):
        msg = Message()
        msg["body"] = "boobobo"
        assert archivable(msg)

        msg.enable("no-store")
        assert not archivable(msg)

    def test_hint_no_permanent_store(self):
        msg = Message()
        msg["body"] = "boobobo"
        assert archivable(msg)

        msg.enable("no-permanent-store")
        assert not archivable(msg)
