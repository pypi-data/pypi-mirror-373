"""add upgrades

Revision ID: ebd75b9feaa7
Revises: 3abcc44f7f91
Create Date: 2024-08-24 09:42:21.199679

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import wuttjamaican.db.util

# revision identifiers, used by Alembic.
revision: str = "ebd75b9feaa7"
down_revision: Union[str, None] = "3abcc44f7f91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # upgrade
    sa.Enum("PENDING", "EXECUTING", "SUCCESS", "FAILURE", name="upgradestatus").create(
        op.get_bind()
    )
    op.create_table(
        "upgrade",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("executing", sa.Boolean(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING",
                "EXECUTING",
                "SUCCESS",
                "FAILURE",
                name="upgradestatus",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("executed", sa.DateTime(timezone=True), nullable=True),
        sa.Column("executed_by_uuid", wuttjamaican.db.util.UUID(), nullable=True),
        sa.Column("exit_code", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_uuid"],
            ["user.uuid"],
            name=op.f("fk_upgrade_created_by_uuid_user"),
        ),
        sa.ForeignKeyConstraint(
            ["executed_by_uuid"],
            ["user.uuid"],
            name=op.f("fk_upgrade_executed_by_uuid_user"),
        ),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_upgrade")),
    )


def downgrade() -> None:

    # upgrade
    op.drop_table("upgrade")
    sa.Enum("PENDING", "EXECUTING", "SUCCESS", "FAILURE", name="upgradestatus").drop(
        op.get_bind()
    )
