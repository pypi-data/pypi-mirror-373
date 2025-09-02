sqlmap
======

|Python 2.6|2.7|3.x| |License| |X|

sqlmap is an open source penetration testing tool that automates the
process of detecting and exploiting SQL injection flaws and taking over
of database servers. It comes with a powerful detection engine, many
niche features for the ultimate penetration tester and a broad range of
switches lasting from database fingerprinting, over data fetching from
the database, to accessing the underlying file system and executing
commands on the operating system via out-of-band connections.

Screenshots
-----------

.. figure:: https://raw.github.com/wiki/sqlmapproject/sqlmap/images/sqlmap_screenshot.png
   :alt: Screenshot


You can visit the `collection of
screenshots <https://github.com/sqlmapproject/sqlmap/wiki/Screenshots>`__
demonstrating some of features on the wiki.

Installation
------------

You can use pip to install and/or upgrade the sqlmap to latest (monthly) tagged version with: ::

    pip install --upgrade sqlmap

Alternatively, you can download the latest tarball by clicking
`here <https://github.com/sqlmapproject/sqlmap/tarball/master>`__ or
latest zipball by clicking
`here <https://github.com/sqlmapproject/sqlmap/zipball/master>`__.

If you prefer fetching daily updates, you can download sqlmap by cloning the
`Git <https://github.com/sqlmapproject/sqlmap>`__ repository:

::

    git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev

sqlmap works out of the box with
`Python <http://www.python.org/download/>`__ version **2.6**, **2.7** and
**3.x** on any platform.

Usage
-----

To get a list of basic options and switches use:

::

    sqlmap -h

To get a list of all options and switches use:

::

    sqlmap -hh

You can find a sample run `here <https://asciinema.org/a/46601>`__. To
get an overview of sqlmap capabilities, list of supported features and
description of all options and switches, along with examples, you are
advised to consult the `user's
manual <https://github.com/sqlmapproject/sqlmap/wiki/Usage>`__.

Links
-----

-  Homepage: https://sqlmap.org
-  Download:
   `.tar.gz <https://github.com/sqlmapproject/sqlmap/tarball/master>`__
   or `.zip <https://github.com/sqlmapproject/sqlmap/zipball/master>`__
-  Commits RSS feed:
   https://github.com/sqlmapproject/sqlmap/commits/master.atom
-  Issue tracker: https://github.com/sqlmapproject/sqlmap/issues
-  User's manual: https://github.com/sqlmapproject/sqlmap/wiki
-  Frequently Asked Questions (FAQ):
   https://github.com/sqlmapproject/sqlmap/wiki/FAQ
-  X: https://x.com/sqlmap
-  Demos: http://www.youtube.com/user/inquisb/videos
-  Screenshots: https://github.com/sqlmapproject/sqlmap/wiki/Screenshots

.. |Python 2.6|2.7|3.x| image:: https://img.shields.io/badge/python-2.6|2.7|3.x-yellow.svg
   :target: https://www.python.org/
.. |License| image:: https://img.shields.io/badge/license-GPLv2-red.svg
   :target: https://raw.githubusercontent.com/sqlmapproject/sqlmap/master/LICENSE
.. |X| image:: https://img.shields.io/badge/x-@sqlmap-blue.svg
   :target: https://x.com/sqlmap

.. pandoc --from=markdown --to=rst --output=README.rst sqlmap/README.md
.. http://rst.ninjs.org/
