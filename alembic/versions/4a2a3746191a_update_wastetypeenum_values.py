"""update wastetypeenum values

Revision ID: 4a2a3746191a
Revises: 25cdef2621bc
Create Date: 2024-03-19 12:34:56.789012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4a2a3746191a'
down_revision: Union[str, None] = '25cdef2621bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a new enum type with all values
    op.execute("ALTER TYPE wastetypeenum RENAME TO wastetypeenum_old")
    op.execute("CREATE TYPE wastetypeenum AS ENUM ('PLASTIC', 'ORGANIC', 'ELECTRONIC', 'HAZARDOUS', 'GENERAL')")
    
    # Update the columns to use the new enum type
    op.execute("ALTER TABLE collector_profiles ALTER COLUMN waste_types TYPE wastetypeenum[] USING waste_types::text[]::wastetypeenum[]")
    op.execute("ALTER TABLE illegal_dump_reports ALTER COLUMN waste_type TYPE wastetypeenum USING waste_type::text::wastetypeenum")
    op.execute("ALTER TABLE collector_profiles_legacy ALTER COLUMN accepted_waste_types TYPE wastetypeenum[] USING accepted_waste_types::text[]::wastetypeenum[]")
    
    # Drop the old enum type with CASCADE to handle any remaining dependencies
    op.execute("DROP TYPE wastetypeenum_old CASCADE")


def downgrade() -> None:
    # Create the old enum type
    op.execute("ALTER TYPE wastetypeenum RENAME TO wastetypeenum_new")
    op.execute("CREATE TYPE wastetypeenum AS ENUM ('PLASTIC', 'ELECTRONIC', 'ORGANIC')")
    
    # Update the columns to use the old enum type
    op.execute("ALTER TABLE collector_profiles ALTER COLUMN waste_types TYPE wastetypeenum[] USING waste_types::text[]::wastetypeenum[]")
    op.execute("ALTER TABLE illegal_dump_reports ALTER COLUMN waste_type TYPE wastetypeenum USING waste_type::text::wastetypeenum")
    op.execute("ALTER TABLE collector_profiles_legacy ALTER COLUMN accepted_waste_types TYPE wastetypeenum[] USING accepted_waste_types::text[]::wastetypeenum[]")
    
    # Drop the new enum type with CASCADE to handle any remaining dependencies
    op.execute("DROP TYPE wastetypeenum_new CASCADE")
