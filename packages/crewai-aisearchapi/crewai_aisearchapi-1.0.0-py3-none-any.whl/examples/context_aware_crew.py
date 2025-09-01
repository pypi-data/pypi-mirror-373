"""
Context-aware research crew that maintains conversation history
"""

import os
from crewai import Agent, Task, Crew
from crewai_aisearchapi import AISearchTool, AISearchToolConfig

# Configure tool with context awareness
config = AISearchToolConfig(
    max_context_messages=20,
    verbose=True,
    include_sources=True
)

search_tool = AISearchTool(
    api_key=os.getenv('AISEARCHAPI_API_KEY'),
    config=config
)

# Create an interactive research agent
research_assistant = Agent(
    role='Research Assistant',
    goal='Provide detailed answers while maintaining context of the conversation',
    backstory='An intelligent assistant that remembers previous queries for better context.',
    tools=[search_tool],
    verbose=True
)

# Series of related research tasks
tasks = [
    Task(
        description='What is machine learning?',
        expected_output='Clear explanation of machine learning',
        agent=research_assistant
    ),
    Task(
        description='What are the main types? (referring to the previous topic)',
        expected_output='Types of machine learning with examples',
        agent=research_assistant
    ),
    Task(
        description='Which type is best for image recognition and why?',
        expected_output='Detailed answer about ML type for image recognition',
        agent=research_assistant
    )
]

# Create crew with sequential processing
crew = Crew(
    agents=[research_assistant],
    tasks=tasks,
    process=Process.sequential,
    verbose=True
)

# Execute with context preservation
result = crew.kickoff()
print(result)

# Check remaining balance
balance = search_tool.check_balance()
print(f"\nRemaining credits: {balance.get('available_credits', 'Unknown')}")
