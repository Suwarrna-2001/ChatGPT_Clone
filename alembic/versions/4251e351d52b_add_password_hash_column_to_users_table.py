"""Add password_hash column to users table

Revision ID: 4251e351d52b
Revises: 10fb8e662b88
Create Date: 2024-09-26 13:43:31.495045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4251e351d52b'
down_revision: Union[str, None] = '10fb8e662b88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('password_hash', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'password_hash')