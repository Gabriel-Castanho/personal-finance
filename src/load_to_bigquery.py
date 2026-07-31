import os
from google.cloud import storage, bigquery

def bq_loader_handler(request=None):
    bucket_name = os.environ.get("GCS_BUCKET_NAME")
    project_id = os.environ.get("GCP_PROJECT_ID")
    dataset_id = "personal_finance_dw"
    
    storage_client = storage.Client()
    bq_client = bigquery.Client(project=project_id)
    
    bucket = storage_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs())
    
    files_processed = 0
    
    for blob in blobs:
        if "processed/" in blob.name or blob.name.endswith("/"):
            continue
            
        print(f"Processando arquivo para o BigQuery: {blob.name}")
        
        table_name = None
        schema_fields = None
        
        if "pluggy_transactions" in blob.name:
            table_name = "transactions"
            schema_fields = [
                bigquery.SchemaField("transaction_id", "STRING"),
                bigquery.SchemaField("item_id", "STRING"),
                bigquery.SchemaField("account_id", "STRING"),
                bigquery.SchemaField("bank_name", "STRING"),
                bigquery.SchemaField("date", "TIMESTAMP"),
                bigquery.SchemaField("description", "STRING"),
                bigquery.SchemaField("description_raw", "STRING"),
                bigquery.SchemaField("amount", "FLOAT64"),
                bigquery.SchemaField("amount_in_account_currency", "FLOAT64"),
                bigquery.SchemaField("currency_code", "STRING"),
                bigquery.SchemaField("type", "STRING"),
                bigquery.SchemaField("operation_type", "STRING"),
                bigquery.SchemaField("operation_type_additional_info", "STRING"),
                bigquery.SchemaField("category_id", "STRING"),
                bigquery.SchemaField("category_name", "STRING"),
                bigquery.SchemaField("status", "STRING"),
                bigquery.SchemaField("balance", "FLOAT64"),
                bigquery.SchemaField("provider_code", "STRING"),
                bigquery.SchemaField("provider_id", "STRING"),
                bigquery.SchemaField("order_index", "INT64"),
                bigquery.SchemaField("payment_method", "STRING"),
                bigquery.SchemaField("payment_reason", "STRING"),
                bigquery.SchemaField("payer_document_type", "STRING"),
                bigquery.SchemaField("payer_document_value", "STRING"),
                bigquery.SchemaField("created_at", "TIMESTAMP"),
                bigquery.SchemaField("updated_at", "TIMESTAMP"),
            ]
        elif "pluggy_investments" in blob.name:
            table_name = "investments"
            schema_fields = [
                bigquery.SchemaField("investment_id", "STRING"),
                bigquery.SchemaField("item_id", "STRING"),
                bigquery.SchemaField("name", "STRING"),
                bigquery.SchemaField("type", "STRING"),
                bigquery.SchemaField("sub_type", "STRING"),
                bigquery.SchemaField("balance", "FLOAT64"),
                bigquery.SchemaField("currency_code", "STRING"),
                bigquery.SchemaField("due_date", "TIMESTAMP"),
                bigquery.SchemaField("rate", "FLOAT64"),
            ]
        elif "pluggy_categories" in blob.name:
            table_name = "categories"
            schema_fields = [
                bigquery.SchemaField("category_id", "STRING"),
                bigquery.SchemaField("name", "STRING"),
                bigquery.SchemaField("parent_id", "STRING"),
            ]
        else:
            print(f"Pasta desconhecida para o arquivo {blob.name}, ignorando.")
            continue
            
        table_id = f"{project_id}.{dataset_id}.{table_name}"
        uri = f"gs://{bucket_name}/{blob.name}"
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            autodetect=False,
            schema=schema_fields
        )
        
        try:
            load_job = bq_client.load_table_from_uri(uri, table_id, job_config=job_config)
            load_job.result()
            print(f"Sucesso: Dados inseridos na tabela {table_id}")
            
            new_blob_name = blob.name.replace("pluggy_", "processed/pluggy_")
            bucket.copy_blob(blob, bucket, new_blob_name)
            blob.delete()
            print(f"Arquivo movido para: {new_blob_name}")
            
            files_processed += 1
            
        except Exception as e:
            print(f"Erro ao processar o arquivo {blob.name}: {e}")
            
    print(f"ETL Finalizado. Total de arquivos processados: {files_processed}")
    return {"status": "success", "files_processed": files_processed}, 200

if __name__ == "__main__":
    bq_loader_handler()