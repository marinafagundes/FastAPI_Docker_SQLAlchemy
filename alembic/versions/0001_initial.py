"""Cria as tabelas iniciais do projeto."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "fornecedor_cliente",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "contas_a_pagar_e_receber",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("descricao", sa.String(length=30), nullable=False),
        sa.Column("valor", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("tipo", sa.String(length=10), nullable=False),
        sa.Column("data_previsao", sa.Date(), nullable=False),
        sa.Column("data_baixa", sa.Date(), nullable=True),
        sa.Column("valor_baixa", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("esta_baixada", sa.Boolean(), nullable=False),
        sa.Column("fornecedor_cliente_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["fornecedor_cliente_id"], ["fornecedor_cliente.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

def downgrade() -> None:
    op.drop_table("contas_a_pagar_e_receber")
    op.drop_table("fornecedor_cliente")
