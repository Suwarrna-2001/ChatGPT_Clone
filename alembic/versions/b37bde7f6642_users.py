"""users

Revision ID: b37bde7f6642
Revises: 7f08a1eddcc0
Create Date: 2024-09-17 14:12:07.942338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b37bde7f6642'
down_revision: Union[str, None] = '7f08a1eddcc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('sessions')
