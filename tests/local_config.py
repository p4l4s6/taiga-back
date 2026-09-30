# Local-only override, never committed: points the test DB at the
# dockerized Postgres used for this session's local verification loop.
from tests.config import *  # noqa

DATABASES["default"]["HOST"] = "taiga-test-pg"
