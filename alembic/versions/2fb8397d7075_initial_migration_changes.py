"""Initial Migration Changes

Revision ID: 2fb8397d7075
Revises: 
Create Date: 2024-06-04 13:52:14.168920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fb8397d7075'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('custom_trick',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('trick_name', sa.String(length=100), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('combo_custom_tricks',
    sa.Column('combo_id', sa.Integer(), nullable=False),
    sa.Column('custom_trick_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['combo_id'], ['combo.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['custom_trick_id'], ['custom_trick.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('combo_id', 'custom_trick_id')
    )
    op.create_table('combo_progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('attempts', sa.Integer(), nullable=False),
    sa.Column('successes', sa.Integer(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('combo_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['combo_id'], ['combo.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('combo_tricks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('combo_id', sa.Integer(), nullable=False),
    sa.Column('trick_id', sa.Integer(), nullable=False),
    sa.Column('trick_type', sa.String(length=50), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('move_id', sa.Integer(), nullable=True),
    sa.Column('custom_trick_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['combo_id'], ['combo.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['custom_trick_id'], ['custom_trick.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['move_id'], ['moves.move_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_constraint('combo_user_id_fkey', 'combo', type_='foreignkey')
    op.create_foreign_key(None, 'combo', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('combo_moves_combo_id_fkey', 'combo_moves', type_='foreignkey')
    op.drop_constraint('combo_moves_move_id_fkey', 'combo_moves', type_='foreignkey')
    op.create_foreign_key(None, 'combo_moves', 'combo', ['combo_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'combo_moves', 'moves', ['move_id'], ['move_id'], ondelete='CASCADE')
    op.drop_constraint('post_user_id_fkey', 'post', type_='foreignkey')
    op.create_foreign_key(None, 'post', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('session_details_user_id_fkey', 'session_details', type_='foreignkey')
    op.drop_constraint('session_details_move_id_fkey', 'session_details', type_='foreignkey')
    op.create_foreign_key(None, 'session_details', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'session_details', 'moves', ['move_id'], ['move_id'], ondelete='CASCADE')
    op.drop_constraint('user_moves_user_id_fkey', 'user_moves', type_='foreignkey')
    op.drop_constraint('user_moves_move_id_fkey', 'user_moves', type_='foreignkey')
    op.create_foreign_key(None, 'user_moves', 'moves', ['move_id'], ['move_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'user_moves', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_moves', type_='foreignkey')
    op.drop_constraint(None, 'user_moves', type_='foreignkey')
    op.create_foreign_key('user_moves_move_id_fkey', 'user_moves', 'moves', ['move_id'], ['move_id'])
    op.create_foreign_key('user_moves_user_id_fkey', 'user_moves', 'user', ['user_id'], ['id'])
    op.drop_constraint(None, 'session_details', type_='foreignkey')
    op.drop_constraint(None, 'session_details', type_='foreignkey')
    op.create_foreign_key('session_details_move_id_fkey', 'session_details', 'moves', ['move_id'], ['move_id'])
    op.create_foreign_key('session_details_user_id_fkey', 'session_details', 'user', ['user_id'], ['id'])
    op.drop_constraint(None, 'post', type_='foreignkey')
    op.create_foreign_key('post_user_id_fkey', 'post', 'user', ['user_id'], ['id'])
    op.drop_constraint(None, 'combo_moves', type_='foreignkey')
    op.drop_constraint(None, 'combo_moves', type_='foreignkey')
    op.create_foreign_key('combo_moves_move_id_fkey', 'combo_moves', 'moves', ['move_id'], ['move_id'])
    op.create_foreign_key('combo_moves_combo_id_fkey', 'combo_moves', 'combo', ['combo_id'], ['id'])
    op.drop_constraint(None, 'combo', type_='foreignkey')
    op.create_foreign_key('combo_user_id_fkey', 'combo', 'user', ['user_id'], ['id'])
    op.drop_table('combo_tricks')
    op.drop_table('combo_progress')
    op.drop_table('combo_custom_tricks')
    op.drop_table('custom_trick')
    # ### end Alembic commands ###
