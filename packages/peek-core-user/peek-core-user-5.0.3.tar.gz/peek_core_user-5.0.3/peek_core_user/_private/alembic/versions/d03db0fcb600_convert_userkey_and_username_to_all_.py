"""Convert userKey and userName to all lowercase for InternalUser

Peek Plugin Database Migration Script

Revision ID: d03db0fcb600
Revises: eef485ef2e0e
Create Date: 2023-02-22 11:49:39.624413

"""

# revision identifiers, used by Alembic.
revision = "d03db0fcb600"
down_revision = "eef485ef2e0e"
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    op.execute(
        """DELETE FROM core_user."InternalUser"
        WHERE id in (
            SELECT id
            FROM core_user."InternalUser"
            WHERE lower("userKey") in (
                SELECT lower("userKey")
                FROM core_user."InternalUser"
                GROUP BY lower("userKey")
                HAVING count(lower("userKey")) > 1
            )
        )
        """
    )

    op.execute(
        """DELETE FROM core_user."InternalUser"
        WHERE id in (
            SELECT id
            FROM core_user."InternalUser"
            WHERE lower("userName") in (
                SELECT lower("userName")
                FROM core_user."InternalUser"
                GROUP BY lower("userName")
                HAVING count(lower("userName")) > 1
            )
        )
        """
    )

    op.execute(
        'UPDATE core_user."InternalUser" SET "userKey" = LOWER("userKey")'
    )
    op.execute(
        'UPDATE core_user."InternalUser" SET "userName" = LOWER("userName")'
    )


def downgrade():
    pass
