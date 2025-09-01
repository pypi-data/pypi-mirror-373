"""add user_api_token

Revision ID: efdcb2c75034
Revises: 6bf900765500
Create Date: 2025-08-08 08:58:19.376105

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "efdcb2c75034"
down_revision: Union[str, None] = "6bf900765500"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # user_api_token
    op.create_table(
        "user_api_token",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("user_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("token_string", sa.String(length=255), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_uuid"], ["user.uuid"], name=op.f("fk_user_api_token_user_uuid_user")
        ),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_user_api_token")),
    )


def downgrade() -> None:

    # user_api_token
    op.drop_table("user_api_token")
