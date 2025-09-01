# Reasoning Deployment Service

Helper package for deploying Vertex AI Reasoning Engines and Agent Spaces

---

## 📦 Installation

Install the package directly from PyPI (version 0.3.5):

```bash
pip install reasoning-deployment-service==0.3.5
```

---

## 🚀 First Run

Run the CLI tool with no arguments:

```bash
reasoning-deploy
```

### What happens

- You will see a list of available modes:

```
Choose an operation:
1) Create/Update
2) Auth only
3) CLI
4) GUI
q) Quit
```

- If required files are missing, usage will be limited until you bootstrap the project
- The tool will guide you to create the starter files:
  - `your_agent_import.py` (shim pointing to your agent folder)
  - `.env.agent` (environment and project settings)
  - `agent.yaml` (agent engine and space definition)

Once these are in place, all modes will be fully available

⚠️ Important: You must be running inside the same virtual environment where you installed reasoning-deployment-service

---

## ⚙️ Required Project Structure

Your project must have the following at minimum:

```
my_project/
├── requirements.txt       # pinned dependencies
├── .env.agent             # environment and project config
├── agent.yaml         # engine and agent space definition
├── my_agent/              # your agent folder
│   └── agent.py           # defines root_agent
```

---

### ✅ requirements.txt

This file must be in your project root and contain all dependencies

Example:

```text
google-adk==1.0.0
google-cloud-aiplatform[adk,agent_engines]>=1.88.0
google-generativeai>=0.7.0
pydantic>=2.0.0
python-dotenv>=1.0.0
python-docx>=1.1.0
google-api-python-client>=2.100.0
google-auth>=2.25.0
google-auth-httplib2>=0.2.0
google-auth-oauthlib>=1.2.0
absl-py>=2.0.0
PyPDF2>=3.0.0
deprecated>=1.2.14
reasoning-deployment-service==0.3.5
```

Install with:

```bash
pip install -r requirements.txt
```

---

### ✅ my_agent/agent.py

Inside your agent folder (for example `my_agent`) you must define a variable called `root_agent`

Example:

```python
from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    description="My reasoning agent",
    instruction="You do not do a whole lot yet"
)
```

This `root_agent` instance is what gets deployed  
It can be an `LlmAgent`, `Agent`, or any derived class

---

### ✅ .env.agent

Environment specific config for DEV and PROD

Example:

```env
DEV_PROJECT_ID=your-dev-project-id
DEV_PROJECT_NUMBER=123456789012
DEV_PROJECT_LOCATION=us-central1
DEV_STAGING_BUCKET=gs://your-dev-staging-bucket
DEV_AGENT_SPACE_ENGINE=your-dev-agentspace-engine
DEV_OAUTH_CLIENT_ID=your-dev-oauth-client-id.apps.googleusercontent.com
DEV_OAUTH_CLIENT_SECRET=your-dev-oauth-client-secret

PROD_PROJECT_ID=
PROD_PROJECT_NUMBER=
PROD_PROJECT_LOCATION=
PROD_STAGING_BUCKET=
PROD_AGENT_SPACE_ENGINE=
PROD_OAUTH_CLIENT_ID=
PROD_OAUTH_CLIENT_SECRET=

REASONING_DEPLOYMENT_VERSION=0.3.5

DEVELOPER=your.name
```

---

### ✅ agent.yaml

Example starter file:

```yaml
defaults:
  scopes:
    - https://www.googleapis.com/auth/cloud-platform
    - https://www.googleapis.com/auth/userinfo.email
  metadata:
    reasoning_engine_name: reasoning-engine-dev
    reasoning_engine_description: My Engine
    agent_space_name: My Agent Space
    agent_space_description: Example Agent Space
    agent_space_tool_description: Example Tool
  agent_folder: my_agent
  auth:
    oauth_authorization_id: test_auth
  environment_variables:
    - DEVELOPER
```

---

## 🛠 Potential Issues

- If you cannot run `reasoning-deploy`, try deleting your venv and making a new one
- If you see a message saying you can only install on user site-packages, you will most likely need a fresh venv and new requirements install
- Always ensure you are running `reasoning-deploy` inside the venv where it was installed

---

## ⚠️ Experimental Notice

This tool is still experimental  
If it takes longer than 20 to 30 minutes to set up, please go back to what already works for you and send logs and feedback to the development team
