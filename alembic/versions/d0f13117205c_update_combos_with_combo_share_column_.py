"""update combos with combo share column to not nullable

Revision ID: d0f13117205c
Revises: 3158206b5c7e
Create Date: 2024-06-08 09:50:59.261042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0f13117205c'
down_revision: Union[str, None] = '3158206b5c7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('combo', 'combo_share',
               existing_type=sa.VARCHAR(length=1),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('combo', 'combo_share',
               existing_type=sa.VARCHAR(length=1),
               nullable=True)
    # ### end Alembic commands ###