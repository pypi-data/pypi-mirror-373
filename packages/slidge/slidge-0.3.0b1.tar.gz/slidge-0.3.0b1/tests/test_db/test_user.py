import pytest
from slixmpp import JID
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from slidge import GatewayUser
from slidge.db.meta import Base
from slidge.db.store import UserStore


@pytest.fixture
def engine():
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def store(engine):
    yield UserStore(sessionmaker(engine))


def test_user(engine, store: UserStore):
    with Session(engine) as orm:
        user1 = GatewayUser(jid=JID("test-user@test-host"), legacy_module_data={})
        orm.add(user1)
        orm.commit()
        assert user1.jid == JID("test-user@test-host")

    user1.preferences = {"section": {"do_xxx": True}}
    store.update(user1)
    del user1

    with Session(engine) as orm:
        user2 = orm.query(GatewayUser).filter_by(jid=JID("test-user@test-host")).one()
        assert user2.preferences == {"section": {"do_xxx": True}}

    user2.preferences["section"]["do_xxx"] = False

    store.update(user2)
    with Session(engine) as orm:
        user3 = orm.query(GatewayUser).filter_by(jid=JID("test-user@test-host")).one()
        assert not user3.preferences["section"]["do_xxx"]
