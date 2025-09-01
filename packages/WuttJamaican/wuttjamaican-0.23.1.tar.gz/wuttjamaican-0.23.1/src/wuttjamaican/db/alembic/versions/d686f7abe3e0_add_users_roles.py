"""add users, roles

Revision ID: d686f7abe3e0
Revises: fc3a3bcaa069
Create Date: 2024-07-14 13:27:22.703093

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "d686f7abe3e0"
down_revision: Union[str, None] = "fc3a3bcaa069"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # role
    op.create_table(
        "role",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("name", name=op.f("uq_role_name")),
    )

    # user
    op.create_table(
        "user",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("username", sa.String(length=25), nullable=False),
        sa.Column("password", sa.String(length=60), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("username", name=op.f("uq_user_username")),
    )

    # permission
    op.create_table(
        "permission",
        sa.Column("role_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("permission", sa.String(length=254), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_uuid"], ["role.uuid"], name=op.f("fk_permission_role_uuid_role")
        ),
        sa.PrimaryKeyConstraint("role_uuid", "permission"),
    )

    # user_x_role
    op.create_table(
        "user_x_role",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("user_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("role_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_uuid"], ["role.uuid"], name=op.f("fk_user_x_role_role_uuid_role")
        ),
        sa.ForeignKeyConstraint(
            ["user_uuid"], ["user.uuid"], name=op.f("fk_user_x_role_user_uuid_user")
        ),
        sa.PrimaryKeyConstraint("uuid"),
    )


def downgrade() -> None:

    # user_x_role
    op.drop_table("user_x_role")

    # permission
    op.drop_table("permission")

    # user
    op.drop_table("user")

    # role
    op.drop_table("role")
