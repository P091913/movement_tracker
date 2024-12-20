"""session cookies

Revision ID: 7383988d9ec4
Revises: 2e4f852e78af
Create Date: 2024-06-10 17:55:55.937186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7383988d9ec4'
down_revision: Union[str, None] = '2e4f852e78af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password',
               existing_type=sa.VARCHAR(length=15),
               type_=sa.String(length=128),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password',
               existing_type=sa.String(length=128),
               type_=sa.VARCHAR(length=15),
               nullable=True)
    # ### end Alembic commands ###
