"""add collector status

Revision ID: f88e4735e454
Revises: 4a2a3746191a
Create Date: 2024-03-19 13:45:56.789012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f88e4735e454'
down_revision: Union[str, None] = '4a2a3746191a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the collector status enum type if it doesn't exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    enums = [e['name'] for e in inspector.get_enums()]
    
    if 'collectorstatusenum' not in enums:
        op.execute("CREATE TYPE collectorstatusenum AS ENUM ('AVAILABLE', 'BUSY', 'OFFLINE')")
    
    # Add the status column to collector_profiles if it doesn't exist
    columns = [c['name'] for c in inspector.get_columns('collector_profiles')]
    if 'status' not in columns:
        op.add_column('collector_profiles',
            sa.Column('status', postgresql.ENUM('AVAILABLE', 'BUSY', 'OFFLINE', name='collectorstatusenum'), 
                     server_default='OFFLINE', nullable=False)
        )
        
        # Create an index on the status column
        op.create_index(op.f('ix_collector_profiles_status'), 'collector_profiles', ['status'], unique=False)


def downgrade() -> None:
    # Drop the index if it exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    indexes = [i['name'] for i in inspector.get_indexes('collector_profiles')]
    
    if 'ix_collector_profiles_status' in indexes:
        op.drop_index(op.f('ix_collector_profiles_status'), table_name='collector_profiles')
    
    # Drop the status column if it exists
    columns = [c['name'] for c in inspector.get_columns('collector_profiles')]
    if 'status' in columns:
        op.drop_column('collector_profiles', 'status')
    
    # Drop the enum type if it exists
    enums = [e['name'] for e in inspector.get_enums()]
    if 'collectorstatusenum' in enums:
        op.execute('DROP TYPE collectorstatusenum')
