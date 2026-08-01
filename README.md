Personal Finance ETL Pipeline: Pluggy API to BigQuery
📌 Overview

This repository contains a production-grade, modular ETL (Extract, Transform, Load) pipeline built on Google Cloud Platform (GCP). It automatically extracts personal finance data (transactions, investments, and categories) from the Pluggy API, stages it in Google Cloud Storage (GCS), and loads it into a BigQuery Data Warehouse for analytics and dashboarding.

To ensure high reliability and scalability, the architecture is strictly decoupled into two separate containerized applications: an Extractor and a Loader, both orchestrated via Google Cloud Run Jobs.
🏗️ Architecture & Technologies

Cloud Provider: Google Cloud Platform (GCP)
Language: Python 3.9+
Containerization: Docker
Core Services Used:

    Pluggy API: Source of financial data (Open Finance).

    Google Cloud Storage (GCS): Acts as the Data Lake for raw and processed data staging.

    Google BigQuery: The ultimate Data Warehouse (personal_finance_dw).

    Google Cloud Run Jobs: Serverless compute environment executing the containerized scripts.

    Google Artifact Registry / Cloud Build: CI/CD for building and storing Docker images.

🚀 Pipeline Workflow (Data Flow)

The ETL follows a structured "Medallion-style" workflow to prevent data loss and ensure data integrity.
1. Extraction (Job 1)

    Script: extractor.py (built with Dockerfile)

    Action: Authenticates with the Pluggy API and fetches accounts, transactions, investments, and categories.

    Transformation: Flattens nested JSON structures (e.g., payment metadata) and resolves translated category names.

    Storage: Converts the payload into Newline-Delimited JSON (NDJSON) and uploads it to GCS under pluggy_transactions/ and pluggy_investments/ prefixes.

2. Loading (Job 2)

    Script: load_to_bigquery.py (built with Dockerfile.loader)

    Action: Scans the GCS bucket for new NDJSON files.

    Validation: Applies strict, hardcoded schemas (disabling BigQuery's autodetect) to prevent type conflicts (e.g., handling Pluggy's rate or categoryId type variations).

    Ingestion: Appends the data into the respective BigQuery tables (transactions, investments, categories).

    Archival: Upon successful BigQuery ingestion, moves the processed files to a processed/ directory within GCS to prevent duplicate runs.

📁 Repository Structure
Plaintext

.
├── extractor.py           # Logic for API extraction and GCS upload
├── load_to_bigquery.py    # Logic for GCS reading and BigQuery ingestion
├── requirements.txt       # Python dependencies (google-cloud-storage, google-cloud-bigquery, requests)
├── Dockerfile             # Container definition for the Extractor Job
└── Dockerfile.loader      # Container definition for the Loader Job

⚙️ Environment Variables

Both Cloud Run Jobs require specific environment variables to function correctly.

For the Extractor Job:

    PLUGGY_CLIENT_ID: Your Pluggy API Client ID.

    PLUGGY_CLIENT_SECRET: Your Pluggy API Client Secret.

    GCS_BUCKET_NAME: The name of the GCS bucket for staging data.

For the Loader Job:

    GCP_PROJECT_ID: Your Google Cloud Project ID.

    GCS_BUCKET_NAME: The name of the GCS bucket where data is staged.

📊 BigQuery Schemas

To ensure pipeline resilience, this project strictly defines BigQuery schemas in the Loader script. This handles edge cases where the API might return an integer (100) or a float (100.5) for rates, or strings for IDs.

    Transactions Table: Captures full transactional data, including raw descriptions, categorical mapping, operation types, and nested payment metadata.

    Investments Table: Captures asset names, subtypes, balances, currencies, and precise rates (forced to FLOAT64).

🛠️ Deployment

    Build the Extractor Image:
    Submit the build to Artifact Registry using the standard Dockerfile.

    Build the Loader Image:
    Submit the build using Dockerfile.loader.

    Deploy to Cloud Run Jobs:
    Create two distinct Cloud Run Jobs, each pointing to its respective image and injected with the necessary Environment Variables.

    Triggering:
    Jobs can be executed manually via the GCP Console or scheduled via Google Cloud Scheduler.