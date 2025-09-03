# VectorBridge Python SDK

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python client for interacting with the [VectorBridge.ai](https://vectorbridge.ai) API. This client provides complete access to all aspects of the VectorBridge platform including authentication, user management, AI processing, vector operations, and more.

## Installation

```bash
pip install vector-bridge
```

## Quick Start

### Initialize the Client

For user authentication (admin access):

```python
from vector_bridge import VectorBridgeClient

# Initialize the client
client = VectorBridgeClient(integration_name="default")

# Login with credentials
client.login(username="your_email@example.com", password="your_password")

# Check if API is accessible
status = client.ping()  # Should return "OK"
```

For API key authentication (application access):

```python
from vector_bridge import VectorBridgeClient

# Initialize with API key
client = VectorBridgeClient(
    integration_name="default", 
    api_key="your_api_key"
)
```

## Authentication Methods

### Username/Password Authentication (Admin Access)

```python
from vector_bridge import VectorBridgeClient

client = VectorBridgeClient(integration_name="default")
token = client.login(username="your_email@example.com", password="your_password")

# Now you can access admin functionality
me = client.admin.user.get_me()
print(f"Logged in as: {me.email}")
```

### API Key Authentication (Application Access)

```python
from vector_bridge import VectorBridgeClient, SortOrder

client = VectorBridgeClient(
    integration_name="default", 
    api_key="your_api_key"
)

# Process a message with AI
response = client.ai_message.process_message_stream(
    content="What can you tell me about vector databases?",
    user_id="user123"
)

# Print the streaming response
for chunk in response.chunks:
    print(chunk, end="")

# Get the complete message after streaming
complete_message = response.message
```

## Core Features

### AI Message Processing

Process messages and get AI responses with streaming support:

```python
# Process a message and get streaming AI response
message_stream = client.ai_message.process_message_stream(
    content="Tell me about artificial intelligence",
    user_id="user123"
)

# Print the streaming response chunks
for chunk in message_stream.chunks:
    print(chunk, end="")

# Access the complete message
whole_message = message_stream.message
```

Process messages and get a Pydantic model as a response:

```python
# Define Pydantic models
class Crew(BaseModel):
    name: str

class MoonLandingDetails(BaseModel):
    landing_year: int
    landing_month: int
    landing_day: int
    crew: List[Crew]

# Process a message and get Pydantic model response
message_model = user_client.ai_message.process_message_json(
    response_model=MoonLandingDetails,
    content="Details about moon landing",
    user_id="user123"
)
```

Retrieve conversation history:

```python
# From DB
messages = client.ai_message.fetch_messages_from_db(
    user_id="user123",
    sort_order=SortOrder.DESCENDING,
    limit=50
)

# From Vector Database with semantic search capability
messages = client.ai_message.fetch_messages_from_vector_db(
    user_id="user123",
    near_text="machine learning"
)
```

### AI Agents

```python
# Set a specific agent for a user conversation
chat = client.ai.set_current_agent(
    user_id="user123",
    agent_name="sales_manager"
)

# Provide core knowledge for an agent
chat = client.ai.set_core_knowledge(
    user_id="user123",
    core_knowledge={
        "product_line": ["widgets", "gadgets"],
        "company_info": "Founded in 2020"
    }
)
```

### Function Execution

```python
# Execute a previously defined function
result = client.functions.run_function(
    function_name="calculator",
    function_args={
        "a": 10,
        "b": 5,
        "operation": "multiply"
    }
)

print(f"Result: {result}")
```

### Vector Database Queries

```python
# Run a semantic search query
results = client.queries.run_search_query(
    vector_schema="Documents",
    query_args={
        "content": "artificial intelligence applications",
        "full_document": False
    }
)

# Find similar documents based on a reference document
similar_docs = client.queries.run_find_similar_query(
    vector_schema="Documents",
    query_args={
        "uuid": "8c03ff2f-36f9-45f7-9918-48766c968f45"
    }
)
```

## Admin Functionality

### User Management

```python
# Get current user info
me = client.admin.user.get_me()

# Update user details
updated_me = client.admin.user.update_me(
    user_data=UserUpdate(
        full_name="John Doe",
        phone_number="+1234567890",
        country="US",
        city="New York"
    )
)

# Change password
client.admin.user.change_password(
    old_password="current_password", 
    new_password="new_secure_password"
)

# Add an agent user
new_agent = client.admin.user.add_agent(
    email="agent@example.com",
    first_name="Agent",
    last_name="User",
    password="secure_password"
)

# List users in your organization
users = client.admin.user.get_users_in_my_organization()

# Get user by ID or email
user = client.admin.user.get_user_by_id("user_id")
user = client.admin.user.get_user_by_email("user@example.com")
```

### Security Groups

```python
# Create a security group
sg = client.admin.security_groups.create_security_group(
    security_group_data=SecurityGroupCreate(
        group_name="Content Creators",
        description="Users who can create and edit content"
    )
)

# List security groups
security_groups = client.admin.security_groups.list_security_groups()

# Update security group permissions
permissions = security_groups.security_groups[0].group_permissions
permissions.logs.read = True
updated_sg = client.admin.security_groups.update_security_group(
    group_id=security_groups.security_groups[0].uuid,
    security_group_data=SecurityGroupUpdate(permissions=permissions)
)

# Get security group details
sg = client.admin.security_groups.get_security_group(group_id="group_id")

# Delete security group
client.admin.security_groups.delete_security_group(group_id="group_id")
```

### Integration Management

```python
# List all integrations
integrations = client.admin.integrations.get_integrations_list()

# Get integration by name
integration = client.admin.integrations.get_integration_by_name("default")

# Get integration by ID
integration = client.admin.integrations.get_integration_by_id("integration_id")

# Create a new integration
new_integration = client.admin.integrations.add_integration(
    integration_data=IntegrationCreate(
        integration_name="API Integration",
        integration_description="Integration for API access",
        openai_api_key="sk-your-openai-key",
        weaviate_url="https://your-weaviate-instance.cloud",
        weaviate_api_key="your-weaviate-key"
    )
)

# Update integration settings
updated = client.admin.integrations.update_integration_weaviate(
    weaviate_key=WeaviateKey.MAX_SIMILARITY_DISTANCE,
    weaviate_value=0.7
)

# Update message storage mode
updated = client.admin.integrations.update_message_storage_mode(
    message_storage_mode=MessageStorageMode.DB
)

# Update environment variables
updated = client.admin.integrations.update_environment_variables(
    env_variables={
        "API_KEY": "value1",
        "SECRET": "value2"
    }
)

# Delete an integration
client.admin.integrations.delete_integration("integration_name")
```

### User Access Management

```python
# Add user to integration
users_in_integration = client.admin.integrations.add_user_to_integration(
    user_id="user_id",
    security_group_id="security_group_id"
)

# Remove user from integration
users_in_integration = client.admin.integrations.remove_user_from_integration(
    user_id="user_id"
)

# Update user's security group
users = client.admin.integrations.update_users_security_group(
    security_group_id="new_group_id",
    user_id="user_id"
)

# Get users in an integration
users = client.admin.integrations.get_users_from_integration()
```

### Instructions Management

```python
# Create an instruction
instruction = client.admin.instructions.add_instruction(
    instruction_data=InstructionCreate(
        instruction_name="Sales Assistant",
        description="Instruction for sales assistance",
        open_ai_api_key="sk-your-openai-key"
    )
)

# Get instruction by name
instruction = client.admin.instructions.get_instruction_by_name("Sales Assistant")

# Get instruction by ID
instruction = client.admin.instructions.get_instruction_by_id("instruction_id")

# List instructions
instructions = client.admin.instructions.list_instructions()

# Delete instruction
client.admin.instructions.delete_instruction("instruction_id")
```

### Function Management

```python
# Create a function
function = client.admin.functions.add_function(
    function_data=FunctionCreate(
        function_name="calculator",
        description="Perform math operations",
        function_action=GPTActions.CODE_EXEC,
        code="""
import math

def calculate_power(base, exponent):
    return math.pow(float(base), float(exponent))

def run(**kwargs):
    base = kwargs.get("base")
    exponent = kwargs.get("exponent")
    return calculate_power(base, exponent)
""",
        function_parameters=FunctionParametersStorageStructure(
            properties=[
                FunctionPropertyStorageStructure(
                    name="base",
                    description="Base number"
                ),
                FunctionPropertyStorageStructure(
                    name="exponent",
                    description="Exponent"
                )
            ]
        )
    )
)


# Get function by name
function = client.admin.functions.get_function_by_name("calculator")

# Get function by ID
function = client.admin.functions.get_function_by_id("function_id")

# Update a function
updated_function = client.admin.functions.update_function(
    function_id="function_id",
    function_data=FunctionUpdate(
        description="Updated function description",
        code="print('Updated function code')"
    )
)

# List functions
functions = client.admin.functions.list_functions()

# List default functions
default_functions = client.admin.functions.list_default_functions()

# Execute a function
result = client.admin.functions.run_function(
    function_name="calculator",
    function_args={
        "base": 2,
        "exponent": 8
    }
)

# Delete a function
client.admin.functions.delete_function("function_id")
```

### Workflows
Vector Bridge offers a powerful Workflow system that enables you to create, manage, and execute multi-step processes with automatic caching, status tracking, and error handling. Workflows are ideal for complex operations that need reliability, reproducibility, and observability.
#### Creating a Custom Workflow
To create a custom workflow, you need to:
1. Create a class that inherits from the Workflow base class
2. Implement your workflow steps as methods decorated with @cache_result 
3. Implement a main execution method decorated with @workflow_runner

#### Example: Developer Search and Analysis Workflow
Here's an example workflow that demonstrates searching for developers and analyzing them:

```python
from vector_bridge import VectorBridgeClient
from vector_bridge.schema.workflows import WorkflowCreate
import json

# Import the Workflow base class and decorators
from vector_bridge.client.workflows import Workflow, workflow_runner, cache_result


class DeveloperAnalysisWorkflow(Workflow):
    def __init__(self, client: VectorBridgeClient, workflow_create: WorkflowCreate, job_description: str):
        # Initialize the base workflow with our configuration
        super().__init__(client, workflow_create)

        # Store workflow-specific parameters
        self.job_description = job_description

    @workflow_runner
    def run(self):
        """
        Main workflow execution method decorated with @workflow_runner
        
        This decorator handles:
        - Workflow status updates (PENDING → IN_PROGRESS → COMPLETED/FAILED)
        - Output capturing
        - Error handling and status updates
        - Result caching
        """
        # Execute each step of the workflow
        developers = self.search_developers()
        analysis = self.analyze_developers(developers)
        report_id = self.generate_report(analysis, developers)

        return {
            "developers_count": len(developers),
            "analysis": analysis,
            "report_id": report_id
        }

    @cache_result
    def search_developers(self):
        """
        Search for relevant developers using vector search.
        
        The @cache_result decorator ensures results are cached and can be 
        retrieved if the workflow is restarted.
        """
        developers = self.client.queries.run_search_query(
            vector_schema="Documents",
            query_args={
                "content": "Python AWS developer",
                "limit": 10,
                "type": "file",
                "tags_contains_all": ["aws", "python"],
                "full_document": True,
            },
        )

        # Process developers to extract content
        developers_content = []
        for developer in developers:
            developer_content = (
                f"File ID: {developer['item_id']}\n"
                f"File Name: {developer['name']}\n"
                f"Content: {''.join([chunk['content'] for chunk in developer['chunks']])}"
            )
            developers_content.append(developer_content)

        return {
            "raw_developers": developers,
            "developers_content": developers_content
        }

    @cache_result
    def analyze_developers(self, developers_data):
        """
        Analyze developers against the job requirements.
        Results are automatically cached.
        """
        analysis = self.client.functions.run_function(
            function_name="applicant_evaluation",
            function_args={
                "content": json.dumps(
                    {
                        "job_description": self.job_description,
                        "candidates": developers_data["developers_content"],
                    }
                ),
            },
        )

        return analysis

    @cache_result
    def generate_report(self, analysis, developers_data):
        """
        Generate a PDF report with the analysis results.
        Results are automatically cached.
        """
        file_id = self.client.functions.run_function(
            function_name="generate_pdf",
            function_args={
                "markdown_content": analysis,
                "file_name": "developer_analysis_report",
                "parent_id": "494b2a8d-c38b-4c8d-bc3e-bfc994f57443",
                "source_documents_ids": [dev["item_id"] for dev in developers_data["raw_developers"]],
            },
        )

        return file_id
```
#### Using the Workflow
Here's how to use the workflow in your application:
```python
from vector_bridge import VectorBridgeClient
from vector_bridge.schema.workflows import WorkflowCreate, WorkflowStatus
from my_workflows import DeveloperAnalysisWorkflow

# Initialize the Vector Bridge client
client = VectorBridgeClient(
    integration_name="HR Assistant",
    api_key="your_api_key_here"
)

# Job description to use for analysis
job_description = """
Provectus helps companies adopt AI to transform the ways they operate, compete, and drive value.
The focus of the company is on building Infrastructure to drive end-to-end AI transformations...
"""

# Initialize the workflow with required data
workflow_create = WorkflowCreate(
    workflow_id="your_workflow_id_here",
    workflow_name="Developer Analysis",
    description="Search for top developers and analyze them against job requirements",
    status=WorkflowStatus.PENDING,
)

# Create and run the workflow
workflow = DeveloperAnalysisWorkflow(client, workflow_create, job_description)
result = workflow.run()

# Check the workflow status
print(f"Workflow Status: {workflow.status}")
print(f"Result: {result}")
```
#### Workflow Decorators and Functions

### `@workflow_runner`

This decorator is designed for the main entry method of your workflow:

- Updates workflow status (PENDING → IN_PROGRESS → COMPLETED/FAILED)
- Captures all console output during execution
- Records execution time and details
- Handles exceptions and captures tracebacks
- Caches results for future retrieval

### `@cache_result`

This decorator is for individual workflow step methods:

- Caches the result of the method execution
- Uses a deterministic key based on method name, args, and kwargs
- Allows workflows to resume from intermediate steps if restarted

#### Important Workflow Methods

- `refresh()` - Refreshes workflow data from the server
- `update_status(status)` - Updates the workflow status
- `status` - Property to get current workflow status
- `get_cache(key)` - Retrieves a value from the workflow cache
- `set_cache(key, value)` - Sets a value in the workflow cache

#### Best Practices

1. **Modularity**: Break your workflow into smaller methods, each handling a specific task
2. **Idempotency**: Design methods to be safely re-executable without side effects
3. **Error Handling**: Add proper error handling inside workflow methods
4. **Progress Logging**: Use print statements to log progress (captured automatically)
5. **Status Monitoring**: Monitor workflow status for long-running workflows
6. **Cache Management**: Use caching wisely for expensive operations

#### Benefits of Using Workflows

- **Reliability**: Automatic status tracking and caching enable reliability
- **Observability**: Captured logs and execution details provide insights
- **Restartability**: Cache results allow workflows to resume after interruptions
- **Traceability**: Complete audit trail of execution steps and outputs
- **Error Recovery**: Workflows can be resumed from the last successful step


### API Key Management

```python
# Create an API key
api_key = client.admin.api_keys.create_api_key(
    api_key_data=APIKeyCreate(
        key_name="Client API Key",
        user_id="user_id",
        expire_days=30,
        monthly_request_limit=10000
    )
)

# Get API key details
api_key = client.admin.api_keys.get_api_key("api_key")

# List all API keys
api_keys = client.admin.api_keys.list_api_keys()

# Delete an API key
client.admin.api_keys.delete_api_key("api_key")
```

### Chat Management

```python
# Get all chats in my organization
chats = client.admin.chat.fetch_chats_for_my_organization(
    integration_name="default"
)

# Get my chats
my_chats = client.admin.chat.fetch_my_chats(
    integration_name="default"
)

# Delete a chat
client.admin.chat.delete_chat(
    user_id="user_id"
)
```

### Internal Message Processing

```python
# Process an internal message with AI
message_stream = client.admin.message.process_internal_message(
    content="Write a product description for our new AI-powered toaster",
    suffix="marketing_team",
    integration_name="default"
)

for chunk in message_stream.chunks:
    print(chunk)

full_message = message_stream.message
```

### AI Knowledge Management

#### File Storage

```python
# Create a folder
folder = client.admin.ai_knowledge.file_storage.create_folder(
    folder_name="Project Documents",
    folder_description="Documentation for our project",
    private=True
)

# Upload a file
file_upload = client.admin.ai_knowledge.file_storage.upload_file(
    file_path="document.pdf",
    file_name="project-specs.pdf",
    parent_id=folder.uuid,
    private=True,
    tags=["project", "documentation"]
)

for progress in file_upload.progress_updates:
    print(progress)

result = file.item

# Rename a file
renamed_file = client.admin.ai_knowledge.file_storage.rename_file_or_folder(
    item_id=file.uuid,
    new_name="updated-specs.pdf"
)

# Update file properties
client.admin.ai_knowledge.file_storage.update_file_or_folder_tags(
    item_id=file.uuid,
    tags=["important", "reference"]
)

client.admin.ai_knowledge.file_storage.update_file_or_folder_starred(
    item_id=file.uuid,
    is_starred=True,
)

# Get file details
file = client.admin.ai_knowledge.file_storage.get_file_or_folder(
    item_id="file_id"
)

# Get file path
path = client.admin.ai_knowledge.file_storage.get_file_or_folder_path(
    item_id="file_id"
)

# List files and folders
items = client.admin.ai_knowledge.file_storage.list_files_and_folders(
    filters=AIKnowledgeFileSystemFilters(
        parent_id=folder.uuid
    )
)

# Count files and folders
count = client.admin.ai_knowledge.file_storage.count_files_and_folders(
    parents=[folder.uuid]
)

# Get download link
download_link = client.admin.ai_knowledge.file_storage.get_download_link_for_document(
    item_id="file_id"
)

# Grant user access to a file
client.admin.ai_knowledge.file_storage.grant_or_revoke_user_access(
    item_id="file_id",
    user_id="user_id",
    has_access=True,
    access_type=FileAccessType.READ
)

# Grant security group access
client.admin.ai_knowledge.file_storage.grant_or_revoke_security_group_access(
    item_id="file_id",
    group_id="group_id",
    has_access=True,
    access_type=FileAccessType.READ
)

# Delete a file or folder
client.admin.ai_knowledge.file_storage.delete_file_or_folder(
    item_id="item_id"
)
```

#### Database Operations

```python
# Process content for database
content = client.admin.ai_knowledge.database.process_content(
    content_data=AIKnowledgeCreate(
        content="Sample content for vectorization",
        other={
            "price": 123,
            "category": "electronics"
        }
    ),
    schema_name="Products",
    unique_identifier="prod123"
)

# Update an item
updated_item = client.admin.ai_knowledge.database.update_item(
    item_data={"price": 149.99},
    schema_name="Products",
    item_id="item_id"
)

# Get content by identifier
item = client.admin.ai_knowledge.database.get_content(
    schema_name="Products",
    unique_identifier="prod123"
)

# List content with filters
items = client.admin.ai_knowledge.database.get_content_list(
    filters={"category": "electronics"},
    schema_name="Products"
)

# Delete content
client.admin.ai_knowledge.database.delete_content(
    schema_name="Products",
    unique_identifier="prod123"
)
```

### Vector Queries

```python
# Run a search query
results = client.admin.queries.run_search_query(
    vector_schema="Documents",
    query_args={
        "content": "machine learning algorithms",
        "full_document": False
    }
)

# Find similar items
similar = client.admin.queries.run_find_similar_query(
    vector_schema="Documents",
    query_args={
        "uuid": "document_uuid"
    }
)
```

### System Information

```python
# Get settings
settings = client.admin.settings.get_settings()

# Get logs
logs = client.admin.logs.list_logs(
    integration_name="default",
    limit=25
)

# Get notifications
notifications = client.admin.notifications.list_notifications(
    integration_name="default"
)

# Get usage statistics
usage = client.admin.usage.list_usage(
    primary_key="integration_id"
)

# Get organization info
org = client.admin.organization.get_my_organization()
```

## Complete Workflow Examples

### Document Processing and Query Workflow

```python
from vector_bridge import VectorBridgeClient, FileAccessType, AIKnowledgeFileSystemFilters

# Initialize client and authenticate
client = VectorBridgeClient(integration_name="Knowledge Base")
client.login(username="admin@example.com", password="secure_password")

# 1. Create a folder structure
main_folder = client.admin.ai_knowledge.file_storage.create_folder(
    folder_name="Research Papers",
    folder_description="Academic papers on machine learning",
    private=False
)

# 2. Upload documents
paper_upload = client.admin.ai_knowledge.file_storage.upload_file(
    file_path="papers/transformer_models.pdf",
    parent_id=main_folder.uuid,
    tags=["nlp", "transformers", "research"],
    vectorized=True  # Ensure the document is vectorized for search
)

print(f"Uploaded paper with ID: {paper_upload.result.uuid}")

# 3. Make the document accessible to a specific user
user = client.admin.user.get_user_by_email("researcher@example.com")
client.admin.ai_knowledge.file_storage.grant_or_revoke_user_access(
    item_id=paper.uuid,
    user_id=user.uuid,
    has_access=True,
    access_type=FileAccessType.READ
)

# 4. Query the document
results = client.admin.queries.run_search_query(
    vector_schema="Documents",
    query_args={
        "content": "attention mechanism in transformer models",
        "limit": 5,
        "full_document": False
    }
)

# 5. Process the results
for i, result in enumerate(results):
    print(f"Result {i+1}:")
    print(f"Document: {result['document'][0]['name']}")
    print(f"Content: {result['content'][:200]}...")
    print(f"Similarity score: {result['metadata']['certainty']}")
    print("---")
```

### AI Assistant with Function Calls

Absolutely! Below is a **rewritten README example** that shows **both methods** for registering and using functions with VectorBridge:

1. Registering a function using `FunctionCreate` with inline code (for lightweight cloud-deployed logic).
2. Registering a native Python function using `add_python_function` (for complex or maintainable workflows).

---

#### 🧠 VectorBridge Function Integration Example

This example demonstrates two ways to register functions in VectorBridge and use them in AI-assisted conversations:

- **Method 1:** Inline function using `FunctionCreate` (for quick cloud registration)
- **Method 2:** Native Python function using `add_python_function` (for clean, scalable projects)

---

#### ✅ Setup

```bash
pip install vector-bridge
```

```python
from vector_bridge import VectorBridgeClient, FunctionCreate, GPTActions, FunctionParametersStorageStructure, FunctionPropertyStorageStructure

# Initialize the client
client = VectorBridgeClient(
    integration_name="Virtual Assistant", 
    api_key="your_api_key"
)
```

---

#### 🔧 Method 1: Registering a Function via Inline Code (Currency Converter)

```python
currency_function = client.admin.functions.add_function(
    function_data=FunctionCreate(
        function_name="currency_converter",
        description="Convert an amount from one currency to another",
        function_action=GPTActions.CODE_EXEC,
        code="""
import requests

def convert_currency(amount, from_currency, to_currency):
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    response = requests.get(url)
    data = response.json()
    
    if to_currency not in data['rates']:
        return {"error": f"Currency {to_currency} not found"}
    
    conversion_rate = data['rates'][to_currency]
    converted_amount = amount * conversion_rate
    
    return {
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "converted_amount": converted_amount,
        "rate": conversion_rate
    }

def run(**kwargs):
    amount = float(kwargs.get("amount"))
    from_currency = kwargs.get("from_currency")
    to_currency = kwargs.get("to_currency")
    return convert_currency(amount, from_currency, to_currency)
""",
        function_parameters=FunctionParametersStorageStructure(
            properties=[
                FunctionPropertyStorageStructure(name="amount", description="Amount to convert"),
                FunctionPropertyStorageStructure(name="from_currency", description="Source currency code (e.g., USD)"),
                FunctionPropertyStorageStructure(name="to_currency", description="Target currency code (e.g., EUR)")
            ]
        )
    )
)
```

---

#### 🔧 Method 2: Registering a Native Python Function (Loan Payment Calculator)

```python
from typing import Dict
from pydantic import BaseModel, Field

# Define input schema using Pydantic
class LoanInput(BaseModel):
    principal: float = Field(..., description="Loan amount in dollars")
    annual_rate: float = Field(..., description="Annual interest rate (%)")
    years: float = Field(..., description="Loan term in years")

# Define logic
def calculate_loan_payment(principal: float, annual_rate: float, years: float) -> Dict[str, float]:
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
              ((1 + monthly_rate) ** num_payments - 1)
    return {"monthly_payment": round(payment, 2)}


# Register with VectorBridge
client.admin.functions.add_python_function(calculate_loan_payment)
```

---

#### 💬 Using the AI in a Conversation

```python
# Start a conversation
conversation_id = "user_1234"

response = client.ai_message.process_message_stream(
    content="How much is 100 US dollars in euros today?",
    user_id=conversation_id
)

print("AI Response:")
for chunk in response.chunks:
    print(chunk, end="")

# Follow-up
follow_up = client.ai_message.process_message_stream(
    content="And what's the monthly payment on a $10,000 loan at 5% over 3 years?",
    user_id=conversation_id
)

print("\n\nFollow-up Response:")
for chunk in follow_up.chunks:
    print(chunk, end="")
```

---

#### ✅ Summary

| Method                      | Best For                                      |
|----------------------------|-----------------------------------------------|
| `FunctionCreate` (inline)  | Quick registration, simpler one-off functions |
| `add_python_function`      | Scalable, debuggable, production-grade logic  |

---

### User Management and Permissions

```python
from vector_bridge import VectorBridgeClient, SecurityGroupCreate, SecurityGroupUpdate, APIKeyCreate, UserUpdate

# Initialize client and authenticate
client = VectorBridgeClient(integration_name="Admin Portal")
client.login(username="admin@example.com", password="secure_password")

# 1. Create security groups with different permission levels
editors_group = client.admin.security_groups.create_security_group(
    security_group_data=SecurityGroupCreate(
        group_name="Content Editors",
        description="Can edit and upload content"
    )
)

viewers_group = client.admin.security_groups.create_security_group(
    security_group_data=SecurityGroupCreate(
        group_name="Content Viewers",
        description="Can only view content"
    )
)

# 2. Update permissions for viewers group
permissions = viewers_group.group_permissions
permissions.ai_knowledge.read = True
permissions.ai_knowledge.write = False
client.admin.security_groups.update_security_group(
    group_id=viewers_group.uuid,
    security_group_data=SecurityGroupUpdate(permissions=permissions)
)

# 3. Add new users
editor = client.admin.user.add_agent(
    email="editor@example.com",
    first_name="Editor",
    last_name="User",
    password="editor_password"
)

viewer = client.admin.user.add_agent(
    email="viewer@example.com",
    first_name="Viewer",
    last_name="User",
    password="viewer_password"
)

# 4. Assign users to security groups
client.admin.integrations.add_user_to_integration(
    user_id=editor.uuid,
    security_group_id=editors_group.uuid
)

client.admin.integrations.add_user_to_integration(
    user_id=viewer.uuid,
    security_group_id=viewers_group.uuid
)

# 5. Create API keys for users
editor_key = client.admin.api_keys.create_api_key(
    api_key_data=APIKeyCreate(
        key_name="Editor API Key",
        user_id=editor.uuid,
        expire_days=90,
        monthly_request_limit=5000,
        integration_name=client.integration_name
    )
)

viewer_key = client.admin.api_keys.create_api_key(
    api_key_data=APIKeyCreate(
        key_name="Viewer API Key",
        user_id=viewer.uuid,
        expire_days=90,
        monthly_request_limit=3000,
        integration_name=client.integration_name
    )
)

print(f"Editor API Key: {editor_key.key}")
print(f"Viewer API Key: {viewer_key.key}")
```

## Error Handling

The client raises `HTTPException` when API requests fail:

```python
from vector_bridge import VectorBridgeClient, HTTPException

client = VectorBridgeClient(integration_name="default")

try:
    client.login(username="user@example.com", password="wrong_password")
except HTTPException as e:
    print(f"Authentication failed: {e.status_code} - {e.detail}")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.