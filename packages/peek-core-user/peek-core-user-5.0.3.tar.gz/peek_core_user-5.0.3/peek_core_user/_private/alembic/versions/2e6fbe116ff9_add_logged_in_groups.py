"""add logged in groups

Peek Plugin Database Migration Script

Revision ID: 2e6fbe116ff9
Revises: d03db0fcb600
Create Date: 2024-03-28 06:54:04.846124

"""

# revision identifiers, used by Alembic.
revision = "2e6fbe116ff9"
down_revision = "d03db0fcb600"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        table_name="UserLoggedIn",
        column=sa.Column("loggedInWithGroups", sa.String(), nullable=True),
        schema="core_user",
    )


def downgrade():
    op.drop_column("UserLoggedIn", "loggedInWithGroups", schema="core_user")
