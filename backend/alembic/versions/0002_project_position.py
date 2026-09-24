"""project position, so teachers can reorder projects

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'projects',
        sa.Column('position', sa.Integer(), server_default='0', nullable=False),
    )
    # Keep today's order (oldest first) within each program.
    op.execute(
        """
        UPDATE projects SET position = ranked.rn
        FROM (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY program_id ORDER BY id) - 1 AS rn
            FROM projects
        ) AS ranked
        WHERE projects.id = ranked.id
        """
    )


def downgrade() -> None:
    op.drop_column('projects', 'position')
