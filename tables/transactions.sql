DROP TABLE IF EXISTS `personal-finance-bd.personal_finance_dw.transactions`;

CREATE TABLE `personal-finance-bd.personal_finance_dw.transactions` (
    transaction_id STRING OPTIONS(description="ID único da transação"),
    item_id STRING OPTIONS(description="ID do item/conexão bancária"),
    account_id STRING OPTIONS(description="ID da conta bancária"),
    bank_name STRING OPTIONS(description="Nome da instituição financeira"),
    date TIMESTAMP OPTIONS(description="Data em que ocorreu a transação"),
    description STRING OPTIONS(description="Descrição da transação"),
    description_raw STRING OPTIONS(description="Descrição original crua da transação"),
    amount FLOAT64 OPTIONS(description="Valor monetário da transação"),
    amount_in_account_currency FLOAT64 OPTIONS(description="Valor na moeda da conta, se aplicável"),
    currency_code STRING OPTIONS(description="Código da moeda (ex: BRL)"),
    type STRING OPTIONS(description="Tipo da transação (CREDIT ou DEBIT)"),
    operation_type STRING OPTIONS(description="Tipo de operação (ex: CARTAO, PIX, etc)"),
    operation_type_additional_info STRING OPTIONS(description="Informação adicional da operação"),
    category_id STRING OPTIONS(description="ID da categoria associada"),
    category_name STRING OPTIONS(description="Nome amigável da categoria"),
    status STRING OPTIONS(description="Status da transação (ex: POSTED)"),
    balance FLOAT64 OPTIONS(description="Saldo da conta após a transação, se disponível"),
    provider_code STRING OPTIONS(description="Código do provedor"),
    provider_id STRING OPTIONS(description="ID do provedor"),
    order_index INT64 OPTIONS(description="Ordem da transação"),
    
    payment_method STRING OPTIONS(description="Método de pagamento"),
    payment_reason STRING OPTIONS(description="Motivo do pagamento"),
    payer_document_type STRING OPTIONS(description="Tipo de documento do pagador"),
    payer_document_value STRING OPTIONS(description="Número do documento do pagador"),
    
    created_at TIMESTAMP OPTIONS(description="Data de criação na origem"),
    updated_at TIMESTAMP OPTIONS(description="Data de atualização na origem")
);