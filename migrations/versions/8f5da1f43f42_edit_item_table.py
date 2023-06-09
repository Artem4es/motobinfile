"""edit Item table

Revision ID: 8f5da1f43f42
Revises: ac45b1b9f8bc
Create Date: 2023-04-13 18:20:06.871077

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f5da1f43f42'
down_revision = 'ac45b1b9f8bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('details', sa.Text(), nullable=True))
        batch_op.drop_column('image_url')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.VARCHAR(length=200), autoincrement=False, nullable=False))
        batch_op.drop_column('details')

    # ### end Alembic commands ###
