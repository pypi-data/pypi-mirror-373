"""Drop InternalUser rows from LDAP for userUuid change

Peek Plugin Database Migration Script

Revision ID: d79da9333e2a
Revises: 43df0e05c728
Create Date: 2022-07-26 15:24:24.408496

"""

# revision identifiers, used by Alembic.
revision = "d79da9333e2a"
down_revision = "43df0e05c728"
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    op.drop_index(
        "idx_InternalUserTable_importHash",
        table_name="InternalUser",
        schema="core_user",
    )

    op.execute(
        """
        DELETE FROM core_user."InternalUser"
        WHERE "importSource" = 'LDAP';
        """
    )

    op.create_index(
        "idx_InternalUserTable_importHash",
        "InternalUser",
        ["importHash"],
        unique=False,
        schema="core_user",
    )


def downgrade():
    pass
