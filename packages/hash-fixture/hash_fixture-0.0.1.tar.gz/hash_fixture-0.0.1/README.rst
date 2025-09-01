hash-fixture
============

Produce lines of reproducible test fixture by repeated hashing.

For a given set of options the output is deterministic, it will always have
the same checksum. So a large file can be reliably generated on demand, rather
than downloaded or stored in version control. Conversely the expected checksum
can be checked into version control, e.g. as part of a test suite.

Usage
-----

.. code:: pycon

   >>> import hash_fixture
   >>> lines = list(hash_fixture.lines(line_count=3))
   >>> for line in lines: print(line)
   b'000000001 hash-fixture/v0 sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=\n'
   b'000000002 hash-fixture/v0 sha256-/ut7HrShdeoT1CKjUIP5z/V/AhSHvjknBr3HRo3H/j4=\n'
   b'000000003 hash-fixture/v0 sha256-lL05gwF2SvDbQyK7C/2+JTFB4A3QMWYxn0fuLd9P5w0=\n'
   >>>
   >>> import hashlib
   >>> hashlib.sha256(b''.join(lines)).hexdigest()
   '3ef0546c961d1c40b848248cea7c552faa8ce1fdc49cda8c77a090f64e5a047f'

.. code:: console

   $ python3 -m hash_fixture --algorithm sha256 --line-count 3
   000000001 hash-fixture/v0 sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=
   000000002 hash-fixture/v0 sha256-/ut7HrShdeoT1CKjUIP5z/V/AhSHvjknBr3HRo3H/j4=
   000000003 hash-fixture/v0 sha256-lL05gwF2SvDbQyK7C/2+JTFB4A3QMWYxn0fuLd9P5w0=
   $ python3 -m hash_fixture --algorithm sha256 --line-count 3 | sha256sum
   3ef0546c961d1c40b848248cea7c552faa8ce1fdc49cda8c77a090f64e5a047f

Install
-------

Use

.. code:: shell

   python3 -m pip install hash-fixture

or

.. code:: shell

   uv pip install hash-fixture

or copy `hash_fixture.py` somewhere convenient, it is a self contained script.

License
-------

..
   SPDX-FileCopyrightText: 2025 Alex Willmer <alex@moreati.org.uk>
   SPDX-License-Identifier: MIT

MIT
