import sys
import argparse
from alembic.config import Config
from alembic import command
from app.core.config import settings

def make_alembic_config():
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    return alembic_cfg

def upgrade():
    alembic_cfg = make_alembic_config()
    command.upgrade(alembic_cfg, "head")

def downgrade():
    alembic_cfg = make_alembic_config()
    command.downgrade(alembic_cfg, "-1")

def revision(message):
    alembic_cfg = make_alembic_config()
    command.revision(alembic_cfg, message=message, autogenerate=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database management script")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    
    subparsers.add_parser("upgrade", help="Upgrade to the latest revision")

    
    subparsers.add_parser("downgrade", help="Downgrade by one revision")

    
    rev_parser = subparsers.add_parser("revision", help="Create a new revision")
    rev_parser.add_argument("-m", "--message", required=True, help="Revision message")

    args = parser.parse_args()

    if args.command == "upgrade":
        upgrade()
    elif args.command == "downgrade":
        downgrade()
    elif args.command == "revision":
        revision(args.message)
    else:
        parser.print_help()
