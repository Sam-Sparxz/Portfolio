"""create contact_messages table

Revision ID: 0001_create_contact_messages_table
Revises: 
Create Date: 2026-02-22 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_contact_messages_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'contact_messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('subject', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.String(length=64), nullable=False),
    )


def downgrade():
    op.drop_table('contact_messages')
