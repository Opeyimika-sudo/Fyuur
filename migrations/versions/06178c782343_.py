"""empty message

Revision ID: 06178c782343
Revises: 
Create Date: 2022-08-20 01:53:51.686307

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06178c782343'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genres', sa.String(), nullable=True))
    op.add_column('venue', sa.Column('website', sa.String(), nullable=True))
    op.add_column('venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('venue', sa.Column('seeking_description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'seeking_description')
    op.drop_column('venue', 'seeking_talent')
    op.drop_column('venue', 'website')
    op.drop_column('venue', 'genres')
    # ### end Alembic commands ###
