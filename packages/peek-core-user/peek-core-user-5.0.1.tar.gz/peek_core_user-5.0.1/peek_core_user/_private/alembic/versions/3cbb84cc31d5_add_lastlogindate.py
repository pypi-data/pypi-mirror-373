"""add lastLoginDate

Peek Plugin Database Migration Script

Revision ID: 3cbb84cc31d5
Revises: 94d5c124461d
Create Date: 2024-11-05 09:23:10.346803

"""

# revision identifiers, used by Alembic.
revision = "3cbb84cc31d5"
down_revision = "94d5c124461d"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        "InternalUser",
        sa.Column("lastLoginDate", sa.DateTime(), nullable=True),
        schema="core_user",
    )
    op.add_column(
        "InternalUser",
        sa.Column("lastLoginDeviceToken", sa.String(), nullable=True),
        schema="core_user",
    )


def downgrade():
    op.drop_column("InternalUser", "lastLoginDate", schema="core_user")
    op.drop_column("InternalUser", "lastLoginDeviceToken", schema="core_user")
