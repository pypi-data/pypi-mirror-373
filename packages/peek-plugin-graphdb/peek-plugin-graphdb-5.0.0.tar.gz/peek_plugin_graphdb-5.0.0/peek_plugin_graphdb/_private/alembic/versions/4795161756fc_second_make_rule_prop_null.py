"""second make rule prop null

Peek Plugin Database Migration Script

Revision ID: 4795161756fc
Revises: 523b8e513a38
Create Date: 2025-08-05 21:41:46.453887

"""

# revision identifiers, used by Alembic.
revision = "4795161756fc"
down_revision = "523b8e513a38"
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    op.execute(
        """
        alter table  pl_graphdb."GraphDbTraceConfigRule"
        alter column "propertyValue"
        drop not null
        """
    )


def downgrade():
    pass
