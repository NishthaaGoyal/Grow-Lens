"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-04 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # 2. watchlists table
    op.create_table(
        'watchlists',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_watchlists_user_id', 'watchlists', ['user_id'], unique=False)

    # 3. watchlist_items table
    op.create_table(
        'watchlist_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('watchlist_id', sa.UUID(), nullable=False),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['watchlist_id'], ['watchlists.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('watchlist_id', 'symbol', name='uq_watchlist_symbol')
    )
    op.create_index('idx_watchlist_items_watchlist_id', 'watchlist_items', ['watchlist_id'], unique=False)
    op.create_index('idx_watchlist_items_symbol', 'watchlist_items', ['symbol'], unique=False)

    # 4. snapshots table
    op.create_table(
        'snapshots',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('snapshot_time', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('trigger_type', sa.String(length=50), server_default='manual', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_snapshots_user_id', 'snapshots', ['user_id'], unique=False)
    op.create_index('idx_snapshots_snapshot_time', 'snapshots', ['snapshot_time'], unique=False)

    # 5. snapshot_items table
    op.create_table(
        'snapshot_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('snapshot_id', sa.UUID(), nullable=False),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('price', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('daily_change', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('daily_change_abs', sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column('volume', sa.BigInteger(), nullable=False),
        sa.Column('avg_volume', sa.BigInteger(), nullable=True),
        sa.Column('market_cap', sa.BigInteger(), nullable=True),
        sa.Column('high_52w', sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column('low_52w', sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['snapshot_id'], ['snapshots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_snapshot_items_snapshot_id', 'snapshot_items', ['snapshot_id'], unique=False)
    op.create_index('idx_snapshot_items_symbol', 'snapshot_items', ['symbol'], unique=False)

    # 6. events table
    op.create_table(
        'events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('impact_score', sa.Integer(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('price_change', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('volume_ratio', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.CheckConstraint('impact_score >= 0 AND impact_score <= 100', name='chk_impact_score_range'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_events_user_id', 'events', ['user_id'], unique=False)
    op.create_index('idx_events_symbol', 'events', ['symbol'], unique=False)
    op.create_index('idx_events_impact_score', 'events', ['impact_score'], unique=False)
    op.create_index('idx_events_created_at', 'events', ['created_at'], unique=False)

    # 7. market_pulse table
    op.create_table(
        'market_pulse',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('pulse_date', sa.Date(), nullable=False),
        sa.Column('market_mood', sa.String(length=50), nullable=True),
        sa.Column('strongest_sector', sa.String(length=100), nullable=True),
        sa.Column('weakest_sector', sa.String(length=100), nullable=True),
        sa.Column('top_theme', sa.String(length=255), nullable=True),
        sa.Column('global_sentiment', sa.String(length=50), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('ai_narrative', sa.Text(), nullable=True),
        sa.Column('raw_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('pulse_date')
    )

    # 8. news_cache table
    op.create_table(
        'news_cache',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('symbol', sa.String(length=50), nullable=True),
        sa.Column('headline', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.Column('sentiment_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_news_cache_symbol', 'news_cache', ['symbol'], unique=False)
    op.create_index('idx_news_cache_published_at', 'news_cache', ['published_at'], unique=False)


def downgrade() -> None:
    op.drop_table('news_cache')
    op.drop_table('market_pulse')
    op.drop_table('events')
    op.drop_table('snapshot_items')
    op.drop_table('snapshots')
    op.drop_table('watchlist_items')
    op.drop_table('watchlists')
    op.drop_table('users')
