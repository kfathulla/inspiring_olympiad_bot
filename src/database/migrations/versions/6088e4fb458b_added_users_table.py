"""Added users table

Revision ID: 6088e4fb458b
Revises: 6de7aa44dc6b
Create Date: 2025-03-25 07:23:00.862433

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6088e4fb458b'
down_revision: Union[str, None] = '6de7aa44dc6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
