"""update score type

Revision ID: 93e0046e75b6
Revises: 35c6166b2db0
Create Date: 2025-03-29 17:06:32.299897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93e0046e75b6'
down_revision: Union[str, None] = '35c6166b2db0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('submissions', 'score',
               existing_type=sa.REAL(),
               type_=sa.Numeric(precision=3, scale=2),
               existing_nullable=False)
    op.alter_column('submitted_answers', 'score',
               existing_type=sa.REAL(),
               type_=sa.Numeric(precision=3, scale=2),
               existing_nullable=False)
    op.alter_column('test_answers', 'score',
               existing_type=sa.REAL(),
               type_=sa.Numeric(precision=3, scale=2),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('test_answers', 'score',
               existing_type=sa.Numeric(precision=3, scale=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('submitted_answers', 'score',
               existing_type=sa.Numeric(precision=3, scale=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('submissions', 'score',
               existing_type=sa.Numeric(precision=3, scale=2),
               type_=sa.REAL(),
               existing_nullable=False)
    # ### end Alembic commands ###
