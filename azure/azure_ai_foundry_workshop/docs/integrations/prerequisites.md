# Azure Prerequisites 🚀

Before starting with Azure AI Foundry, ensure you have the following resources and configurations:

## Required Azure Resources

### 1. Azure AI Foundry Project 【†L1】
1. [Create an AI Foundry project](https://learn.microsoft.com/azure/ai-foundry/get-started):
   ```bash
   az login
   az account set --subscription <subscription-id>
   az group create --name myResourceGroup --location eastus
   az ai project create --name myProject --resource-group myResourceGroup
   ```
2. Configure project settings:
   - Enable AI services
   - Set up resource providers
   - Configure networking
3. Set up Azure AD authentication:
   - Add `Azure AI Developer` role
   - Configure service principal
   - Set up identity management

### 2. Azure AI Search 【†L4】
1. [Create an Azure AI Search service](https://learn.microsoft.com/azure/search/search-create-service-portal):
   ```bash
   az search service create \
     --name myaisearch \
     --resource-group myResourceGroup \
     --sku Standard \
     --location eastus
   ```
2. Enable vector search capabilities:
   - Navigate to your search service in Azure Portal
   - Under "Settings" > "Vector search", enable vector search
   - Choose appropriate vector configuration

3. Configure access:
   ```bash
   # Get admin key
   az search admin-key show \
     --resource-group myResourceGroup \
     --service-name myaisearch
   
   # Create query key
   az search query-key create \
     --resource-group myResourceGroup \
     --service-name myaisearch \
     --name myquerykey
   ```

4. Add to environment variables:
   ```bash
   AZURE_SEARCH_SERVICE_ENDPOINT="https://myaisearch.search.windows.net"
   AZURE_SEARCH_ADMIN_KEY="your-admin-key"
   AZURE_SEARCH_INDEX_NAME="your-index-name"
   ```

### 3. Azure Cosmos DB 【†L5】
1. [Create a Cosmos DB account](https://learn.microsoft.com/azure/cosmos-db/nosql/quickstart-portal):
   ```bash
   az cosmosdb create \
     --name mycosmosdb \
     --resource-group myResourceGroup \
     --kind GlobalDocumentDB \
     --locations regionName=eastus
   ```

2. Create a database and container:
   ```bash
   az cosmosdb sql database create \
     --account-name mycosmosdb \
     --resource-group myResourceGroup \
     --name mydb

   az cosmosdb sql container create \
     --account-name mycosmosdb \
     --resource-group myResourceGroup \
     --database-name mydb \
     --name mycontainer \
     --partition-key-path "/id"
   ```

3. Enable vector search:
   - Navigate to your Cosmos DB account
   - Under "Settings" > "Vector search", enable the feature
   - Configure vector index settings

4. Get connection string:
   ```bash
   az cosmosdb keys list \
     --name mycosmosdb \
     --resource-group myResourceGroup \
     --type connection-strings
   ```

5. Add to environment variables:
   ```bash
   AZURE_COSMOS_CONNECTION_STRING="your-connection-string"
   AZURE_COSMOS_DATABASE_NAME="mydb"
   AZURE_COSMOS_CONTAINER_NAME="mycontainer"
   ```

### 4. Azure Database for PostgreSQL 【†L6】
1. [Deploy PostgreSQL Flexible Server](https://learn.microsoft.com/azure/postgresql/flexible-server/quickstart-create-server-portal):
   ```bash
   az postgres flexible-server create \
     --name mypgserver \
     --resource-group myResourceGroup \
     --location eastus \
     --admin-user myadmin \
     --admin-password "your-password" \
     --sku-name Standard_B2s
   ```

2. Enable pgvector extension:
   ```bash
   az postgres flexible-server parameter set \
     --resource-group myResourceGroup \
     --server-name mypgserver \
     --name azure.extensions \
     --value vector

   # Connect to your server and create extension
   psql "host=mypgserver.postgres.database.azure.com \
     port=5432 dbname=postgres \
     user=myadmin password=your-password" \
     -c "CREATE EXTENSION vector;"
   ```

3. Create database and configure access:
   ```bash
   az postgres flexible-server db create \
     --resource-group myResourceGroup \
     --server-name mypgserver \
     --database-name mydb

   # Allow your IP
   az postgres flexible-server firewall-rule create \
     --name myip \
     --resource-group myResourceGroup \
     --server-name mypgserver \
     --start-ip-address your-ip \
     --end-ip-address your-ip
   ```

4. Add to environment variables:
   ```bash
   AZURE_POSTGRES_CONNECTION_STRING="postgresql://myadmin:your-password@mypgserver.postgres.database.azure.com:5432/mydb"
   AZURE_POSTGRES_SERVER_NAME="mypgserver"
   AZURE_POSTGRES_DATABASE_NAME="mydb"
   ```

### 5. Azure API Management 【†L7】
1. [Create an APIM instance](https://learn.microsoft.com/azure/api-management/get-started-create-service-instance):
   ```bash
   az apim create \
     --name myapim \
     --resource-group myResourceGroup \
     --location eastus \
     --publisher-name "Your Company" \
     --publisher-email "your-email@domain.com" \
     --sku-name Developer
   ```

2. Configure AI endpoints:
   ```bash
   # Import OpenAPI specification
   az apim api import \
     --resource-group myResourceGroup \
     --service-name myapim \
     --api-id myai \
     --specification-format OpenApi \
     --specification-path ./openapi.json

   # Set up named values for keys
   az apim nv create \
     --resource-group myResourceGroup \
     --service-name myapim \
     --named-value-id AiKey \
     --display-name "AI API Key" \
     --value "your-key" \
     --secret true
   ```

3. Configure security policies:
   ```xml
   <!-- Add to your API's policy -->
   <policies>
     <inbound>
       <base />
       <set-header name="Ocp-Apim-Subscription-Key" exists-action="override">
         <value>{{AiKey}}</value>
       </set-header>
       <rate-limit calls="100" renewal-period="60" />
     </inbound>
   </policies>
   ```

4. Add to environment variables:
   ```bash
   AZURE_APIM_ENDPOINT="https://myapim.azure-api.net"
   AZURE_APIM_KEY="your-subscription-key"
   ```

### 6. Azure Logic Apps 【†L8】
1. [Create a Logic App](https://learn.microsoft.com/azure/logic-apps/quickstart-create-first-logic-app-workflow):
   ```bash
   az logic workflow create \
     --resource-group myResourceGroup \
     --location eastus \
     --name mylogicapp \
     --definition @workflow.json
   ```

2. Configure AI workflow connections:
   ```bash
   # Create API connection
   az logic workflow connection create \
     --resource-group myResourceGroup \
     --workflow-name mylogicapp \
     --connection-name myaiconnection \
     --api-id "/subscriptions/{subscription-id}/providers/Microsoft.Web/locations/eastus/managedApis/azureai"
   ```

3. Set up event triggers:
   - Create an Event Hub trigger
   - Configure AI processing actions
   - Set up response handling

4. Add to environment variables:
   ```bash
   AZURE_LOGIC_APP_NAME="mylogicapp"
   AZURE_LOGIC_APP_ENDPOINT="https://mylogicapp.azurewebsites.net"
   ```

### 7. Azure Functions 【†L9】
1. [Create a Function App](https://learn.microsoft.com/azure/azure-functions/functions-create-first-function-vs-code):
   ```bash
   az functionapp create \
     --resource-group myResourceGroup \
     --consumption-plan-location eastus \
     --runtime python \
     --runtime-version 3.9 \
     --functions-version 4 \
     --name myfuncapp \
     --os-type linux \
     --storage-account mystorageaccount
   ```

2. Configure application settings:
   ```bash
   # Set required environment variables
   az functionapp config appsettings set \
     --resource-group myResourceGroup \
     --name myfuncapp \
     --settings \
     PROJECT_CONNECTION_STRING="your-connection-string" \
     MODEL_DEPLOYMENT_NAME="your-model-name" \
     AZURE_OPENAI_ENDPOINT="your-endpoint"
   ```

3. Deploy your function:
   ```bash
   # Using Azure Functions Core Tools
   func azure functionapp publish myfuncapp
   ```

4. Add to environment variables:
   ```bash
   AZURE_FUNCTION_APP_NAME="myfuncapp"
   AZURE_FUNCTION_KEY="your-function-key"
   ```

## Environment Variables

The following environment variables are required for running the workshop samples. Create a `.env` file in your project root. Make sure to replace the placeholder values with your actual configuration:

### Quick Setup
```bash
# Download example environment file
curl -O https://raw.githubusercontent.com/Azure/ai-foundry-workshop/main/.env.example
# Copy to .env
cp .env.example .env
# Edit with your values
nano .env
```

### Required Variables
```bash
# Core Configuration (Required)
PROJECT_CONNECTION_STRING=     # Format: {region}.api.azureml.ms;{subscription_id};{resource_group};{workspace}
MODEL_DEPLOYMENT_NAME=         # Example: gpt-4o
EMBEDDING_MODEL_DEPLOYMENT_NAME= # Example: text-embedding-3-small
SERVERLESS_MODEL_NAME=         # Your serverless model name

# Integration Settings (Required)
BING_CONNECTION_NAME=         # Your Bing search connection name
AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true  # Enable telemetry
AZURE_SDK_TRACING_IMPLEMENTATION=opentelemetry       # Set tracing implementation

# Optional Settings
TENANT_ID=                    # Your Azure AD tenant ID
DEBUG=false                   # Enable debug mode
LOG_LEVEL=info               # Logging level (debug/info/warn/error)
```

> **Note**: The model specified in `MODEL_DEPLOYMENT_NAME` must be supported by Azure AI Agents Service. See [supported models](https://learn.microsoft.com/azure/ai-services/agents/concepts/model-region-support) for details.

```bash
# Project Configuration
PROJECT_CONNECTION_STRING=     # Azure AI Foundry project connection string
MODEL_DEPLOYMENT_NAME=         # Primary model deployment name
EMBEDDING_MODEL_DEPLOYMENT_NAME= # Embedding model deployment name
SERVERLESS_MODEL_NAME=         # Serverless model name

# Integration Settings
BING_CONNECTION_NAME=         # Bing grounding tool connection
AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true  # Enable telemetry
AZURE_SDK_TRACING_IMPLEMENTATION=opentelemetry       # Set tracing implementation
```

## Authentication Setup

1. Install Azure CLI:
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

2. Login to Azure:
```bash
az login
```

3. Set subscription:
```bash
az account set --subscription <subscription-id>
```

For detailed setup instructions, see the [Azure AI Foundry documentation](https://learn.microsoft.com/azure/ai-foundry/get-started).
