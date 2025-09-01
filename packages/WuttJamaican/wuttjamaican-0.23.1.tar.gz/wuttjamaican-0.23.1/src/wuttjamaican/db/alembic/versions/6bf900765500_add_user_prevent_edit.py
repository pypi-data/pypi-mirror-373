"""add user.prevent_edit

Revision ID: 6bf900765500
Revises: ebd75b9feaa7
Create Date: 2024-11-24 16:52:36.773657

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6bf900765500"
down_revision: Union[str, None] = "ebd75b9feaa7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # user
    op.add_column("user", sa.Column("prevent_edit", sa.Boolean(), nullable=True))


def downgrade() -> None:

    # user
    op.drop_column("user", "prevent_edit")
