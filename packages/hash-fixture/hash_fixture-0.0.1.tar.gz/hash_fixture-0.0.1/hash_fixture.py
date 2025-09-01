#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Alex Willmer <alex@moreati.org.uk>
# SPDX-License-Identifier: MIT

"""
Produce lines of reproducible test fixture by repeated hashing.

$ python3 hash_fixture.py --algorithm sha256 --line-count 3
000000001 hash-fixture/v0 sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=
000000002 hash-fixture/v0 sha256-/ut7HrShdeoT1CKjUIP5z/V/AhSHvjknBr3HRo3H/j4=
000000003 hash-fixture/v0 sha256-lL05gwF2SvDbQyK7C/2+JTFB4A3QMWYxn0fuLd9P5w0=
$ python3 hash_fixture.py --algorithm sha256 --line-count 3 | sha256sum
3ef0546c961d1c40b848248cea7c552faa8ce1fdc49cda8c77a090f64e5a047f

For a given set of options the output is deterministic, it will always have
the same checksum. So a large file can be reliably generated on demand, rather
than downloaded or stored in version control. Conversely the expected checksum
can be checked into version control, e.g. as part of a test suite.
"""

from __future__ import absolute_import, division, unicode_literals

import argparse
import base64
import hashlib
import sys

__version__ = '0.0.1'

FORMAT_VERSION = 0
SRI_ALGORITHMS = (
    'sha256',
    'sha384',
    'sha512',
)


class DEFAULTS(object):
    ALGORITHM = 'sha256'
    LABEL = 'hash-fixture'
    LINE_COUNT = 5


def lines(
    algorithm=DEFAULTS.ALGORITHM,
    label=DEFAULTS.LABEL,
    line_count=DEFAULTS.LINE_COUNT,
):
    hasher = hashlib.new(algorithm)
    version = FORMAT_VERSION
    for lineno in range(1, line_count + 1):
        digest = hasher.digest()
        digest_b64 = base64.b64encode(digest).decode('ascii')
        line = (
            '%(lineno)09d %(label)s/v%(version)s %(algorithm)s-%(digest_b64)s\n'
            % locals()
        )
        line_b = line.encode('ascii')
        yield line_b
        hasher.update(line_b)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__.strip().split('\n')[0],  # type: ignore
    )
    parser.add_argument(
        '-a',
        '--algorithm',
        default=DEFAULTS.ALGORITHM,
        choices=SRI_ALGORITHMS,
        help='Hash algorithm (default: %(default)s)',
    )
    parser.add_argument(
        '-l',
        '--label',
        default=DEFAULTS.LABEL,
        help='Label included in each line (default: %(default)s)',
    )
    parser.add_argument(
        '-n',
        '--line-count',
        default=DEFAULTS.LINE_COUNT,
        type=int,
        metavar='N',
        help='Number of lines of output to produce (default: %(default)s)',
    )
    parser.add_argument(
        '-o',
        '--out',
        default='-',
        metavar='FILE',
        help='Output destination (default: -, stdout)',
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%%(prog)s %s' % (__version__,),
    )
    args = parser.parse_args()
    output = lines(args.algorithm, args.label, args.line_count)
    if args.out == '-':
        sys.stdout.buffer.writelines(output)
    else:
        with open(args.out, 'wb') as out:
            out.writelines(output)
    sys.exit()


if __name__ == '__main__':
    main()
