"""update_uniqueness_of_alt_uuid

Revision ID: bec34208dd87
Revises: fe8c0d015ba2
Create Date: 2024-04-04 08:13:39.761670

"""
from os import name
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bec34208dd87'
down_revision: Union[str, None] = 'fe8c0d015ba2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'datasets_temp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.Uuid(), nullable=False),
        sa.Column('alt_uid', sa.String(), nullable=True),
        sa.Column('collected', sa.TIMESTAMP(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('scope_id', sa.Integer(), nullable=False),
        sa.Column('creator', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=False),
        sa.Column('search_helper', sa.String(), nullable=False),
        sa.Column('ranking', sa.Integer(), nullable=False),
        sa.Column('synchronized', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['scope_id'], ['scopes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid', name='datasets_uuid_unique'),
        sa.UniqueConstraint('alt_uid', 'scope_id', name='datasets_alt_uid_scope_id_unique')
    )
    
    op.create_index(op.f('idx_datasets_alt_uid'), 'datasets_temp', ['alt_uid'], unique=False)
    op.create_index(op.f('idx_datasets_scope_id'), 'datasets_temp', ['scope_id'], unique=False)
    op.create_index(op.f('idx_datasets_uuid'), 'datasets_temp', ['uuid'], unique=False)
    op.execute('DROP INDEX IF EXISTS ix_datasets_alt_uid;')
    op.execute('DROP INDEX IF EXISTS ix_datasets_scope_id;')
    op.execute('DROP INDEX IF EXISTS ix_datasets_uuid;')

    op.execute("INSERT INTO datasets_temp  (id, uuid, alt_uid, collected, created, modified, name, scope_id, creator, description, keywords, search_helper, ranking, synchronized, notes)\
 SELECT id, uuid, alt_uid, collected, created, modified, name, scope_id, creator, description, keywords, search_helper, ranking, synchronized, notes FROM datasets;")
 
    op.drop_table('datasets')
    op.execute("ALTER TABLE datasets_temp RENAME TO datasets;")


def downgrade() -> None:
    op.create_table('datasets_temp',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.Uuid(), nullable=False),
    sa.Column('alt_uid', sa.String(), nullable=True),
    sa.Column('collected', sa.TIMESTAMP(), nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('modified', sa.DateTime(timezone=True), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('scope_id', sa.Integer(), nullable=False),
    sa.Column('creator', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('keywords', sa.JSON(), nullable=False),
    sa.Column('search_helper', sa.String(), nullable=False),
    sa.Column('ranking', sa.Integer(), nullable=False),
    sa.Column('synchronized', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['scope_id'], ['scopes.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uuid', 'alt_uid'))
    op.create_index(op.f('ix_datasets_alt_uid'), 'datasets_temp', ['alt_uid'], unique=False)
    op.create_index(op.f('ix_datasets_scope_id'), 'datasets_temp', ['scope_id'], unique=False)
    op.create_index(op.f('ix_datasets_uuid'), 'datasets_temp', ['uuid'], unique=False)

    op.execute("INSERT INTO datasets_temp  (id, uuid, alt_uid, collected, created, modified, name, scope_id, creator, description, keywords, search_helper, ranking, synchronized, notes)\
 SELECT id, uuid, alt_uid, collected, created, modified, name, scope_id, creator, description, keywords, search_helper, ranking, synchronized, notes FROM datasets;")

    op.drop_index('idx_datasets_alt_uid', table_name='datasets')
    op.drop_index('idx_datasets_scope_id', table_name='datasets')
    op.drop_index('idx_datasets_uuid', table_name='datasets')
    op.drop_table('datasets')
    op.execute("ALTER TABLE datasets_temp RENAME TO datasets;")
