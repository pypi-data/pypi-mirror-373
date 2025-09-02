# AI Search API for CrewAI - Developer & SEO Guide

[![PyPI version](https://badge.fury.io/py/crewai-aisearchapi.svg)](https://badge.fury.io/py/crewai-aisearchapi)
[![Python Support](https://img.shields.io/pypi/pyversions/crewai-aisearchapi.svg)](https://pypi.org/project/crewai-aisearchapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **Python integration for CrewAI** that connects your agents to the [AI Search API](https://aisearchapi.io?utm_source=github).  
It enables **semantic search, contextual queries, SEO‑friendly content generation, and intelligent answers with sources**.

👉 To start, get your **free API key** from the [AI Search API dashboard](https://app.aisearchapi.io/dashboard).

---

## Features

- **🔍 AI-Powered Web Search**: Let CrewAI agents search the web with natural language  
- **🎯 Context Awareness**: Add history messages for better, more relevant answers  
- **⚡ Seamless CrewAI Integration**: Works out of the box with `Agent`, `Task`, and `Crew`  
- **🛡️ Strong Typing**: Includes dataclasses and type hints for safe development  
- **💡 SEO Use Cases**: Generate SEO‑optimized content, product descriptions, FAQs  
- **📊 Sources**: Always returns sources for transparency  
- **🖥️ Local LLM Support**: Combine with free Ollama models for offline reasoning  

---

## Installation

```bash
pip install crewai-aisearchapi
```

---

## Quick Start (with Ollama + CrewAI)

```python
from crewai import Agent, Task, Crew, Process, LLM
from crewai_aisearchapi import AISearchTool

# Use a local free model (Ollama)
llm = LLM(
    model="ollama/llama3.2:3b",            # or llama3.1:8b
    base_url="http://localhost:11434",     # Ollama default
    temperature=0.2,
)

# Add the AI Search tool
tool = AISearchTool(api_key="your-api-key")

agent = Agent(
    role="Researcher",
    goal="Short, correct answers with sources when available.",
    backstory="Careful and concise.",
    tools=[tool],
    llm=llm,
    verbose=True,
)

task = Task(
    description="Answer: '{question}'. Keep it short.",
    expected_output="2–4 sentences.",
    agent=agent,
    markdown=True,
)

crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)

if __name__ == "__main__":
    print(crew.kickoff(inputs={"question": "What is RLHF in AI?"}))
```

---

## Configuration Options

```python
from crewai_aisearchapi import AISearchTool, AISearchToolConfig

config = AISearchToolConfig(
    default_response_type="markdown",  # or "text"
    include_sources=True,
    timeout=30,
    verbose=True
)

tool = AISearchTool(api_key="your-key", config=config)
```

---

## Contextual Search

You can pass multiple context messages (all must be role `"user"`):

```python
result = tool.run({
    "prompt": "Summarize quantum dots for displays.",
    "context": [
        {"role": "user", "content": "Be concise."},
        {"role": "user", "content": "Focus on consumer TVs."}
    ],
    "response_type": "markdown"
})
```

---

## SEO Use Cases

The AI Search API is not just for research — it’s also great for **SEO content generation**:

- 📈 Write **product descriptions** with live data & sources  
- 📝 Generate **blog posts** enriched with context and citations  
- ❓ Build **FAQ sections** that adapt to user intent  
- 🌍 Research **competitor content** and summarize strengths/weaknesses  
- ⚙️ Automate **content briefs** for writers using CrewAI agents  

Example:

```python
seo_agent = Agent(
    role="SEO Writer",
    goal="Generate SEO-optimized product descriptions.",
    backstory="Expert in e-commerce SEO content.",
    tools=[tool],
    llm=llm
)

seo_task = Task(
    description="Write a 150-word SEO product description for '{product}'",
    expected_output="SEO-rich product description with 2 citations.",
    agent=seo_agent
)
```

---

## Handling Responses

The tool automatically formats results:

```markdown
The current Bitcoin price is approximately $45,000 USD...

**Sources:**
- [1] https://coinmarketcap.com
- [2] https://finance.yahoo.com

*Response time: 150ms*
```

---

## Environment Variables

```bash
export AISEARCH_API_KEY="your-api-key"
```

In Python:

```python
import os
from crewai_aisearchapi import AISearchTool

tool = AISearchTool(api_key=os.getenv("AISEARCH_API_KEY"))
```

---

## Development (for contributors)

```bash
git clone https://github.com/aisearchapi/crewai-aisearchapi.git
cd crewai-aisearchapi
python -m venv venv
source venv/bin/activate
pip install -e ".[dev,test]"
pytest
```

---

## License

MIT License - see the [LICENSE](LICENSE) file.

---

## Support

- **Dashboard & API Key**: [AI Search API Dashboard](https://app.aisearchapi.io/dashboard)  
- **Docs**: [docs.aisearchapi.io](https://docs.aisearchapi.io/)  
- **Homepage**: [aisearchapi.io](https://aisearchapi.io?utm_source=github)  
- **Issues**: [GitHub Issues](https://github.com/aisearchapi/crewai-aisearchapi/issues)  
