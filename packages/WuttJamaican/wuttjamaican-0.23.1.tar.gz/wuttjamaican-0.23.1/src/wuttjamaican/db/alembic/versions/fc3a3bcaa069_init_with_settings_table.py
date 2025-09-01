"""init with settings table

Revision ID: fc3a3bcaa069
Revises:
Create Date: 2024-07-10 20:33:41.273952

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fc3a3bcaa069"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = ("wutta",)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # setting
    op.create_table(
        "setting",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("name"),
    )


def downgrade() -> None:

    # setting
    op.drop_table("setting")
