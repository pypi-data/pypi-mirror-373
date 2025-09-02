"""drop unique model title idx

Peek Plugin Database Migration Script

Revision ID: 0f1665e2ea55
Revises: 0b20ccfb7a6a
Create Date: 2025-08-09 14:10:16.016184

"""

# revision identifiers, used by Alembic.
revision = "0f1665e2ea55"
down_revision = "0b20ccfb7a6a"
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    op.drop_index(
        "idx_DocDbProp_model_title",
        table_name="DocDbProperty",
        schema="core_docdb",
    )


def downgrade():
    op.create_index(
        "idx_DocDbProp_model_title",
        "DocDbProperty",
        ["modelSetId", "title"],
        unique=True,
        schema="core_docdb",
    )
