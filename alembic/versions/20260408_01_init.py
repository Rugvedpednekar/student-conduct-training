"""initial tables

Revision ID: 20260408_01
Revises:
Create Date: 2026-04-08
"""

from alembic import op
import sqlalchemy as sa

revision = "20260408_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=30), nullable=False, unique=True),
    )
    op.create_index("ix_roles_id", "roles", ["id"])
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=60), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "editable_content",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("page_name", sa.String(length=80), nullable=False),
        sa.Column("section_key", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("page_name", "section_key", name="uq_page_section"),
    )
    op.create_index("ix_editable_content_id", "editable_content", ["id"])
    op.create_index("ix_editable_content_page_name", "editable_content", ["page_name"])
    op.create_index("ix_editable_content_section_key", "editable_content", ["section_key"])


def downgrade() -> None:
    op.drop_index("ix_editable_content_section_key", table_name="editable_content")
    op.drop_index("ix_editable_content_page_name", table_name="editable_content")
    op.drop_index("ix_editable_content_id", table_name="editable_content")
    op.drop_table("editable_content")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_index("ix_roles_id", table_name="roles")
    op.drop_table("roles")
