# SPDX-FileCopyrightText: 2025 Alex Willmer <alex@moreati.org.uk>
# SPDX-License-Identifier: MIT

import hashlib
import os
import subprocess

import nox

# Try `uv venv` first, fallback to `python -m virtualenv`
nox.options.default_venv_backend = 'uv|virtualenv'

# Nox doesn't natively handle PEP 735 dependency groups yet
# https://nox.thea.codes/en/stable/tutorial.html#loading-dependencies-from-pyproject-toml-or-scripts
# https://github.com/wntrblm/nox/issues/845
PYPROJECT = nox.project.load_toml('pyproject.toml')
PYTHONS = [
    '2.7',
    '3.6',
    '3.7',
    '3.8',
    '3.9',
    '3.10',
    '3.11',
    '3.12',
    '3.13',
    '3.14',
]


@nox.session(default=False)
def generate(session: nox.Session):
    "Regenerate tests/fixtures/*/*.txt"
    session.install('-e.')
    for algorithm in ['sha256', 'sha384', 'sha512']:
        os.makedirs(f'tests/fixtures/v0/{algorithm}', exist_ok=True)
        with open(
            f'tests/fixtures/v0/{algorithm}/{algorithm}sums.txt', 'w') as f:
            for line_count in [0, 1, 5, 10, 50, 100, 500, 1000]:
                proc = subprocess.Popen(
                    [
                        'python',
                        '-mhash_fixture',
                        f'--algorithm={algorithm}',
                        f'--line-count={line_count}',
                    ],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                )
                stdout, _ = proc.communicate()
                hasher = hashlib.new(algorithm)
                hasher.update(stdout)
                f.write(f'{hasher.hexdigest()}  hf-v0-{algorithm}-{line_count}-lines\n')


@nox.session(tags=['clean'])
def cov_clean(session: nox.Session):
    session.install(*nox.project.dependency_groups(PYPROJECT, 'coverage'))
    session.run('coverage', 'erase')


@nox.session(requires=['cov_clean'], tags=['test'])
@nox.parametrize('python', PYTHONS, ids=PYTHONS)
def test(session: nox.Session):
    session.install('-e.', *nox.project.dependency_groups(PYPROJECT, 'test'))
    session.run('coverage', 'run', '-m', 'pytest')


@nox.session(tags=['test'])
def test_readme(session: nox.Session):
    session.install('-e.')
    session.run('python', '-mdoctest', 'README.rst')


@nox.session
def typecheck(session: nox.Session):
    session.install('-e.', 'mypy')
    session.run('mypy', '--strict', 'hash_fixture.pyi')


@nox.session(requires=['test'], tags=['report'])
def cov_report(session: nox.Session):
    session.install(*nox.project.dependency_groups(PYPROJECT, 'coverage'))
    session.run('coverage', 'combine')
    session.run('coverage', 'report')
    session.run('coverage', 'html')
