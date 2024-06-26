"""Modifies Preferences Table

Revision ID: c43bfa3ca751
Revises: 
Create Date: 2024-04-27 15:48:29.130194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c43bfa3ca751'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('preference', schema=None) as batch_op:
        batch_op.add_column(sa.Column('preference_value1', sa.String(length=30), nullable=False))
        batch_op.add_column(sa.Column('preference_value2', sa.String(length=30), nullable=False))
        batch_op.alter_column('preference_name',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=50),
               existing_nullable=False)
        batch_op.drop_column('preference_value')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('preference', schema=None) as batch_op:
        batch_op.add_column(sa.Column('preference_value', sa.VARCHAR(length=255), nullable=False))
        batch_op.alter_column('preference_name',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)
        batch_op.drop_column('preference_value2')
        batch_op.drop_column('preference_value1')

    # ### end Alembic commands ###
