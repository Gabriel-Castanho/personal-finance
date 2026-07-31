import os
import json
import requests
from datetime import datetime
from google.cloud import storage

def get_pluggy_api_key(client_id, client_secret):
    """Autentica na Pluggy via Client ID e Secret e retorna a API Key."""
    url = "https://api.pluggy.ai/auth"
    payload = {"clientId": client_id, "clientSecret": client_secret}
    headers = {"accept": "application/json", "content-type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json().get("apiKey")

def fetch_pluggy_endpoint(endpoint, api_key, params=None):
    """Busca dados nos endpoints da Pluggy aceitando parâmetros opcionais."""
    url = f"https://api.pluggy.ai/{endpoint}"
    headers = {"accept": "application/json", "X-API-KEY": api_key}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("results", [])

def upload_to_gcs(bucket_name, destination_blob_name, data):
    """Faz o upload de um dicionário (JSON) para o Google Cloud Storage de forma correta."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    blob.upload_from_string(json_data, content_type='application/json')
    print(f"Sucesso: Arquivo salvo em gs://{bucket_name}/{destination_blob_name}")

def cloud_run_handler(request=None):
    client_id = os.environ.get("PLUGGY_CLIENT_ID")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
    bucket_name = os.environ.get("GCS_BUCKET_NAME")
    
    item_ids = [
        "9d652dcf-2dc5-42f2-9f7b-4d8ef9fc0596",
        "fb5308bd-25ad-482f-a66f-3bb1ebf7ceae",
        "95598b3f-cf2c-4b32-9b03-3b5fecb35732"
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        print("Gerando token JWT...")
        api_key = get_pluggy_api_key(client_id, client_secret)
        
        print("Extraindo tabela de categorias...")
        categories_raw = fetch_pluggy_endpoint("categories", api_key)
        category_map = {
            cat["id"]: cat.get("descriptionTranslated", cat.get("description")) 
            for cat in categories_raw
        }
        
        all_cleaned_transactions = []
        all_cleaned_investments = []
        
        for item_id in item_ids:
            print(f"\n--- Processando Item ID: {item_id} ---")
            
            # 1. Transações
            try:
                accounts_raw = fetch_pluggy_endpoint("accounts", api_key, params={"itemId": item_id, "type": "BANK"})
                for account in accounts_raw:
                    account_id = account.get("id")
                    bank_name = account.get("bank", {}).get("name", "Banco Desconhecido")
                    print(f"Buscando transações da conta: {account_id} ({bank_name})")
                    
                    transactions_raw = fetch_pluggy_endpoint("v2/transactions", api_key, params={"accountId": account_id})
                    for t in transactions_raw:
                        all_cleaned_transactions.append({
                            "transaction_id": t.get("id"),
                            "item_id": item_id,
                            "account_id": account_id,
                            "bank_name": bank_name,
                            "date": t.get("date"),
                            "description": t.get("description"),
                            "amount": t.get("amount"),
                            "type": t.get("type"),
                            "category_id": t.get("categoryId"),
                            "category_name": category_map.get(t.get("categoryId"), "Não Categorizado")
                        })
            except Exception as e:
                print(f"Aviso: Erro ao puxar transações para o item {item_id}: {e}")

            # 2. Investimentos
            try:
                print(f"Buscando investimentos para o Item ID: {item_id}")
                investments_raw = fetch_pluggy_endpoint("investments", api_key, params={"itemId": item_id})
                
                for inv in investments_raw:
                    all_cleaned_investments.append({
                        "investment_id": inv.get("id"),
                        "item_id": item_id,
                        "name": inv.get("name"),
                        "type": inv.get("type"),
                        "sub_type": inv.get("subtype"),
                        "balance": inv.get("balance"),
                        "currency_code": inv.get("currencyCode"),
                        "due_date": inv.get("dueDate"),
                        "rate": inv.get("rate")
                    })
            except Exception as e:
                print(f"Aviso: Erro ao puxar investimentos para o item {item_id}: {e}")

        # Salvando no Cloud Storage
        if all_cleaned_transactions:
            trans_file_name = f"pluggy_transactions/transactions_{timestamp}.json"
            upload_to_gcs(bucket_name, trans_file_name, all_cleaned_transactions)
            
        if all_cleaned_investments:
            inv_file_name = f"pluggy_investments/investments_{timestamp}.json"
            upload_to_gcs(bucket_name, inv_file_name, all_cleaned_investments)
            
        print("\nProcesso de ETL concluído com sucesso!")
        return {"status": "success"}, 200
        
    except Exception as e:
        print(f"Erro crítico na execução: {e}")
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    cloud_run_handler()