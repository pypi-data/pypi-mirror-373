# CodeMie Python SDK

Python SDK for CodeMie services. This SDK provides a comprehensive interface to interact with CodeMie services, including LLM (Large Language Models), assistants, workflows, and tools.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
- [Service Details](#service-details)
  - [LLM Service](#llm-service)
  - [Assistant Service](#assistant-service)
    - [Core Methods](#core-methods)
    - [Advanced Features](#advanced-features)
  - [Datasource Service](#datasource-service)
    - [Supported Datasource Types](#supported-datasource-types)
    - [Core Methods](#core-methods-1)
    - [Datasource Status](#datasource-status)
    - [Best Practices for Datasources](#best-practices-for-datasources)
  - [Integration Service](#integration-service)
    - [Integration Types](#integration-types)
    - [Core Methods](#core-methods-2)
    - [Best Practices for Integrations](#best-practices-for-integrations)
  - [Workflow Service](#workflow-service)
    - [Core Methods](#core-methods-3)
    - [Workflow Execution](#workflow-execution)
    - [Workflow Configuration](#workflow-configuration)
    - [Best Practices](#best-practices)
    - [Error Handling](#error-handling)
    - [Workflow Status Monitoring](#workflow-status-monitoring)
- [Development](#development)
  - [Setup](#setup)
  - [Running Tests](#running-tests)
  - [Building Package](#building-package)
- [Error Handling](#error-handling-1)
- [Authentication](#authentication)
  - [Required Parameters](#required-parameters)
  - [Usage Examples](#usage-examples)
- [Best Practices](#best-practices-1)
- [Support](#support)

## Installation

```sh
pip install codemie-sdk
```
OR
```sh
poetry install
```

### If you want to run only tests, go to ## Running tests section

## Usage

### Basic usage

```python
from codemie_sdk import CodeMieClient

# Initialize client with authentication parameters
client = CodeMieClient(
    auth_server_url="https://keycloak.eks-core.aws.main.edp.projects.epam.com/auth",
    auth_client_id="your-client-id",
    auth_client_secret="your-client-secret",
    auth_realm_name="your-realm",
    codemie_api_domain="https://codemie.lab.epam.com/code-assistant-api"
)
```

## Service Details

### LLM Service

The LLM service provides access to language models and embedding models:

- **list()**: Retrieves a list of available LLM models
  ```python
  llm_models = client.llm.list(token=client.token)
  ```

- **list_embeddings()**: Retrieves a list of available embedding models
  ```python
  embedding_models = client.llm.list_embeddings(token=client.token)
  ```

Each LLM model contains the following information:
- Model identifier
- Model capabilities
- Configuration parameters

Example usage:
```python
# List available LLM models
llm_models = client.llm.list(token=client.token)

# List available embedding models
embedding_models = client.llm.list_embeddings(token=client.token)
```

### Assistant Service

The Assistant service allows you to manage and interact with CodeMie assistants:

#### Core Methods

1. **List Assistants**
```python
assistants = client.assistant.list(
    minimal_response=True,  # Return minimal assistant info
    scope="visible_to_user",  # or "created_by_user"
    page=0,
    per_page=12,
    filters={"key": "value"}  # Optional filters
)
```

2. **Get Assistant Details**
```python
# By ID
assistant = client.assistant.get("assistant-id")

# By Slug
assistant = client.assistant.get_by_slug("assistant-slug")
```

3. **Create Assistant**
```python
from codemie_sdk.models.assistant import AssistantCreateRequest

request = AssistantCreateRequest(
    name="My Assistant",
    description="Assistant description",
    instructions="Assistant instructions",
    tools=["tool1", "tool2"],
    # Additional parameters as needed
)
new_assistant = client.assistant.create(request)
```

4. **Update Assistant**
```python
from codemie_sdk.models.assistant import AssistantUpdateRequest

request = AssistantUpdateRequest(
    name="Updated Name",
    description="Updated description",
    # Other fields to update
)
updated_assistant = client.assistant.update("assistant-id", request)
```

5. **Delete Assistant**
```python
result = client.assistant.delete("assistant-id")
```

#### Advanced Features

6. **Chat with Assistant**
```python
from codemie_sdk.models.assistant import AssistantChatRequest

chat_request = AssistantChatRequest(
    text="Your message here",
    stream=False,  # Set to True for streaming response
    # Additional parameters
)
response = client.assistant.chat("assistant-id", chat_request)
```

7. **Utilize structured outputs with Assistant**
```python
from pydantic import BaseModel

class OutputSchema(BaseModel):
    requirements: list[str]

chat_request = AssistantChatRequest(
    text="Your message here",
    stream=False, 
    output_schema=OutputSchema
    # Additional parameters
)

response = client.assistants.chat("id", chat_request)
# response.generated is a Pydantic object
```
Or using JSON schema in dict format
```python
output_schema = {
    "properties": {
        "requirements": {
            "items": {"type": "string"},
            "title": "Requirements",
            "type": "array",
        }
    },
    "required": ["requirements"],
    "title": "OutputSchema",
    "type": "object",
}

chat_request = AssistantChatRequest(
    text="Your message here",
    stream=False, 
    output_schema=output_schema 
    # Additional parameters
)

response = client.assistants.chat("id", chat_request)
# response.generated is a dict corresponded with JSON schema
```

8. **Work with Prebuilt Assistants**
```python
# List prebuilt assistants
prebuilt = client.assistant.get_prebuilt()

# Get specific prebuilt assistant
prebuilt_assistant = client.assistant.get_prebuilt_by_slug("assistant-slug")
```

9. **Get Available Tools**
```python
tools = client.assistant.get_tools()
```

### Datasource Service

The Datasource service enables managing various types of data sources in CodeMie, including code repositories, Confluence spaces, Jira projects, files, and Google documents.

#### Supported Datasource Types

- `CODE`: Code repository datasources
- `CONFLUENCE`: Confluence knowledge base
- `JIRA`: Jira knowledge base
- `FILE`: File-based knowledge base
- `GOOGLE`: Google documents

#### Core Methods

1. **Create Datasource**
```python
from codemie_sdk.models.datasource import (
    CodeDataSourceRequest,
    ConfluenceDataSourceRequest,
    JiraDataSourceRequest,
    GoogleDataSourceRequest
)

# Create Code Datasource
code_request = CodeDataSourceRequest(
    name="my_repo",  # lowercase letters and underscores only
    project_name="my_project",
    description="My code repository",
    link="https://github.com/user/repo",
    branch="main",
    index_type="code",  # or "summary" or "chunk-summary"
    files_filter="*.py",  # optional
    embeddings_model="model_name",
    summarization_model="gpt-4",  # optional
    docs_generation=False  # optional
)
result = client.datasource.create(code_request)

# Create Confluence Datasource
confluence_request = ConfluenceDataSourceRequest(
    name="confluence_kb",
    project_name="my_project",
    description="Confluence space",
    cql="space = 'MYSPACE'",
    include_restricted_content=False,
    include_archived_content=False,
    include_attachments=True,
    include_comments=True
)
result = client.datasource.create(confluence_request)

# Create Jira Datasource
jira_request = JiraDataSourceRequest(
    name="jira_kb",
    project_name="my_project",
    description="Jira project",
    jql="project = 'MYPROJECT'"
)
result = client.datasource.create(jira_request)

# Create Google Doc Datasource
google_request = GoogleDataSourceRequest(
    name="google_doc",
    project_name="my_project",
    description="Google document",
    google_doc="document_url"
)
result = client.datasource.create(google_request)
```

2. **Update Datasource**
```python
from codemie_sdk.models.datasource import UpdateCodeDataSourceRequest

# Update Code Datasource
update_request = UpdateCodeDataSourceRequest(
    name="my_repo",
    project_name="my_project",
    description="Updated description",
    branch="develop",
    full_reindex=True,  # optional reindex parameters
    skip_reindex=False,
    resume_indexing=False
)
result = client.datasource.update("datasource_id", update_request)
```

3. **List Datasources**
```python
# List all datasources with filtering and pagination
datasources = client.datasource.list(
    page=0,
    per_page=10,
    sort_key="update_date",  # or "date"
    sort_order="desc",  # or "asc"
    datasource_types=["CODE", "CONFLUENCE"],  # optional filter by type
    projects=["project1", "project2"],  # optional filter by projects
    owner="John Doe",  # optional filter by owner
    status="COMPLETED"  # optional filter by status
)
```

4. **Get Datasource Details**
```python
# Get single datasource by ID
datasource = client.datasource.get("datasource_id")
```

5. **Delete Datasource**
```python
# Delete datasource by ID
result = client.datasource.delete("datasource_id")
```

#### Datasource Status

Datasources can have the following statuses:
- `COMPLETED`: Indexing completed successfully
- `FAILED`: Indexing failed
- `FETCHING`: Fetching data from source
- `IN_PROGRESS`: Processing/indexing in progress

#### Best Practices for Datasources

1. **Naming Convention**:
   - Use lowercase letters and underscores for datasource names
   - Keep names descriptive but concise

2. **Performance Optimization**:
   - Use appropriate filters when listing datasources
   - Consider pagination for large result sets
   - Choose appropriate reindex options based on your needs

3. **Error Handling**:
   - Always check datasource status after creation/update
   - Handle potential failures gracefully
   - Monitor processing information for issues

4. **Security**:
   - Be careful with sensitive data in filters and queries
   - Use proper access controls when sharing datasources
   - Regularly review and clean up unused datasources

### Integration Service

The Integration service manages both user and project-level integrations in CodeMie, allowing you to configure and manage various integration settings.

#### Integration Types

- `USER`: User-level integrations
- `PROJECT`: Project-level integrations

#### Core Methods

1. **List Integrations**
```python
from codemie_sdk.models.integration import IntegrationType

# List user integrations with pagination
user_integrations = client.integration.list(
    setting_type=IntegrationType.USER,
    page=0,
    per_page=10,
    filters={"some_filter": "value"}  # optional
)

# List project integrations
project_integrations = client.integration.list(
    setting_type=IntegrationType.PROJECT,
    per_page=100
)
```

2. **Get Integration**
```python
# Get integration by ID
integration = client.integration.get(
    integration_id="integration_id",
    setting_type=IntegrationType.USER
)

# Get integration by alias
integration = client.integration.get_by_alias(
    alias="integration_alias",
    setting_type=IntegrationType.PROJECT
)
```

3. **Create Integration**
```python
from codemie_sdk.models.integration import Integration

# Create new integration
new_integration = Integration(
    setting_type=IntegrationType.USER,
    alias="my_integration",
    # Add other required fields based on integration type
)
result = client.integration.create(new_integration)
```

4. **Update Integration**
```python
# Update existing integration
updated_integration = Integration(
    setting_type=IntegrationType.USER,
    alias="updated_alias",
    # Add other fields to update
)
result = client.integration.update("integration_id", updated_integration)
```

5. **Delete Integration**
```python
# Delete integration
result = client.integration.delete(
    setting_id="integration_id",
    setting_type=IntegrationType.USER
)
```

#### Best Practices for Integrations

1. **Error Handling**:
   - Handle `NotFoundError` when getting integrations by ID or alias
   - Validate integration settings before creation/update
   - Use appropriate setting type (USER/PROJECT) based on context

2. **Performance**:
   - Use pagination for listing integrations
   - Cache frequently accessed integrations when appropriate
   - Use filters to reduce result set size

3. **Security**:
   - Keep integration credentials secure
   - Regularly review and update integration settings
   - Use project-level integrations for team-wide settings
   - Use user-level integrations for personal settings

### Workflow Service

The Workflow service enables you to create, manage, and execute workflows in CodeMie. Workflows allow you to automate complex processes and integrate various CodeMie services.

#### Core Methods

1. **Create Workflow**
```python
from codemie_sdk.models.workflow import WorkflowCreateRequest

# Create new workflow
workflow_request = WorkflowCreateRequest(
    name="My Workflow",
    description="Workflow description",
    project="project-id",
    yaml_config="your-yaml-configuration",
    mode="SEQUENTIAL",  # Optional, defaults to SEQUENTIAL
    shared=False,       # Optional, defaults to False
    icon_url="https://example.com/icon.png"  # Optional
)
result = client.workflow.create_workflow(workflow_request)
```

2. **Update Workflow**
```python
from codemie_sdk.models.workflow import WorkflowUpdateRequest

# Update existing workflow
update_request = WorkflowUpdateRequest(
    name="Updated Workflow",
    description="Updated description",
    yaml_config="updated-yaml-config",
    mode="PARALLEL",
    shared=True
)
result = client.workflow.update("workflow-id", update_request)
```

3. **List Workflows**
```python
# List workflows with pagination and filtering
workflows = client.workflow.list(
    page=0,
    per_page=10,
    projects=["project1", "project2"]  # Optional project filter
)
```

4. **Get Workflow Details**
```python
# Get workflow by ID
workflow = client.workflow.get("workflow-id")

# Get prebuilt workflows
prebuilt_workflows = client.workflow.get_prebuilt()
```

5. **Delete Workflow**
```python
result = client.workflow.delete("workflow-id")
```

#### Workflow Execution

The SDK provides comprehensive workflow execution management through the WorkflowExecutionService:

1. **Run Workflow**
```python
# Simple workflow execution
execution = client.workflow.run("workflow-id", user_input="optional input")

# Get execution service for advanced operations
execution_service = client.workflow.executions("workflow-id")
```

2. **Manage Executions**
```python
# List workflow executions
executions = execution_service.list(
    page=0,
    per_page=10
)

# Get execution details
execution = execution_service.get("execution-id")

# Abort running execution
result = execution_service.abort("execution-id")

# Resume interrupted execution
result = execution_service.resume("execution-id")

# Delete all executions
result = execution_service.delete_all()
```

3. **Work with Execution States**
```python
# Get execution states
states = execution_service.states(execution_id).list()

# Get state output
state_output = execution_service.states(execution_id).get_output(state_id)

# Example of monitoring workflow with state verification
def verify_workflow_execution(execution_service, execution_id):
    execution = execution_service.get(execution_id)
    
    if execution.status == ExecutionStatus.SUCCEEDED:
        # Get and verify states
        states = execution_service.states(execution_id).list()
        
        # States are ordered by completion date
        if len(states) >= 2:
            first_state = states[0]
            second_state = states[1]
            assert first_state.completed_at < second_state.completed_at
            
            # Get state outputs
            for state in states:
                output = execution_service.states(execution_id).get_output(state.id)
                print(f"State {state.id} output: {output.output}")
    
    elif execution.status == ExecutionStatus.FAILED:
        print(f"Workflow failed: {execution.error_message}")
```

#### Workflow Configuration

Workflows support various configuration options:

1. **Modes**:
- `SEQUENTIAL`: Tasks execute in sequence
- `PARALLEL`: Tasks can execute simultaneously

2. **YAML Configuration**:
```yaml
name: Example Workflow
description: Workflow description
tasks:
  - name: task1
    type: llm
    config:
      prompt: "Your prompt here"
      model: "gpt-4"
  
  - name: task2
    type: tool
    config:
      tool_name: "your-tool"
      parameters:
        param1: "value1"
```

#### Best Practices

1. **Workflow Design**:
- Keep workflows modular and focused
- Use clear, descriptive names for workflows and tasks
- Document workflow purpose and requirements
- Test workflows thoroughly before deployment

2. **Execution Management**:
- Monitor long-running workflows
- Implement proper error handling
- Use pagination for listing executions
- Clean up completed executions regularly

3. **Performance Optimization**:
- Choose appropriate workflow mode (SEQUENTIAL/PARALLEL)
- Manage resource usage in parallel workflows
- Consider task dependencies and ordering
- Use efficient task configurations

4. **Security**:
- Control workflow sharing carefully
- Validate user inputs
- Manage sensitive data appropriately
- Regular audit of workflow access

5. **Maintenance**:
- Regular review of workflow configurations
- Update workflows when dependencies change
- Monitor workflow performance
- Archive or remove unused workflows

#### Error Handling

Implement proper error handling for workflow operations:

```python
try:
    workflow = client.workflow.get("workflow-id")
except ApiError as e:
    if e.status_code == 404:
        print("Workflow not found")
    else:
        print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

#### Workflow Status Monitoring

Monitor workflow execution status:

```python
def monitor_execution(execution_service, execution_id):
    while True:
        execution = execution_service.get(execution_id)
        status = execution.status
        
        if status == "COMPLETED":
            print("Workflow completed successfully")
            break
        elif status == "FAILED":
            print(f"Workflow failed: {execution.error}")
            break
        elif status == "ABORTED":
            print("Workflow was aborted")
            break
            
        time.sleep(5)  # Poll every 5 seconds
```

## Error Handling

The SDK implements comprehensive error handling. All API calls may raise exceptions for:
- Authentication failures
- Network errors
- Invalid parameters
- Server-side errors

It's recommended to implement try-catch blocks around SDK operations to handle potential exceptions gracefully.

## Authentication

The SDK supports two authentication methods through Keycloak:

1. Username/Password Authentication
2. Client Credentials Authentication

### Required Parameters

You must provide either:

- Username/Password credentials:
  ```python
  {
      "username": "your-username", 
      "password": "your-password",
      "auth_client_id": "client-id",        # Optional, defaults to "codemie-sdk"
      "auth_realm_name": "realm-name",
      "auth_server_url": "keycloak-url",
      "verify_ssl": True                    # Optional, defaults to True
  }
  ```

OR

- Client Credentials:
  ```python
  {
      "auth_client_id": "your-client-id",
      "auth_client_secret": "your-client-secret",
      "auth_realm_name": "realm-name", 
      "auth_server_url": "keycloak-url",
      "verify_ssl": True                    # Optional, defaults to True
  }
  ```

### Usage Examples

1. Username/Password Authentication:
```python
from codemie_sdk import CodeMieClient

client = CodeMieClient(
    codemie_api_domain="https://api.domain.com",
    username="your-username",
    password="your-password",
    auth_client_id="your-client-id",        # Optional
    auth_realm_name="your-realm",
    auth_server_url="https://keycloak.domain.com/auth",
    verify_ssl=True                         # Optional
)
```

2. Client Credentials Authentication:
```python
from codemie_sdk.auth import KeycloakCredentials

credentials = KeycloakCredentials(
    server_url="https://keycloak.domain.com/auth",
    realm_name="your-realm",
    client_id="your-client-id",
    client_secret="your-client-secret",
    verify_ssl=True                         # Optional
)

client = CodeMieClient(
    codemie_api_domain="https://api.domain.com",
    credentials=credentials
)
```

## Support
For providing credentials please contact AI/Run CodeMie Team: Vadym_Vlasenko@epam.com or Nikita_Levyankov@epam.com

## Running tests

For running tests on custom environment you should create .env file in the ./tests directory,
ask QA team: anton_yeromin@epam.com to provide all needed testing credentials. Under this directory there are stubs
for .env files for running tests on local and preview environments.

Configuration example:

``` properties

AUTH_SERVER_URL=https://keycloak.eks-core.aws.main.edp.projects.epam.com/auth
AUTH_CLIENT_ID=codemie-preview
AUTH_CLIENT_SECRET=<auth_clienbt_secret>
AUTH_REALM_NAME=codemie-prod
CODEMIE_API_DOMAIN=http://localhost:8080
VERIFY_SSL=False

NATS_URL=nats://localhost:4222

ENV=local
CLEANUP_DATA=True

AUTH_USERNAME=<username>
AUTH_PASSWORD=<password>
TEST_USER_FULL_NAME=<user_full_name>

PROJECT_NAME=codemie
GIT_ENV=gitlab

DEFAULT_TIMEOUT=60

GITLAB_URL=https://gitbud.epam.com
GITLAB_TOKEN=<gitlab_token>
GITLAB_PROJECT=https://gitbud.epam.com/epm-cdme/autotests/codemie-test-project
GITLAB_PROJECT_ID=17889

GITHUB_URL=https://github.com
GITHUB_TOKEN=<github_token>
GITHUB_PROJECT=https://github.com/wild47/final_task

JIRA_URL=https://jiraeu.epam.com
JIRA_TOKEN=<jira_token>
JQL="project = 'EPMCDME' and issuetype = 'Epic' and status = 'Closed'"

CONFLUENCE_URL=https://kb.epam.com
CONFLUENCE_TOKEN=<confluence_token>
CQL="space = EPMCDME and type = page and title = 'AQA Backlog Estimation'"

AWS_ACCESS_KEY=<aws_access_token>
AWS_SECRET_KEY=<aws_secret_key>

RP_API_KEY=<report_portal_key_optional>
```

Run all tests (-n - number of parallel workers. Fill free to change it to find the best that suits your environment)

```shell
pytest -n 10 --reruns 2
```

Run e2e/regression tests

```shell
pytest -n 10 -m "e2e or regression" --reruns 2
```

Run UI tests

First you have to install playwright browsers:

```shell
playwright install
```
and then

```shell
pytest -n 4 -m ui --reruns 2
```

All Playwright documentation can be found by the following link: https://playwright.dev/python/docs/intro

Run tests for e2e tests for specific integration/tool.
Available marks:
 - jira_kb
 - confluence_kb
 - code_kb
 - gitlab
 - github
 - git

```shell
pytest -n 10 -m "jira_kb or github" --reruns 2
```

In case you want to send test results in **ReportPortal** you should specify RP_API_KEY in .env and run tests like this:

```shell
pytest -n 10 -m "e2e or regression" --reruns 2 --reportportal
```

ReportPortal link is available by the following URL: https://report-portal.core.kuberocketci.io/ui/#epm-cdme/launches/all

If you do not have access to the project ask Anton Yeromin (anton_yeromin@epam.com) to add you.