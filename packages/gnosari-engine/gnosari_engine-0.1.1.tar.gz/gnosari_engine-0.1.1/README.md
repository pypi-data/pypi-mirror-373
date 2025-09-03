# Gnosari AI Workforce

**Gnosari AI Workforce** is a powerful framework for orchestrating multi-agent teams using Large Language Models. Create intelligent AI agent swarms that collaborate through streaming delegation and dynamic tool discovery.

## What is Gnosari AI Workforce?

Gnosari AI Workforce enables you to build sophisticated multi-agent systems where AI agents can:

- 🤝 **Delegate tasks** to specialized agents in real-time
- 🔧 **Discover and use tools** dynamically through MCP servers
- 📚 **Query knowledge bases** for context-aware responses
- 🌐 **Make API calls** to external services
- 🗄️ **Query databases** for data-driven decisions
- 📊 **Stream responses** for real-time collaboration

## Key Features

### Multi-Provider LLM Support
Each agent can use different models from various providers:
- OpenAI (GPT-4, GPT-4o, etc.)
- Anthropic (Claude)
- DeepSeek
- Google (Gemini)
- And more...

### Task Delegation
Agents use the delegate_agent tool to send tasks to other agents and receive responses, enabling seamless multi-agent coordination.

### Tool Integration
- Built-in tools (delegate_agent, api_request, knowledge_query, mysql_query, website_content, file_operations)
- MCP (Model Context Protocol) server integration
- Dynamic tool discovery

### Knowledge Bases
Embedchain integration for RAG capabilities with support for:
- Websites
- YouTube videos
- Documents
- And more...

## Quick Start

### Prerequisites
- **Python 3.12+** installed on your system
- **Poetry** for dependency management
- **API Keys** for the LLM providers you want to use

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/neomanex/gnosari-engine.git
cd gnosari-engine
```

2. **Install Dependencies**
```bash
poetry install
```

3. **Set Up Environment Variables**
Create a `.env` file in the project root:
```bash
# OpenAI (required for most examples)
OPENAI_API_KEY=your-openai-api-key

# Optional: Other providers
ANTHROPIC_API_KEY=your-anthropic-key
DEEPSEEK_API_KEY=your-deepseek-key
```

### Your First Team

Create a file called `my-first-team.yaml`:

```yaml
name: My First Team

# Define tools for the team
tools:
  - name: delegate_agent
    module: gnosari.tools.delegate_agent
    class: DelegateAgentTool
    args:
      pass

# Define agents
agents:
  - name: Coordinator
    instructions: >
      You are a helpful coordinator who manages tasks and delegates work to specialists.
      When you receive a request, analyze it and delegate to the appropriate specialist.
      Always provide a summary of the work completed.
    orchestrator: true
    model: gpt-4o
    tools:
      - delegate_agent

  - name: Writer
    instructions: >
      You are a professional writer who creates clear, engaging content.
      When given a writing task, focus on clarity, structure, and engaging the reader.
      Always ask for clarification if the requirements are unclear.
    model: gpt-4o

  - name: Researcher
    instructions: >
      You are a thorough researcher who gathers and analyzes information.
      When given a research task, provide comprehensive, well-sourced information.
      Always cite your sources and note any limitations in the information.
    model: gpt-4o
```

### Run Your Team

```bash
# Run entire team
poetry run gnosari --config "my-first-team.yaml" --message "Write a blog post about the benefits of renewable energy"

# Run specific agent
poetry run gnosari --config "my-first-team.yaml" --message "Research renewable energy trends" --agent "Researcher"

# With streaming output
poetry run gnosari --config "my-first-team.yaml" --message "Your message" --stream

# With debug mode
poetry run gnosari --config "my-first-team.yaml" --message "Your message" --debug
```

## Advanced Configuration

### Team with Knowledge Bases and Tools

```yaml
name: Advanced Content Team

# Knowledge bases (automatically adds knowledge_query tool)
knowledge:
  - name: "company_docs"
    type: "website"
    data: ["https://docs.yourcompany.com"]

# Tools configuration
tools:
  - name: delegate_agent
    module: gnosari.tools.delegate_agent
    class: DelegateAgentTool
    args:
      pass

  - name: api_request
    module: gnosari.tools.api_request
    class: APIRequestTool
    args:
      base_url: https://api.example.com
      base_headers:
        Authorization: Bearer ${API_TOKEN}
        Content-Type: application/json
      timeout: 30
      verify_ssl: true

  - name: mysql_query
    module: gnosari.tools.mysql_query
    class: MySQLQueryTool
    args:
      host: ${DB_HOST}
      port: 3306
      database: ${DB_NAME}
      username: ${DB_USER}
      password: ${DB_PASSWORD}
      pool_size: 5
      query_timeout: 30

