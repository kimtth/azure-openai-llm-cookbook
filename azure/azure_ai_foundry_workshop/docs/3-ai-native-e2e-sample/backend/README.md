# Drug Development Platform Backend 🧬

## Overview 🎯
Backend for the Drug Development Platform, leveraging Azure AI Foundry SDKs for molecular analysis and clinical trial monitoring.

## Azure AI Integration 🤖

### SDKs Used
- 🎯 **azure-ai-projects**: Project and agent management
  ```python
  # main.py
  project_client = AIProjectClient.from_connection_string(
      credential=credential,
      conn_str=PROJECT_CONNECTION_STRING
  )
  ```

- 🔬 **azure-ai-inference**: Molecular analysis and predictions
  ```python
  # molecular_design.py
  inference_client = project_client.inference.get_chat_completions_client()
  ```

- 📊 **azure-ai-evaluation**: Result analysis and confidence scoring
  ```python
  # automated_testing.py
  evaluation = Evaluation(
      display_name="Drug Analysis Evaluation",
      description="Evaluation of drug analysis outputs",
      data=Dataset(id=data_id),
      evaluators={
          "f1_score": EvaluatorConfiguration(id=F1ScoreEvaluator.id),
          "relevance": EvaluatorConfiguration(id=RelevanceEvaluator.id)
      }
  )
  ```

- 📈 **opentelemetry-sdk**: Performance monitoring and tracing
  ```python
  # main.py
  trace.set_tracer_provider(TracerProvider())
  tracer = trace.get_tracer(__name__)
  ```

- 🔐 **azure-identity**: Secure Azure authentication
  ```python
  # main.py
  credential = DefaultAzureCredential()
  ```

## Getting Started 🚀

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   - Copy `.env.example` to `.env`
   - Update with your Azure credentials:
   ```env
   # Azure Authentication (DO NOT commit actual values!)
   AZURE_CLIENT_ID=your_client_id_here
   AZURE_CLIENT_SECRET=your_client_secret_here
   AZURE_TENANT_ID=your_tenant_id_here
   
   # AI Foundry Configuration (use your project-specific values)
   PROJECT_CONNECTION_STRING=your_connection_string_here
   MODEL_DEPLOYMENT_NAME=your_model_name_here
   
   # OpenTelemetry Settings (adjust based on your environment)
   OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
   OTEL_SERVICE_NAME=drug-discovery-platform
   OTEL_RESOURCE_ATTRIBUTES=deployment.environment=development
   ```

   > ⚠️ **Security Note**: Never commit real credentials or sensitive information to version control.
   > Always use environment variables or secure secret management solutions in production.

   Required Environment Variables:
   - `AZURE_CLIENT_ID`: Azure AD application ID for authentication
   - `AZURE_CLIENT_SECRET`: Azure AD application secret for authentication
   - `AZURE_TENANT_ID`: Azure AD tenant ID for authentication
   - `PROJECT_CONNECTION_STRING`: AI Foundry project connection string for agent and model access
   - `MODEL_DEPLOYMENT_NAME`: Name of your deployed model for agent creation
   - `OTEL_EXPORTER_OTLP_ENDPOINT`: OpenTelemetry collector endpoint for tracing
   - `OTEL_SERVICE_NAME`: Service name for tracing (default: drug-discovery-platform)
   - `OTEL_RESOURCE_ATTRIBUTES`: Additional tracing attributes (default: deployment.environment=development)

4. **Run the Server**:
   ```bash
   uvicorn main:app --reload
   ```

5. **Access API Documentation**:
   - OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Architecture 🏗️

```mermaid
flowchart TB
    subgraph Client
        FE[Frontend]
    end
    
    subgraph Backend
        API[FastAPI]
        AI[Azure AI Clients]
        TEL[OpenTelemetry]
    end
    
    subgraph Azure["Azure AI Foundry"]
        PRJ[AI Projects]
        AGT[AI Agents]
        INF[AI Inference]
        EVAL[AI Evaluation]
        subgraph Agents["AI Agent Tools"]
            BING[Bing Grounding]
            FUNC[Function Calling]
            CODE[Code Interpreter]
        end
    end
    
    FE <--> API
    API <--> AI
    AI <--> PRJ
    PRJ <--> AGT
    AGT <--> BING
    AGT <--> FUNC
    AGT <--> CODE
    PRJ <--> INF
    PRJ <--> EVAL
    API --> TEL
```

## Endpoints 🛠️

### Molecular Design Endpoints

#### 1. Analyze Molecule
```bash
POST /molecular-design/analyze
```
Analyzes a drug candidate's molecular properties using Azure AI Inference.

Request:
```json
{
    "id": "DRUG-001",
    "molecule_type": "Small Molecule",
    "therapeutic_area": "Oncology",
    "target_proteins": ["EGFR", "HER2"],
    "development_stage": "Phase 1"
}
```

Response:
```json
{
    "message": "Molecular analysis complete",
    "analysis": {
        "efficacy_score": 0.85,
        "safety_score": 0.92,
        "confidence": 0.89
    }
}
```

### Azure AI Agent Endpoints

#### 1. Literature Search
```bash
POST /agents/literature-search
```
Uses Azure AI Agent's Bing grounding capability to search and analyze scientific literature.

Request:
```json
{
    "query": "EGFR inhibitors in lung cancer"
}
```

Response:
```json
{
    "query": "EGFR inhibitors in lung cancer",
    "summary": "Analysis of recent publications...",
    "agent_id": "agent-123"
}
```

#### 2. Molecule Analysis
```bash
POST /agents/molecule-analysis
```
Uses Azure AI Agent's function calling capability to analyze molecular properties.

