# SPDX-FileCopyrightText: 2025 Alex Willmer <alex@moreati.org.uk>
# SPDX-License-Identifier: MIT

import json
import os
import pathlib
import subprocess
import textwrap
import sys

import pytest

import hash_fixture


def expected_lines():
    with open('tests/fixtures/v0/lines.json') as f:
        cases = json.load(f)
    for d in cases:
        lines = [s.encode() for s in d['lines']]
        yield (d['algorithm'], d['line_count'], lines)


def algorithms():
    return ['sha256', 'sha384', 'sha512']


def line_counts():
    return [0, 1, 5, 10, 50, 100, 500, 1000]


@pytest.mark.parametrize('algorithm', algorithms())
def test_empty(algorithm):
    assert b'' == b''.join(hash_fixture.lines(algorithm=algorithm, line_count=0))


@pytest.mark.parametrize(
    ['algorithm', 'line_count', 'expected_lines'],
    expected_lines(),
)
def test_lines(algorithm, line_count, expected_lines):
    assert expected_lines == list(
        hash_fixture.lines(algorithm=algorithm, line_count=line_count)
    )


@pytest.mark.parametrize('algorithm', algorithms())
def test_shasums(algorithm: str, tmp_path: pathlib.Path):
    os.link(
        f'tests/fixtures/v0/{algorithm}/{algorithm}sums.txt',
        f'{tmp_path}/{algorithm}sums.txt',
    )
    for line_count in line_counts():
        subprocess.run(
            [
                sys.executable,
                '-mhash_fixture',
                f'--algorithm={algorithm}',
                f'--line-count={line_count}',
                f'--out=hf-v0-{algorithm}-{line_count}-lines',
            ],
            cwd=tmp_path,
        )
    shasum_proc = subprocess.run(
        [f'{algorithm}sum', '-c', f'{algorithm}sums.txt'],
        cwd=tmp_path,
    )
    assert shasum_proc.returncode == 0


def test_stdout_default(capfd):
    subprocess.run([sys.executable, '-m', 'hash_fixture'])
    captured = capfd.readouterr()
    assert captured.out == textwrap.dedent(
        """\
        000000001 hash-fixture/v0 sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=
        000000002 hash-fixture/v0 sha256-/ut7HrShdeoT1CKjUIP5z/V/AhSHvjknBr3HRo3H/j4=
        000000003 hash-fixture/v0 sha256-lL05gwF2SvDbQyK7C/2+JTFB4A3QMWYxn0fuLd9P5w0=
        000000004 hash-fixture/v0 sha256-PvBUbJYdHEC4SCSM6nxVL6qM4f3EnNqMd6CQ9k5aBH8=
        000000005 hash-fixture/v0 sha256-DrLBwbHnsedQf05SWC8RDHK6b8ZQcZ9BLiL1MYoFtJQ=
        """,
    )
