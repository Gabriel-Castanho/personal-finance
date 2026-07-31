DROP TABLE IF EXISTS `personal-finance-bd.personal_finance_dw.investments`;

CREATE TABLE `personal-finance-bd.personal_finance_dw.investments` (
    investment_id STRING OPTIONS(description="ID único do ativo de investimento"),
    item_id STRING OPTIONS(description="ID do item/conexão bancária"),
    name STRING OPTIONS(description="Nome do ativo ou produto financeiro"),
    type STRING OPTIONS(description="Tipo principal do investimento"),
    sub_type STRING OPTIONS(description="Subtipo do investimento"),
    balance FLOAT64 OPTIONS(description="Saldo/Valor atual investido"),
    currency_code STRING OPTIONS(description="Moeda do ativo"),
    due_date TIMESTAMP OPTIONS(description="Data de vencimento"),
    rate FLOAT64 OPTIONS(description="Taxa de rendimento")
);