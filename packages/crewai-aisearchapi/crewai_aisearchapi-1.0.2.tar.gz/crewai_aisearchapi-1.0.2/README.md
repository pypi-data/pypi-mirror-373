# AI Search API for CrewAI - Developer Guide

## What is it?
A web search tool that gives your CrewAI agents the ability to search the internet and get intelligent, context-aware responses with source citations.

## Installation

```bash
pip install crewai-aisearchapi
```

## Quick Start

```python
from crewai import Agent, Task, Crew
from crewai_aisearchapi import AISearchTool

# Create the search tool
search_tool = AISearchTool(api_key='your-api-key')

# Give it to an agent
agent = Agent(
    role='Researcher',
    goal='Find information on the internet',
    tools=[search_tool]
)

# Create a task
task = Task(
    description='Search for the latest news about SpaceX',
    agent=agent
)

# Run it
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

## Common Use Cases

### 1. Basic Web Search Agent
```python
from crewai import Agent, Task, Crew
from crewai_aisearchapi import AISearchTool

# Setup
search = AISearchTool(api_key='your-key')

researcher = Agent(
    role='Web Researcher',
    goal='Search the web for information',
    tools=[search]
)

# Search for anything
task = Task(
    description='Find the current Bitcoin price and recent news about cryptocurrency',
    agent=researcher
)

crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
print(result)
```

### 2. News Monitoring Agent
```python
news_agent = Agent(
    role='News Monitor',
    goal='Find latest news and updates',
    tools=[AISearchTool(api_key='your-key')]
)

def get_latest_news(topic):
    task = Task(
        description=f'Search for the latest news about {topic} from the last 24 hours',
        agent=news_agent
    )
    crew = Crew(agents=[news_agent], tasks=[task])
    return crew.kickoff()

# Get news about any topic
tech_news = get_latest_news("artificial intelligence")
print(tech_news)
```

### 3. Fact-Checking Agent
```python
fact_checker = Agent(
    role='Fact Checker',
    goal='Verify claims by searching for reliable sources',
    tools=[AISearchTool(api_key='your-key')]
)

def verify_claim(claim):
    task = Task(
        description=f'Search the web to verify this claim: "{claim}". Find reliable sources.',
        agent=fact_checker
    )
    crew = Crew(agents=[fact_checker], tasks=[task])
    return crew.kickoff()

# Check any claim
result = verify_claim("The Great Wall of China is visible from space")
print(result)
```

### 4. Multi-Step Research
```python
search = AISearchTool(api_key='your-key')

agent = Agent(
    role='Research Analyst',
    goal='Conduct thorough research',
    tools=[search]
)

# Create multiple search tasks
tasks = [
    Task(
        description='Search for information about renewable energy trends in 2024',
        agent=agent
    ),
    Task(
        description='Find the top 5 solar panel manufacturers by market share',
        agent=agent
    ),
    Task(
        description='Search for government incentives for solar energy in the United States',
        agent=agent
    )
]

crew = Crew(agents=[agent], tasks=tasks)
results = crew.kickoff()
```

### 5. Question-Answering Bot
```python
from crewai import Agent, Task, Crew
from crewai_aisearchapi import AISearchTool

qa_bot = Agent(
    role='Q&A Assistant',
    goal='Answer questions using web search',
    tools=[AISearchTool(api_key='your-key')]
)

def answer_question(question):
    task = Task(
        description=f'Search the web and provide a comprehensive answer to: {question}',
        agent=qa_bot
    )
    crew = Crew(agents=[qa_bot], tasks=[task])
    return crew.kickoff()

# Ask anything
answer = answer_question("What are the health benefits of green tea?")
print(answer)
```

## Configuration Options

```python
from crewai_aisearchapi import AISearchTool, AISearchToolConfig

# Customize the tool behavior
config = AISearchToolConfig(
    default_response_type="markdown",  # or "text"
    include_sources=True,              # Include source URLs
    timeout=30,                        # Request timeout
    verbose=True                       # Show debug info
)

search = AISearchTool(
    api_key='your-key',
    config=config
)
```

## Using Environment Variables

```bash
# Set your API key
export AISEARCHAPI_API_KEY="your-api-key"
```

```python
# No need to pass API key
search = AISearchTool()  # Automatically uses env variable
```

## Handling Responses

The search tool returns responses with:
- **Answer**: The main search result
- **Sources**: URLs of sources used
- **Response Time**: How long the search took

```python
# The tool handles formatting automatically
# Your agents will receive formatted responses like:

"""
The current Bitcoin price is approximately $45,000 USD...

**Sources:**
- [1] https://coinmarketcap.com/...
- [2] https://finance.yahoo.com/...

*Response time: 150ms*
"""
```

## Multiple Agents with Search

```python
from crewai import Agent, Task, Crew, Process

search = AISearchTool(api_key='your-key')

# First agent searches
searcher = Agent(
    role='Searcher',
    goal='Find information',
    tools=[search]
)

# Second agent analyzes
analyzer = Agent(
    role='Analyzer',
    goal='Analyze search results',
    tools=[]
)

# Chain tasks
search_task = Task(
    description='Search for information about the latest iPhone',
    agent=searcher
)

analyze_task = Task(
    description='Analyze the search results and create a summary of key features',
    agent=analyzer
)

crew = Crew(
    agents=[searcher, analyzer],
    tasks=[search_task, analyze_task],
    process=Process.sequential
)

result = crew.kickoff()
```

## Error Handling

```python
# The tool handles errors gracefully
search = AISearchTool(api_key='your-key')

# If there's an error (rate limit, bad connection, etc.)
# The tool returns a formatted error message instead of crashing
# Your crew continues running
```

## Check Your Balance

```python
search = AISearchTool(api_key='your-key')

# Check remaining API credits
balance = search.check_balance()
print(f"Credits remaining: {balance['available_credits']}")
```

## Complete Example: Company Research Bot

```python
from crewai import Agent, Task, Crew
from crewai_aisearchapi import AISearchTool

def research_company(company_name):
    # Create search tool
    search = AISearchTool(api_key='your-key')
    
    # Create agent
    researcher = Agent(
        role='Company Researcher',
        goal='Gather comprehensive information about companies',
        tools=[search]
    )
    
    # Define what to search for
    task = Task(
        description=f"""
        Search for information about {company_name}:
        1. What does the company do?
        2. Recent news or announcements
        3. Who are the main competitors?
        4. Any recent product launches
        
        Provide a comprehensive summary.
        """,
        agent=researcher
    )
    
    # Run the research
    crew = Crew(agents=[researcher], tasks=[task])
    return crew.kickoff()

# Research any company
result = research_company("OpenAI")
print(result)
```

## Tips for Best Results

1. **Be specific in task descriptions** - The clearer your search task, the better the results
2. **Use markdown format** - Set `response_type="markdown"` for better formatted responses
3. **Check your balance** - Monitor API credits if running many searches
4. **Include sources** - Keep `include_sources=True` for credibility

## That's it!

Your AI Search API tool is now ready to use with CrewAI. Just:
1. Get your API key from [aisearchapi.io](https://aisearchapi.io?utm_source)
2. Install the package
3. Give the tool to your agents
4. Start searching!

```python
# Minimal working example
from crewai import Agent, Task, Crew
from crewai_aisearchapi import AISearchTool

agent = Agent(role='Searcher', tools=[AISearchTool(api_key='your-key')])
task = Task(description='Search for anything', agent=agent)
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```