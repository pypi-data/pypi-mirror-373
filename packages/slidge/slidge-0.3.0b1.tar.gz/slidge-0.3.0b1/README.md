![Slidge logo](https://codeberg.org/slidge/slidge/raw/branch/main/dev/assets/slidge-color-small.png)

[![woodpecker CI status](https://ci.codeberg.org/api/badges/14027/status.svg)](https://ci.codeberg.org/repos/14027)
[![coverage](https://slidge.im/coverage/slidge/main/coverage.svg)](https://slidge.im/coverage/slidge/main)
[![Chat](https://conference.nicoco.fr:5281/muc_badge/slidge@conference.nicoco.fr)](https://conference.nicoco.fr:5281/muc_log/slidge/)

Slidge is an XMPP (puppeteer) gateway library in python.
It makes
[writing gateways to other chat networks](https://slidge.im/docs/slidge/main/dev/tutorial.html)
(*legacy modules*) as frictionless as possible.
It supports fancy IM features, such as
[(emoji) reactions](https://xmpp.org/extensions/xep-0444.html),
[replies](https://xmpp.org/extensions/xep-0461.html), and
[retractions](https://xmpp.org/extensions/xep-0424.html).
The full list of supported XEPs in on [xmpp.org](https://xmpp.org/software/slidge/).

Status
------

Slidge is **beta**-grade software. It support groups and 1:1 chats.
Try slidge and give us some
feedback, through the [MUC](xmpp:slidge@conference.nicoco.fr?join) or the
[issue tracker](https://codeberg.org/slidge/slidge/issues).
Don't be shy!

Usage
-----

A minimal (and fictional!) slidge-powered "legacy module" looks like this:

```python
from cool_chat_lib import CoolClient
from slidge import BaseGateway, BaseSession
from slidge.contact import LegacyContact
from slidge.group import LegacyMUC
from slidge.db import GatewayUser


class Gateway(BaseGateway):
    # Various aspects of the gateway component are configured as class
    # attributes of the concrete Gateway class
    COMPONENT_NAME = "Gateway to the super duper chat network"


class Session(BaseSession):
    def __init__(self, user: GatewayUser):
        super().__init__(user)
        self.legacy_client = CoolClient(
            login=user.legacy_module_data["username"],
            password=user.legacy_module_data["password"],
        )

    async def on_text(self, chat: LegacyContact | LegacyMUC, text: str, **kwargs):
        """
        Triggered when the slidge user sends an XMPP message through the gateway
        """
        self.legacy_client.send_message(text=text, destination=chat.legacy_id)
```

There's more in [the tutorial](https://slidge.im/docs/slidge/main/dev/tutorial.html)!

Installation
------------

⚠️  Slidge is a lib for gateway developers, if you are an XMPP server admin and
want to install gateways on your server, you are looking for a
[slidge-based gateway](https://codeberg.org/explore/repos?q=slidge&topic=1).
or the
[slidge-debian](https://git.sr.ht/~nicoco/slidge-debian)
bundle.

[![pypi version](https://badge.fury.io/py/slidge.svg)](https://pypi.org/project/slidge/)

[![Packaging status](https://repology.org/badge/vertical-allrepos/slidge.svg)](https://repology.org/project/slidge/versions)

Slidge is available on
[codeberg](https://codeberg.org/slidge/slidge/releases)
and [pypi](https://pypi.org/project/slidge/).
Refer to [the docs](https://slidge.im/docs/slidge/main/admin/install.html) for details.

About privacy
-------------

Slidge (and most if not all XMPP gateway that I know of) will break
end-to-end encryption, or more precisely one of the 'ends' become the
gateway itself. If privacy is a major concern for you, my advice would
be to:

-   use XMPP + OMEMO
-   self-host your gateways
-   have your gateways hosted by someone you know AFK and trust

Related projects
----------------

-   [Spectrum](https://www.spectrum.im/)
-   [telegabber](https://dev.narayana.im/narayana/telegabber)
-   [biboumi](https://biboumi.louiz.org/)
-   [Bifröst](https://github.com/matrix-org/matrix-bifrost)
-   [Mautrix](https://github.com/mautrix)
-   [matterbridge](https://github.com/42wim/matterbridge)

Thank you, [Trung](https://trung.fun/), for the slidge logo!
