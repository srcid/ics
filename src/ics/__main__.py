"""Allow ``python -m ics``."""

from ics.cli import cli

if __name__ == '__main__':
  raise SystemExit(cli())
