"""sessions

Revision ID: 7f08a1eddcc0
Revises: 
Create Date: 2024-09-17 14:11:50.247112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f08a1eddcc0'
down_revision: Union[str, None] = None  #kisi se connection nhi hai iska ye ek tareeke ka entry point hai 
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False)#####updations done so make it happen in actual
    )


def downgrade() -> None:
    op.drop_table('users')
