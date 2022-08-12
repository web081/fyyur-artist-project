"""empty message

Revision ID: 1b821e233cde
Revises: 1872bc7e6467
Create Date: 2022-08-12 03:23:24.817749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b821e233cde'
down_revision = '1872bc7e6467'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('artist_genre_genre_id_fkey', 'artist_genre', type_='foreignkey')
    op.drop_column('artist_genre', 'genre_id')
    op.drop_constraint('venue_genre_genre_id_fkey', 'venue_genre', type_='foreignkey')
    op.drop_column('venue_genre', 'genre_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue_genre', sa.Column('genre_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('venue_genre_genre_id_fkey', 'venue_genre', 'genre', ['genre_id'], ['id'])
    op.add_column('artist_genre', sa.Column('genre_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('artist_genre_genre_id_fkey', 'artist_genre', 'genre', ['genre_id'], ['id'])
    # ### end Alembic commands ###
