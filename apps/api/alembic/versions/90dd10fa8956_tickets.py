"""tickets

Revision ID: 90dd10fa8956
Revises:
Create Date: 2026-02-19 20:47:55.393453
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "90dd10fa8956"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # IMPORTANT:
    # - Do NOT touch refresh_tokens here (autogenerate tried to drop it because metadata mismatch).
    # - Convert VARCHAR -> ENUM with explicit USING casts.
    # - Migrate ticket_messages data from (author_type, body) -> (role, content).

    # ---- 1) Create enum types if not exists (safe on reruns) ----
    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'message_role') THEN "
        "CREATE TYPE message_role AS ENUM ('user','agent','ai'); "
        "END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ticket_status') THEN "
        "CREATE TYPE ticket_status AS ENUM ('open','pending','closed'); "
        "END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ticket_priority') THEN "
        "CREATE TYPE ticket_priority AS ENUM ('low','medium','high'); "
        "END IF; END $$;"
    )

    # ---- 2) ticket_messages: add new columns as nullable, backfill, then enforce NOT NULL ----
    op.add_column(
        "ticket_messages",
        sa.Column("role", sa.Enum("user", "agent", "ai", name="message_role"), nullable=True),
    )
    op.add_column("ticket_messages", sa.Column("content", sa.Text(), nullable=True))
    op.add_column(
        "ticket_messages",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )

    # Backfill from old columns if they exist (author_type/body)
    # Map author_type -> role:
    #   - "agent" -> agent
    #   - "ai" -> ai
    #   - anything else -> user
    op.execute(
        """
        UPDATE ticket_messages
        SET
          content = COALESCE(content, body),
          role = COALESCE(
            role,
            CASE
              WHEN author_type ILIKE 'agent' THEN 'agent'::message_role
              WHEN author_type ILIKE 'ai' THEN 'ai'::message_role
              ELSE 'user'::message_role
            END
          ),
          created_at = COALESCE(created_at, now())
        """
    )

    # Now enforce NOT NULL
    op.alter_column("ticket_messages", "role", nullable=False)
    op.alter_column("ticket_messages", "content", nullable=False)
    op.alter_column("ticket_messages", "created_at", nullable=False)

    # Add index
    op.create_index(op.f("ix_ticket_messages_role"), "ticket_messages", ["role"], unique=False)

    # Drop old columns (only after migration)
    op.drop_column("ticket_messages", "author_type")
    op.drop_column("ticket_messages", "body")

    # ---- 3) tickets: add timestamps with defaults (safe for existing rows) ----
    op.add_column(
        "tickets",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.add_column(
        "tickets",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # subject length change
    op.alter_column(
        "tickets",
        "subject",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.String(length=200),
        existing_nullable=False,
    )

    # Convert status/priority to enums using explicit casts
    op.execute(
        "ALTER TABLE tickets "
        "ALTER COLUMN status TYPE ticket_status USING status::ticket_status"
    )
    op.execute(
        "ALTER TABLE tickets "
        "ALTER COLUMN priority TYPE ticket_priority USING priority::ticket_priority"
    )

    # Indexes
    op.create_index(op.f("ix_tickets_priority"), "tickets", ["priority"], unique=False)
    op.create_index(op.f("ix_tickets_status"), "tickets", ["status"], unique=False)

    # Optional: remove server_default if you don't want DB defaults (totally fine to keep)
    # op.alter_column("tickets", "created_at", server_default=None)
    # op.alter_column("tickets", "updated_at", server_default=None)
    # op.alter_column("ticket_messages", "created_at", server_default=None)


def downgrade() -> None:
    # Reverse indexes
    op.drop_index(op.f("ix_tickets_status"), table_name="tickets")
    op.drop_index(op.f("ix_tickets_priority"), table_name="tickets")

    # Convert enums back to varchar
    op.execute("ALTER TABLE tickets ALTER COLUMN priority TYPE VARCHAR(20) USING priority::text")
    op.execute("ALTER TABLE tickets ALTER COLUMN status TYPE VARCHAR(20) USING status::text")

    # subject length back
    op.alter_column(
        "tickets",
        "subject",
        existing_type=sa.String(length=200),
        type_=sa.VARCHAR(length=255),
        existing_nullable=False,
    )

    # Drop timestamps
    op.drop_column("tickets", "updated_at")
    op.drop_column("tickets", "created_at")

    # ticket_messages: restore old columns
    op.add_column("ticket_messages", sa.Column("body", sa.TEXT(), nullable=True))
    op.add_column("ticket_messages", sa.Column("author_type", sa.VARCHAR(length=20), nullable=True))

    # Backfill old columns from new ones
    op.execute(
        """
        UPDATE ticket_messages
        SET
          body = COALESCE(body, content),
          author_type = COALESCE(
            author_type,
            CASE
              WHEN role::text = 'agent' THEN 'agent'
              WHEN role::text = 'ai' THEN 'ai'
              ELSE 'user'
            END
          )
        """
    )

    # Enforce NOT NULL on restored columns
    op.alter_column("ticket_messages", "body", nullable=False)
    op.alter_column("ticket_messages", "author_type", nullable=False)

    # Drop new index + new columns
    op.drop_index(op.f("ix_ticket_messages_role"), table_name="ticket_messages")
    op.drop_column("ticket_messages", "created_at")
    op.drop_column("ticket_messages", "content")
    op.drop_column("ticket_messages", "role")

    # Drop enum types (only if no longer used)
    op.execute("DROP TYPE IF EXISTS ticket_priority")
    op.execute("DROP TYPE IF EXISTS ticket_status")
    op.execute("DROP TYPE IF EXISTS message_role")

    # IMPORTANT: Do NOT recreate refresh_tokens here (this migration never touched it)