Request:
```json
{
    "smiles": "CC1=CC=C(C=C1)NC(=O)C2=CC=C(Cl)C=C2",
    "target_proteins": ["EGFR", "HER2"],
    "therapeutic_area": "Oncology"
}
```

Response:
```json
{
    "molecule": "CC1=CC=C(C=C1)NC(=O)C2=CC=C(Cl)C=C2",
    "analysis": "Detailed molecular property analysis...",
    "agent_id": "agent-456"
}
```

#### 3. Clinical Trial Data Analysis
```bash
POST /agents/data-analysis
```
Uses Azure AI Agent's code interpreter capability to analyze trial data.

Request:
```
multipart/form-data
- file: trial_data.csv
```

Response:
```json
{
    "filename": "trial_data.csv",
    "analysis": "Statistical analysis and visualizations...",
    "agent_id": "agent-789"
}
```

### Clinical Trials Endpoints

#### 1. Monitor Trials
```bash
GET /clinical-trials/monitor?trial_id=TRIAL-001
```
Real-time monitoring of clinical trial metrics and patient responses.

Response:
```json
{
    "trial_id": "TRIAL-001",
    "phase": "Phase 2",
    "status": "Active",
    "real_time_metrics": {
        "enrollment_rate": 0.75,
        "retention_rate": 0.92,
        "safety_signals": []
    }
}
```

#### 2. Predict Patient Response
```bash
POST /clinical-trials/predict-response
```
Predicts individual patient response using biomarker analysis.

Request:
```json
{
    "trial_id": "TRIAL-001",
    "patient_id": "PAT-001"
}
```

Response:
```json
{
    "predicted_response": 0.85,
    "confidence": 0.92,
    "recommendations": [
        "Continue monitoring key biomarkers",
        "Schedule follow-up in 2 weeks"
    ]
}
```

### Automated Testing Endpoints

#### 1. Run Evaluation Demo

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Evaluator
    participant Dataset
    
    Client->>API: POST /evaluation/run-demo
    API->>Dataset: Upload JSONL Data
    API->>Evaluator: Configure Evaluation
    Evaluator->>Evaluator: Run F1 Score
    Evaluator->>Evaluator: Run Relevance
    Evaluator-->>API: Results
    API-->>Client: Metrics
```

## OpenTelemetry Integration 📊

This project uses OpenTelemetry for distributed tracing to monitor and debug the drug development pipeline. Traces help us understand:

- 🔍 Performance bottlenecks
- 🔗 Request flows through the system
- ❌ Error patterns and their context
- 📈 AI model inference timing

### Viewing Traces

1. Traces are collected by the OpenTelemetry collector at:
   ```
   http://localhost:4318/v1/traces
   ```

2. Key spans to monitor:
   - `molecular_design.analyze`: Molecule analysis and AI inference
   - `clinical_trials.monitor`: Trial monitoring and metrics
   - `clinical_trials.predict_response`: Patient response predictions

3. Important attributes in traces:
   - `molecule.id`: Unique identifier for drug candidates
   - `molecule.type`: Type of molecule being analyzed
   - `therapeutic.area`: Target therapeutic area
   - `analysis.efficacy`: Predicted efficacy score
   - `analysis.safety`: Safety assessment score
   - `trial.id`: Clinical trial identifier
   - `patient.id`: Patient identifier for specific analyses

### Example Trace Analysis

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant AI as Azure AI
    participant DB as Database
    
    C->>A: POST /molecular-design/analyze
    activate A
    A->>AI: Analyze molecule
    AI-->>A: Inference results
    A->>DB: Store results
    A-->>C: Analysis response
    deactivate A
```

## Security 🔒

1. **Environment Variables**:
   - All secrets stored in `.env`
   - Never commit sensitive data

2. **Authentication**:
   - Azure AD integration
   - Role-based access control

3. **Data Protection**:
   - Encryption at rest
   - Secure communication

## Contributing 🤝
1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

## Setup and Running

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server (runs on port 8002):

   Windows (PowerShell):
   ```powershell
   .\start.ps1
   ```
   
   Unix/Linux/MacOS:
   ```bash
   ./start.sh
   ```

## Environment Variables

The backend server uses the following environment variables:

- `PORT`: Server port (defaults to 8002)
- `PROJECT_CONNECTION_STRING`: Azure project connection string
- `MODEL_DEPLOYMENT_NAME`: Azure model deployment name
- Other environment variables as specified in main.py

## API Documentation

Once the server is running, you can access the API documentation at:
- http://localhost:8002/ (ReDoc interface)

## Development

The server includes:
- FastAPI framework
- OpenTelemetry instrumentation
- CORS middleware configured for frontend at http://localhost:3000
- Health check endpoint at /health

## Deployment with Azure Developer CLI (azd) 🚀

1. **Install Azure Developer CLI**:
   ```bash
   curl -fsSL https://aka.ms/install-azd.sh | bash
   ```

2. **Login to Azure**:
   ```bash
   azd auth login
   ```

3. **Deploy from Root Directory**:
   From the root of "3-e2e-drug-discovery-sample/", run:
   ```bash
   azd init
   azd up
   ```

This will:
- Create Azure Container App for the backend
- Configure environment variables from your .env
- Deploy the backend service
- Output the public endpoint URL

After deployment:
- Access API documentation at `https://<your-app>.azurecontainerapps.io/docs`
- Use the endpoint URL in your frontend configuration

## Learn More 📚
- [Azure AI Projects SDK](https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme?view=azure-python-preview)
- [Azure AI Inference SDK](https://learn.microsoft.com/python/api/overview/azure/ai-inference-readme?view=azure-python-preview)
- [Azure AI Evaluation SDK](https://learn.microsoft.com/python/api/overview/azure/ai-evaluation-readme?view=azure-python-preview)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
