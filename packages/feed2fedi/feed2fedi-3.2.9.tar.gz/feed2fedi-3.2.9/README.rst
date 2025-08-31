Feed2Fedi
=========

|Repo| |CI - Woodpecker| |Downloads|

|Checked against| |Checked with| |CodeLimit|

|Code style| |PyPI - Python Version| |PyPI - Wheel|

|AGPL|


Feed2Fedi is a Python bot that reads RSS feeds and automatically posts them to a Fediverse instance. It supports
instances running Mastodon, Takahe, and Pleroma.
Feed2Fedi has been inspired by `feed2toot`_.

Features
---------

* Feed2Fedi posts to `Fediverse`_ instances.
* Feed2Fedi attaches a picture to the post if the feed item contains a "media_thumbnail".
* Feed2Fedi can monitor multiple RSS/ATOM feeds at once
* Feed2Fedi is fully open-source, so you don't have to give an external service full access to your social media accounts

There is also some `Documentation`_ for Feed2Fedi.

If you'd like to delete older posts from your Fediverse account look into `Fedinesia`_ as a tool that might
work for you.

Disclaimer
----------

The developers of Feed2Fedi hold no liability for what you do with this script or what happens to you by using this
script. Abusing this script *can* get you banned from Fediverse instances, so make sure to read up on proper usage
for each site.

Setup and usage
---------------

Feed2Fedi is available on PyPi.org and I recommend installing it with pipx using the command below:

   `pipx install feed2fedi`

Once installed you can start it by issuing the `feed2fedi` command.

During the first run it will prompt for some values and create a `config.ini` file with sensible starting settings.

Then edit the `config.ini` file and add the RSS/ATOM feed in the feeds section and remove the sample feed. Detailed
information about config options is available in the `documentation`_.

Support Feed2Fedi
-----------------

A big thank you to the good folk over at `CharCha`_ who have allowed me to test Feed2Fedi against their
instance that is based on `Rebased`_ and `Soapbox`_.


There are a number of ways you can support Feed2Fedi:

- Create an issue with problems or ideas you have with/for Feed2Fedi
- You can `buy me a coffee`_.
- You can send me small change in Monero to the address below:

Monero donation address:
`84oC6aUX4yyRoEk6pMVVdZYZP4JGJZk4KKJq1p7n9ZqLPK8zH3W1vpFAnSxDQGbwmZAeXrE4w4ct6HqAXdM1K9LfCAxZx4u`

Changelog
---------

See the `Changelog`_ for any changes introduced with each version.

License
-------

Feed2Fedi is licensed under the `GNU Affero General Public License v3.0`_


.. _CharCha: https://charcha.cc/
.. _Soapbox: https://soapbox.pub/
.. _Rebased: https://gitlab.com/soapbox-pub/rebased
.. _feed2toot: https://gitlab.com/chaica/feed2toot
.. _Fediverse: https://fediverse.party/
.. _Fedinesia: https://pypi.org/project/fedinesia/
.. _Healthchecks: https://healthchecks.io/
.. _buy me a coffee: https://www.buymeacoffee.com/marvin8
.. _GNU Affero General Public License v3.0: http://www.gnu.org/licenses/agpl-3.0.html
.. _Changelog: https://codeberg.org/MarvinsMastodonTools/feed2fedi/src/branch/main/CHANGELOG.rst
.. _documentation: https://marvinsmastodontools.codeberg.page/feed2fedi/

.. |AGPL| image:: https://www.gnu.org/graphics/agplv3-with-text-162x68.png
    :alt: AGLP 3 or later
    :target: https://codeberg.org/MarvinsMastodonTools/feed2fedi/src/branch/main/license.md

.. |Repo| image:: https://img.shields.io/badge/repo-Codeberg.org-blue
    :alt: Repo at Codeberg
    :target: https://codeberg.org/MarvinsMastodonTools/feed2fedi

.. |Downloads| image:: https://pepy.tech/badge/feed2fedi
    :target: https://pepy.tech/project/feed2fedi

.. |Code style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code Style: Black
    :target: https://github.com/psf/black

.. |Checked against| image:: https://img.shields.io/badge/Safety--DB-Checked-green
    :alt: Checked against Safety DB
    :target: https://pyup.io/safety/

.. |Checked with| image:: https://img.shields.io/badge/pip--audit-Checked-green
    :alt: Checked with pip-audit
    :target: https://pypi.org/project/pip-audit/

.. |PyPI - Python Version| image:: https://img.shields.io/pypi/pyversions/feed2fedi

.. |PyPI - Wheel| image:: https://img.shields.io/pypi/wheel/feed2fedi

.. |CI - Woodpecker| image:: https://ci.codeberg.org/api/badges/MarvinsMastodonTools/feed2fedi/status.svg
    :target: https://ci.codeberg.org/MarvinsMastodonTools/feed2fedi

.. |CodeLimit| image:: https://img.shields.io/badge/CodeLimit-checked-green.svg
    :target: https://github.com/getcodelimit/codelimit
