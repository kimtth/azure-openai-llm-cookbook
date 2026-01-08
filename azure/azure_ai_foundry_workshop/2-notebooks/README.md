# Azure AI Foundry Workshop Notebooks

This directory contains Jupyter notebooks for hands-on exercises with Azure AI Foundry.

## Setup Instructions

1. **Python Environment Setup**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Azure Authentication**
   You'll need to set up the following environment variables:
   ```bash
   export AZURE_SUBSCRIPTION_ID='your-subscription-id'
   export AZURE_RESOURCE_GROUP='your-resource-group'
   export AZURE_TENANT_ID='your-tenant-id'
   export AZURE_CLIENT_ID='your-client-id'
   export AZURE_CLIENT_SECRET='your-client-secret'
   ```

3. **Running the Notebooks**
   ```bash
   jupyter notebook
   ```
   Then open `project_setup.ipynb` in your browser.

## Notebooks

- `project_setup.ipynb`: Learn how to create and configure an AI project using Azure AI Foundry
