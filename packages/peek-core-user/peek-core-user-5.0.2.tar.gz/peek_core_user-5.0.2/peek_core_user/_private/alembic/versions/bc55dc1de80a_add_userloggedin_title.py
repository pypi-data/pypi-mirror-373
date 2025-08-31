"""add UserLoggedIn title

Peek Plugin Database Migration Script

Revision ID: bc55dc1de80a
Revises: 8fbb7b3fa4d8
Create Date: 2025-01-15 23:56:41.364881

"""

# revision identifiers, used by Alembic.
revision = "bc55dc1de80a"
down_revision = "8fbb7b3fa4d8"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        "UserLoggedIn",
        sa.Column("userTitle", sa.VARCHAR(), nullable=True),
        schema="core_user",
    )


def downgrade():

    op.drop_column("UserLoggedIn", "userTitle", schema="core_user")
