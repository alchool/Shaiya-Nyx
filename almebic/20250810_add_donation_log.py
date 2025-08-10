# Salvalo nella cartella alembic/versions/ con un nome tipo: 20250810_add_donation_log.py
# (il prefisso numerico deve essere unico nella tua repo Alembic)


"""add Donation_Log table

Revision ID: 20250810_add_donation_log
Revises: <id_revision_precedente>
Create Date: 2025-08-10

"""
from alembic import op
import sqlalchemy as sa

# ID univoci Alembic
revision = '20250810_add_donation_log'
down_revision = '<id_revision_precedente>'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'Donation_Log',
        sa.Column('ID', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('UserUID', sa.Integer, nullable=False),
        sa.Column('UserID', sa.String(50), nullable=False),
        sa.Column('AmountUSD', sa.Numeric(10, 2), nullable=False),
        sa.Column('APGranted', sa.Integer, nullable=False),
        sa.Column('PayPalTxnID', sa.String(255), nullable=False),
        sa.Column('Status', sa.String(50), nullable=False),
        sa.Column('CreatedAt', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='dbo'
    )

def downgrade():
    op.drop_table('Donation_Log', schema='dbo')
