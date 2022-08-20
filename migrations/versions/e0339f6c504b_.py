"""empty message

Revision ID: e0339f6c504b
Revises: e4548ac57c34
Create Date: 2022-08-20 01:58:38.576775

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0339f6c504b'
down_revision = 'e4548ac57c34'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('start_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('show', 'start_time')
    # ### end Alembic commands ###
