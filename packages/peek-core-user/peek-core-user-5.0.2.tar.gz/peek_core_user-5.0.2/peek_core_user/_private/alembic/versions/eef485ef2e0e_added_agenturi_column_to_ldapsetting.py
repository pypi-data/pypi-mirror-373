"""Added agentUri column to LdapSetting

Peek Plugin Database Migration Script

Revision ID: eef485ef2e0e
Revises: d79da9333e2a
Create Date: 2022-08-24 09:10:13.594230

"""

# revision identifiers, used by Alembic.
revision = "eef485ef2e0e"
down_revision = "d79da9333e2a"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        "LdapSetting",
        sa.Column(
            "agentHost",
            sa.String(),
            nullable=True,
        ),
        schema="core_user",
    )
    op.execute(
        """
        UPDATE "core_user"."LdapSetting" SET "agentHost" = NULL;
        """
    )


def downgrade():
    op.drop_column("LdapSetting", "agentHost", schema="core_user")
