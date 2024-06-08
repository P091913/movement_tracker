"""update combos with combo share column

Revision ID: 3158206b5c7e
Revises: 2fb8397d7075
Create Date: 2024-06-08 09:49:10.548067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3158206b5c7e'
down_revision: Union[str, None] = '2fb8397d7075'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('combo', sa.Column('combo_share', sa.String(length=1), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('combo', 'combo_share')
    # ### end Alembic commands ###
