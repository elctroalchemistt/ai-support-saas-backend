"""tickets"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

revision = "90dd10fa8956"
down_revision = None
branch_labels = None
depends_on = None


def table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:

    # ---------- CREATE ENUM TYPES SAFELY ----------
    op.execute("""
    DO $$ BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'message_role') THEN
            CREATE TYPE message_role AS ENUM ('user','agent','ai');
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$ BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ticket_status') THEN
            CREATE TYPE ticket_status AS ENUM ('open','pending','closed');
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$ BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ticket_priority') THEN
            CREATE TYPE ticket_priority AS ENUM ('low','medium','high');
        END IF;
    END $$;
    """)

    message_role_enum = postgresql.ENUM(
        "user", "agent", "ai",
        name="message_role",
        create_type=False
    )

    ticket_status_enum = postgresql.ENUM(
        "open", "pending", "closed",
        name="ticket_status",
        create_type=False
    )

    ticket_priority_enum = postgresql.ENUM(
        "low", "medium", "high",
        name="ticket_priority",
        create_type=False
    )

    # ---------- CREATE TABLES IF NOT EXIST ----------
    if not table_exists("tickets"):
        op.create_table(
            "tickets",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("subject", sa.String(200), nullable=False),
            sa.Column("status", ticket_status_enum, nullable=False),
            sa.Column("priority", ticket_priority_enum, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True),
                      server_default=sa.text("now()"), nullable=False),
        )

    if not table_exists("ticket_messages"):
        op.create_table(
            "ticket_messages",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("ticket_id", sa.Integer, nullable=False),
            sa.Column("role", message_role_enum, nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.text("now()"), nullable=False),
        )

        op.create_foreign_key(
            "fk_ticket_messages_ticket",
            "ticket_messages",
            "tickets",
            ["ticket_id"],
            ["id"],
            ondelete="CASCADE"
        )

        op.create_index(
            "ix_ticket_messages_role",
            "ticket_messages",
            ["role"]
        )


def downgrade() -> None:
    op.drop_table("ticket_messages")
    op.drop_table("tickets")

    op.execute("DROP TYPE IF EXISTS ticket_priority")
    op.execute("DROP TYPE IF EXISTS ticket_status")
    op.execute("DROP TYPE IF EXISTS message_role")