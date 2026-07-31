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
        if "pluggy_transactions" in blob.name:
            table_name = "transactions"
        elif "pluggy_investments" in blob.name:
            table_name = "investments"
        elif "pluggy_categories" in blob.name:
            table_name = "categories"
        else:
            print(f"Pasta desconhecida para o arquivo {blob.name}, ignorando.")
            continue
            
        table_id = f"{project_id}.{dataset_id}.{table_name}"
        
        uri = f"gs://{bucket_name}/{blob.name}"
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True, 
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND 
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