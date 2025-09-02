# Knowrithm Python SDK

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PyPI version](https://badge.fury.io/py/knowrithm-py.svg)](https://badge.fury.io/py/knowrithm-py)

**Knowrithm** is a powerful Python SDK that enables you to create, train, and deploy intelligent AI agents using your own data. Build custom chatbots and virtual assistants that can be seamlessly integrated into websites to provide exceptional customer support and engagement.

## 🚀 Features

- **Custom AI Agent Creation**: Build intelligent agents tailored to your specific needs
- **Data Training**: Train agents with your own documents, FAQs, and knowledge base
- **Easy Integration**: Simple APIs to embed agents into websites and applications
- **Multi-Modal Support**: Handle text, documents, and various data formats
- **Scalable Architecture**: Deploy agents that can handle multiple conversations simultaneously
- **Real-time Responses**: Fast and efficient agent responses for better user experience
- **Analytics & Insights**: Track agent performance and user interactions

## 📦 Installation

### Using pip

```bash
pip install knowrithm-py
```

### From Source

```bash
git clone https://github.com/Knowrithm/knowrithm-py.git
cd knowrithm-py
pip install -e .
```

## 🏃‍♂️ Quick Start

### 1. Initialize the Client

```python
from knowrithm.client import KnowrithmClient

# Initialize the client
client = KnowrithmClient()
client.auth.login("your-email", "your-password")
```

### 2. Create an AI Agent

```python
from knowrithm.agent import Agent

# Create a new agent
agent = client.create_agent(
    name="Customer Support Bot",
    description="AI agent for customer support",
    personality="friendly and helpful"
)

print(f"Agent created with ID: {agent.id}")
```

### 3. Train Your Agent

```python
from services.document import DocumentService

# Upload training documents
document_service = DocumentService(client)

# Train with documents
training_files = [
    "path/to/faq.pdf",
    "path/to/user_manual.docx",
    "path/to/product_info.txt"
]

for file_path in training_files:
    document_service.upload_document(agent.id, file_path)

# Start training
agent.train()
print("Training started. This may take a few minutes...")
```

### 4. Test Your Agent

```python
# Test the agent
response = agent.chat("How can I reset my password?")
print(f"Agent: {response.message}")
```

### 5. Deploy to Website

```python
# Generate embed code for your website
embed_code = agent.get_embed_code(
    theme="light",
    position="bottom-right",
    welcome_message="Hi! How can I help you today?"
)

print("Add this code to your website:")
print(embed_code)
```

## 📚 Detailed Usage

### Managing Agents

```python
from knowrithm.agent import Agent
from models.agent import AgentModel

# List all agents
agents = client.agents.list()

# Get specific agent
agent = client.agents.get_agent("agent_id")

# Update agent settings
agent.update(
    name="Updated Bot Name",
    personality="professional and concise",
    max_response_length=500
)

# Delete agent
agent.delete()
```

### Training with Different Data Types

```python
from services.document import DocumentService

document_service = DocumentService(client)

# Upload PDF documents
document_service.upload_pdf("agent_id", "manual.pdf")

# Upload text content directly
document_service.upload_text("agent_id", """
Q: What are your business hours?
A: We're open Monday-Friday 9AM-6PM EST.
""")

# Upload from URL
document_service.upload_from_url("agent_id", "https://example.com/faq")

# Bulk upload
document_service.bulk_upload("agent_id", [
    {"type": "pdf", "path": "doc1.pdf"},
    {"type": "text", "content": "Custom knowledge..."},
    {"type": "url", "url": "https://example.com/help"}
])
```

### Conversation Management

```python
from services.conversation import ConversationService

conversation_service = ConversationService(client)

# Start a new conversation
conversation = conversation_service.start_conversation(
    agent_id="your_agent_id",
    user_id="user_123"
)

# Send messages
response = conversation_service.send_message(
    conversation_id=conversation.id,
    message="Hello, I need help with billing"
)

# Get conversation history
history = conversation_service.get_history(conversation.id)

# End conversation
conversation_service.end_conversation(conversation.id)
```

### Advanced Features

#### Custom Response Handling

```python
from dataclass.response import ResponseConfig

# Configure response behavior
response_config = ResponseConfig(
    max_length=300,
    tone="professional",
    include_sources=True,
    fallback_message="I'm sorry, I don't have information about that."
)

agent.update_response_config(response_config)
```

#### Analytics and Monitoring

```python
from services.dashboard import DashboardService

dashboard = DashboardService(client)

# Get agent performance metrics
metrics = dashboard.get_agent_metrics("agent_id")
print(f"Total conversations: {metrics.total_conversations}")
print(f"Average satisfaction: {metrics.avg_satisfaction}")

# Get popular questions
popular_questions = dashboard.get_popular_questions("agent_id")

# Export conversation logs
logs = dashboard.export_conversations("agent_id", date_range="last_30_days")
```

## 🌐 Website Integration

### HTML/JavaScript Integration

```html
<!-- Add to your website's <head> section -->
<script 
    src="{base_url}/api/widget.js"
    data-agent-id="{agent_id}"
    data-company-id="{company_id}"
    data-api-url="{base_url}/api"
    data-color="{['color']}"
    data-position="{['position']}"
    data-welcome="{['welcome']}"
    data-title="{['title']}"
    async>
</script>
```

## ⚙️ Configuration

### Configuration File

```python
from config.config import Config

config = Config(
    api_key="your_api_key",
    base_url="https://app.knowrithm.org",
    timeout=30,
    max_retries=3,
    debug=True
)
```

## 📖 Examples

### Customer Support Bot

```python
from knowrithm.client import KnowrithmClient

# Initialize client
client = KnowrithmClient(api_key="your_key")

# Create customer support agent
support_agent = client.create_agent(
    name="Support Assistant",
    description="Helps customers with common inquiries",
    personality="empathetic and solution-focused"
)

# Train with support documents
support_agent.train_from_files([
    "support_docs/faq.pdf",
    "support_docs/troubleshooting.md",
    "support_docs/billing_info.txt"
])

# Deploy to website
embed_code = support_agent.generate_embed_code(
    theme="modern",
    greeting="Hi! I'm here to help with any questions you have."
)
```

### Sales Assistant Bot

```python
# Create sales-focused agent
sales_agent = client.create_agent(
    name="Sales Assistant",
    description="Helps potential customers learn about products",
    personality="enthusiastic and knowledgeable"
)

# Train with product information
sales_agent.train_from_content({
    "product_catalog": "Our products include...",
    "pricing": "Our pricing structure is...",
    "features": "Key features include..."
})

# Configure for lead generation
sales_agent.enable_lead_capture(
    fields=["name", "email", "company"],
    webhook_url="https://your-crm.com/webhook"
)
```

## 🛠️ Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/Knowrithm/knowrithm-py.git
cd knowrithm-py

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_agent.py
```

### Building the Package

```bash
# Build distribution files
python -m build

# Install locally
pip install -e .
```

## 📝 API Reference

### Core Classes

- **`KnowrithmClient`**: Main client for API interactions
- **`Agent`**: Represents an AI agent instance
- **`Conversation`**: Manages conversation state and history
- **`Document`**: Handles document upload and processing

### Services

- **`AuthService`**: Handle authentication and user management
- **`AgentService`**: Agent creation, training, and management
- **`ConversationService`**: Conversation handling and history
- **`DocumentService`**: Document upload and processing
- **`DashboardService`**: Analytics and monitoring

For detailed API documentation, visit: [https://docs.knowrithm.org](https://docs.knowrithm.org)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://docs.knowrithm.org](https://docs.knowrithm.org)
- **Discord Community**: [https://discord.gg/knowrithm](https://discord.gg/knowrithm)
- **Email Support**: support@knowrithm.org
- **GitHub Issues**: [https://github.com/Knowrithm/knowrithm-py.git/issues](https://github.com/Knowrithm/knowrithm-py.git/issues)

## 🏆 Examples in the Wild

- **E-commerce**: Product recommendation and support bots
- **SaaS Platforms**: Onboarding and feature explanation assistants
- **Healthcare**: Patient inquiry and appointment scheduling bots
- **Education**: Course information and student support assistants
- **Real Estate**: Property inquiry and virtual tour guides

## 🔮 Roadmap

- [ ] Voice integration capabilities
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with popular CRM systems
- [ ] Mobile SDK for iOS and Android
- [ ] Webhook system for custom integrations

---

**Made with ❤️ by the Knowrithm Team**

*Transform your website with intelligent AI agents that understand your business and delight your customers.*