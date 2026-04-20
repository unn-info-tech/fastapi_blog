"""add_phone_to_users

Revision ID: b4ee114cb279
Revises: d341dbb172d0
Create Date: 2026-04-20 22:08:47.045912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4ee114cb279'
down_revision: Union[str, Sequence[str], None] = 'd341dbb172d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('phone', sa.String(20), nullable=True)
    )
    # Index ham qo'shamiz:
    op.create_index(
        'ix_users_phone',
        'users',
        ['phone'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_users_phone', table_name='users')
    op.drop_column('users', 'phone')