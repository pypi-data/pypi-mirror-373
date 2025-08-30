"""add otp-group

Peek Plugin Database Migration Script

Revision ID: 8fbb7b3fa4d8
Revises: 3cbb84cc31d5
Create Date: 2024-12-02 19:26:32.558867

"""

# revision identifiers, used by Alembic.
revision = "8fbb7b3fa4d8"
down_revision = "3cbb84cc31d5"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.execute(
        """
        INSERT INTO core_user."InternalGroup"( "groupName", "groupTitle")
        VALUES ('peek-field-app-otp-login',	'Use One Time Password')	
    """
    )


def downgrade():
    pass
