"""create marketplace listings

Revision ID: d6cbbdb3d57a
Revises: f88e4735e454
Create Date: 2024-03-19 14:15:56.789012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd6cbbdb3d57a'
down_revision: Union[str, None] = 'f88e4735e454'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the listing status enum type if it doesn't exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    enums = [e['name'] for e in inspector.get_enums()]
    
    if 'listingstatusenum' not in enums:
        op.execute("CREATE TYPE listingstatusenum AS ENUM ('AVAILABLE', 'RESERVED', 'SOLD', 'CANCELLED')")
    
    # Create the marketplace_listings table
    op.create_table(
        'marketplace_listings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resident_id', sa.Integer(), nullable=False),
        sa.Column('collector_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('waste_type', postgresql.ENUM('PLASTIC', 'ORGANIC', 'ELECTRONIC', 'HAZARDOUS', 'GENERAL', name='wastetypeenum', create_type=False), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('quantity', postgresql.ENUM('SMALL', 'MEDIUM', 'LARGE', name='quantityenum', create_type=False), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=False),
        sa.Column('status', postgresql.ENUM('AVAILABLE', 'RESERVED', 'SOLD', 'CANCELLED', name='listingstatusenum', create_type=False), nullable=False, server_default='AVAILABLE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('reserved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sold_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['collector_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['resident_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_marketplace_listings_id'), 'marketplace_listings', ['id'], unique=False)
    op.create_index(op.f('ix_marketplace_listings_resident_id'), 'marketplace_listings', ['resident_id'], unique=False)
    op.create_index(op.f('ix_marketplace_listings_collector_id'), 'marketplace_listings', ['collector_id'], unique=False)
    op.create_index(op.f('ix_marketplace_listings_waste_type'), 'marketplace_listings', ['waste_type'], unique=False)
    op.create_index(op.f('ix_marketplace_listings_location'), 'marketplace_listings', ['location'], unique=False)
    op.create_index(op.f('ix_marketplace_listings_status'), 'marketplace_listings', ['status'], unique=False)
    op.create_index(op.f('ix_marketplace_listings_created_at'), 'marketplace_listings', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_marketplace_listings_created_at'), table_name='marketplace_listings')
    op.drop_index(op.f('ix_marketplace_listings_status'), table_name='marketplace_listings')
    op.drop_index(op.f('ix_marketplace_listings_location'), table_name='marketplace_listings')
    op.drop_index(op.f('ix_marketplace_listings_waste_type'), table_name='marketplace_listings')
    op.drop_index(op.f('ix_marketplace_listings_collector_id'), table_name='marketplace_listings')
    op.drop_index(op.f('ix_marketplace_listings_resident_id'), table_name='marketplace_listings')
    op.drop_index(op.f('ix_marketplace_listings_id'), table_name='marketplace_listings')
    
    # Drop the table
    op.drop_table('marketplace_listings')
    
    # Drop the enum type if it exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    enums = [e['name'] for e in inspector.get_enums()]
    if 'listingstatusenum' in enums:
        op.execute('DROP TYPE listingstatusenum')
