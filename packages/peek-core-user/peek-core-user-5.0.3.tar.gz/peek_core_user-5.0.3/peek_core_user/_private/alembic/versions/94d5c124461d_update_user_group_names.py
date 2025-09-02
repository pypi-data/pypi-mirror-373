"""update user group names

Peek Plugin Database Migration Script

Revision ID: 94d5c124461d
Revises: aa692f37c14d
Create Date: 2024-04-05 15:15:41.462937

"""

# revision identifiers, used by Alembic.
revision = "94d5c124461d"
down_revision = "aa692f37c14d"
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    op.execute(
        """
    UPDATE "core_user"."SettingProperty" SET 
    "char_value"='peek-admin-app-login' WHERE "char_value"='peek-admin-login';
    """
    )

    op.execute(
        """
    UPDATE "core_user"."SettingProperty" SET 
    "char_value"='peek-field-app-login' WHERE "char_value"='peek-mobile-login';
    """
    )

    op.execute(
        """
        UPDATE "core_user"."InternalGroup" SET "groupName"='peek-admin-app-login'
        WHERE "groupName"='peek-admin-login';
        """
    )

    op.execute(
        """
        UPDATE "core_user"."InternalGroup" SET "groupName"='peek-field-app-login'
        WHERE "groupName"='peek-mobile-login';
        """
    )


def downgrade():
    pass
