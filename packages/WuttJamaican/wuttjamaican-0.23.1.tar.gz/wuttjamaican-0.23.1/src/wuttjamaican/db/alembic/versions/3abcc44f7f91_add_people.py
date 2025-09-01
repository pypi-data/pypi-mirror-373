"""add people

Revision ID: 3abcc44f7f91
Revises: d686f7abe3e0
Create Date: 2024-07-14 15:14:30.552682

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "3abcc44f7f91"
down_revision: Union[str, None] = "d686f7abe3e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # person
    op.create_table(
        "person",
        sa.Column("uuid", wuttjamaican.db.util.UUID(), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=True),
        sa.Column("middle_name", sa.String(length=50), nullable=True),
        sa.Column("last_name", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_person")),
    )

    # user
    op.add_column(
        "user", sa.Column("person_uuid", wuttjamaican.db.util.UUID(), nullable=True)
    )
    op.create_foreign_key(
        op.f("fk_user_person_uuid_person"), "user", "person", ["person_uuid"], ["uuid"]
    )


def downgrade() -> None:

    # user
    op.drop_constraint(op.f("fk_user_person_uuid_person"), "user", type_="foreignkey")
    op.drop_column("user", "person_uuid")

    # person
    op.drop_table("person")
