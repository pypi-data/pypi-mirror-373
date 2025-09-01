"""adding delete cache table

Revision ID: 24b0115d4cc7
Revises: bec34208dd87
Create Date: 2024-04-16 20:24:07.507888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24b0115d4cc7'
down_revision: Union[str, None] = 'bec34208dd87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('file_delete_queue',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('local_path', sa.String(), nullable=False),
                    sa.Column('delete_after', sa.DateTime(timezone=True), nullable=False),
                    sa.PrimaryKeyConstraint('id') )


def downgrade() -> None:
    op.drop_table('file_delete_queue')
