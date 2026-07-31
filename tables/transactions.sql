CREATE TABLE `personal-finance-bd.personal_finance_dw.transactions` (
    transaction_id STRING OPTIONS(description="ID único da transação"),
    item_id STRING OPTIONS(description="ID do item/conexão bancária"),
    account_id STRING OPTIONS(description="ID da conta bancária"),
    bank_name STRING OPTIONS(description="Nome da instituição financeira"),
    date TIMESTAMP OPTIONS(description="Data em que ocorreu a transação"),
    description STRING OPTIONS(description="Descrição original da transação"),
    amount FLOAT64 OPTIONS(description="Valor monetário da transação"),
    type STRING OPTIONS(description="Tipo da transação (CREDIT ou DEBIT)"),
    category_id STRING OPTIONS(description="ID da categoria associada"),
    category_name STRING OPTIONS(description="Nome amigável da categoria")
);