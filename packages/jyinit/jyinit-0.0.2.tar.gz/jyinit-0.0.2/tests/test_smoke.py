import tempfile
from pathlib import Path

from jyinit import main


def test_create_dry_run():
    # basic smoke: ensure CLI runs in dry-run mode without writing files
    main(['create', 'demo', '--types', 'library', '--dry-run'])
    # if no exception is raised, consider it a pass
    assert True