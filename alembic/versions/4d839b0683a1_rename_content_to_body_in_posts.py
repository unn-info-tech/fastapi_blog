"""rename_content_to_body_in_posts

Revision ID: 4d839b0683a1
Revises: b4ee114cb279
Create Date: 2026-04-20 22:10:39.535024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d839b0683a1'
down_revision: Union[str, Sequence[str], None] = 'b4ee114cb279'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'posts',
        'content',      # Eski nom
        new_column_name='body'   # Yangi nom
    )

def downgrade() -> None:
    op.alter_column(
        'posts',
        'body',
        new_column_name='content'
    )
