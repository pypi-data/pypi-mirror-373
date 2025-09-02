"""add plpython3u

Revision ID: 2efc91c0f0f6
Revises:
Create Date: 2020-04-24 19:43:44.230799

"""

# revision identifiers, used by Alembic.
revision = "2efc91c0f0f6"
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    sql = """
        DROP EXTENSION IF EXISTS plpython3u CASCADE;

        CREATE EXTENSION IF NOT EXISTS plpython3u;

        ALTER LANGUAGE plpython3u
            OWNER TO peek;
          """
    op.execute(sql)


def downgrade():
    pass