# Agents configuration
agents:
  - name: Content Manager
    instructions: >
      You are a content manager who coordinates content creation workflows.
      You can delegate tasks to specialists and use various tools to gather information.
      Always ensure content is accurate, engaging, and meets quality standards.
    orchestrator: true
    model: gpt-4o
    tools:
      - delegate_agent
      - knowledge_query
    knowledge: ["company_docs"]

  - name: Data Analyst
    instructions: >
      You are a data analyst who works with databases and APIs to gather insights.
      Use the mysql_query tool to analyze data and the api_request tool to fetch external data.
      Always provide clear, actionable insights based on the data.
    model: gpt-4o
    tools:
      - mysql_query
      - api_request

  - name: Content Writer
    instructions: >
      You are a professional content writer who creates engaging, well-researched content.
      Use the knowledge_query tool to access company documentation and ensure accuracy.
      Focus on creating content that resonates with the target audience.
    model: gpt-4o
    tools:
      - knowledge_query
    knowledge: ["company_docs"]
```

## Built-in Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| **delegate_agent** | Delegate tasks to other agents in the team | Multi-agent coordination |
| **api_request** | Make HTTP requests to external APIs | External service integration |
| **knowledge_query** | Query knowledge bases for information | RAG and information retrieval |
| **mysql_query** | Execute SQL queries against MySQL databases | Database operations |
| **website_content** | Fetch content from websites via API | Web content retrieval |
| **file_operations** | Read, write, and manage files in a sandboxed directory | Local file management |

## Knowledge Base Support

Gnosari AI Workforce supports various knowledge sources through Embedchain:

- **Websites**: Crawl and index content from websites
- **YouTube**: Extract and index content from YouTube videos
- **Documents**: Process PDF, text, CSV, and JSON files
- **Direct Text**: Q&A content and structured information

## CLI Options

```bash
# Basic team execution
poetry run gnosari --config "team.yaml" --message "Your message"

# Run specific agent from team
poetry run gnosari --config "team.yaml" --message "Your message" --agent "AgentName"

# With streaming output
poetry run gnosari --config "team.yaml" --message "Your message" --stream

# With debug mode
poetry run gnosari --config "team.yaml" --message "Your message" --debug

# With custom model and temperature
poetry run gnosari --config "team.yaml" --message "Your message" --model "gpt-4o" --temperature 0.7
```

## Architecture

### Core Components
- **Team Builder**: Builds teams from YAML configs using OpenAI Agents SDK with handoffs
- **Team Runner**: Executes team workflows using OpenAI Agents SDK Runner with streaming support
- **Agent System**: Uses OpenAI's official Agents SDK with native handoff support
- **Tool Integration**: Native OpenAI tool calling with MCP server integration
- **Knowledge Bases**: Embedchain integration for RAG capabilities

### Key Directories
- **`src/gnosari/`**: Main source code
  - **`agents/`**: Agent implementations  
  - **`engine/`**: Team orchestration and execution
  - **`tools/`**: Built-in tools (delegation, API requests, etc.)
  - **`prompts/`**: Prompt engineering utilities
  - **`schemas/`**: Pydantic schemas and base classes
  - **`utils/`**: LLM client, tool manager, knowledge manager
- **`examples/`**: Team configuration examples
- **`tests/`**: Test files
- **`docs/`**: Documentation

## Development

### Testing
```bash
# Run all tests
poetry run pytest

# Run specific test
poetry run pytest tests/test_specific.py

# Run tests with coverage
poetry run pytest --cov=gnosari
```

### Alternative Execution
If experiencing pyenv shim issues, use the wrapper script:
```bash
./scripts/run-gnosari team run --config "examples/team.yaml" --message "Your message"
```

## Documentation

For comprehensive documentation, visit the [docs folder](docs/) which includes:

- [Quickstart Guide](docs/docs/quickstart.md) - Get up and running in minutes
- [Agents](docs/docs/agents.md) - Learn about agent configuration and capabilities
- [Teams](docs/docs/teams.md) - Understand team structure and coordination
- [Orchestration](docs/docs/orchestration.md) - Learn about agent coordination and workflow management
- [Knowledge Bases](docs/docs/knowledge.md) - Set up knowledge bases for RAG capabilities
- [Tools Overview](docs/docs/tools/intro.md) - Learn about built-in tools and how to use them

## Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit issues and pull requests.

## License

This project is licensed under the Creative Commons Attribution 4.0 International License - see the LICENSE file for details.

**You are free to:**
- Share and redistribute the code
- Modify and adapt the code  
- Use the code for any purpose, including commercial purposes
- Use the code in commercial products or services

**You must:**
- Provide proper attribution when using the code
- Indicate any changes made
- Link to the license

---

Ready to build your first AI workforce? Start with the [Quickstart Guide](docs/docs/quickstart.md) and create intelligent multi-agent teams that can tackle complex tasks through collaboration and specialization! 🚀