"""Initial tables

Revision ID: e748549d8d91
Revises: 
Create Date: 2023-01-12 19:21:58.431417

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e748549d8d91'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.engine.name == 'sqlite':
        binary_type = sa.BLOB()
        json_type = sa.JSON()
    else:
        from sqlalchemy.dialects.postgresql import BYTEA, JSONB
        binary_type = BYTEA()
        json_type = JSONB()

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth',
    sa.Column('pubkey', sa.Text(), nullable=False),
    sa.Column('roles', sa.Text(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('pubkey')
    )
    op.create_table('events',
    sa.Column('id', binary_type, nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=True),
    sa.Column('kind', sa.Integer(), nullable=True),
    sa.Column('pubkey', binary_type, nullable=True),
    sa.Column('tags', json_type, nullable=True),
    sa.Column('sig', binary_type, nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('cidx', 'events', ['created_at'], unique=False)
    op.create_index('kidx', 'events', ['kind'], unique=False)
    op.create_index('pkidx', 'events', ['pubkey'], unique=False)
    op.create_table('identity',
    sa.Column('identifier', sa.Text(), nullable=False),
    sa.Column('pubkey', sa.Text(), nullable=True),
    sa.Column('relays', json_type, nullable=True),
    sa.PrimaryKeyConstraint('identifier')
    )
    op.create_table('tag',
    sa.Column('id', binary_type, nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('value', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['events.id'], ondelete='CASCADE'),
    sa.UniqueConstraint('id', 'name', 'value', name='unique_tag')
    )
    op.create_index('tag_idx', 'tag', ['name', 'value'], unique=False)
    op.create_table('verification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('identifier', sa.Text(), nullable=True),
    sa.Column('metadata_id', binary_type, nullable=True),
    sa.Column('verified_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('failed_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['metadata_id'], ['events.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('identifieridx', 'verification', ['identifier'], unique=False)
    op.create_index('metadataidx', 'verification', ['metadata_id'], unique=False)
    op.create_index('verifiedidx', 'verification', ['verified_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('verifiedidx', table_name='verification')
    op.drop_index('metadataidx', table_name='verification')
    op.drop_index('identifieridx', table_name='verification')
    op.drop_table('verification')
    op.drop_index('tag_idx', table_name='tag')
    op.drop_table('tag')
    op.drop_table('identity')
    op.drop_index('pkidx', table_name='events')
    op.drop_index('kidx', table_name='events')
    op.drop_index('cidx', table_name='events')
    op.drop_table('events')
    op.drop_table('auth')
    # ### end Alembic commands ###
