import os
import json
import requests
from datetime import datetime
from google.cloud import storage
from dotenv import load_dotenv
load_dotenv()

def get_pluggy_api_key(client_id, client_secret):
    """Autentica na Pluggy via Client ID e Secret e retorna a API Key."""
    url = "https://api.pluggy.ai/auth"
    payload = {"clientId": client_id, "clientSecret": client_secret}
    headers = {"accept": "application/json", "content-type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json().get("apiKey")

def fetch_pluggy_endpoint(endpoint, api_key):
    """Busca dados nos endpoints da Pluggy."""
    url = f"https://api.pluggy.ai/{endpoint}"
    headers = {"accept": "application/json", "X-API-KEY": api_key}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("results", [])

def upload_to_gcs(bucket_name, destination_blob_name, data):
    """Faz o upload de um dicionário (JSON) para o Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    blob.upload_from_string(json_data, content_type='application/json')
    print(f"Sucesso: Arquivo salvo em gs://{bucket_name}/{destination_blob_name}")


def cloud_run_handler(request=None):
    client_id = os.environ.get("PLUGGY_CLIENT_ID", "SEU_CLIENT_ID_AQUI")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET", "SEU_CLIENT_SECRET_AQUI")
    bucket_name = os.environ.get("GCS_BUCKET_NAME", "nome-do-seu-bucket-aqui")
    
    try:
        print("Gerando token JWT...")
        api_key = get_pluggy_api_key(client_id, client_secret)
        
        print("Extraindo categorias e transações...")
        categories_raw = fetch_pluggy_endpoint("categories", api_key)
        transactions_raw = fetch_pluggy_endpoint("v2/transactions", api_key)
        
        category_map = {
            cat["id"]: cat.get("descriptionTranslated", cat.get("description")) 
            for cat in categories_raw
        }
        
        cleaned_transactions = []
        for t in transactions_raw:
            cleaned_transactions.append({
                "transaction_id": t.get("id"),
                "date": t.get("date"),
                "description": t.get("description"),
                "amount": t.get("amount"),
                "type": t.get("type"),
                "category_id": t.get("categoryId"),
                "category_name": category_map.get(t.get("categoryId"), "Não Categorizado")
            })
            
        print(f"{len(cleaned_transactions)} transações processadas.")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"pluggy_transactions/extracao_{timestamp}.json"
        upload_to_gcs(bucket_name, file_name, cleaned_transactions)
        
        return {
            "status": "success", 
            "extracted_records": len(cleaned_transactions),
            "file_path": f"gs://{bucket_name}/{file_name}"
        }, 200
        
    except Exception as e:
        print(f"Erro na execução: {e}")
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    cloud_run_handler()