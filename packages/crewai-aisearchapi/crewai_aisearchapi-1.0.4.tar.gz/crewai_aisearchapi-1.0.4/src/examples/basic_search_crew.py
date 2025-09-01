"""
Basic example of using AI Search API with CrewAI
"""

import os
from crewai import Agent, Task, Crew
from crewai_aisearchapi import aisearch_tool

# Create the search tool
search_tool = aisearch_tool(api_key=os.getenv('AISEARCHAPI_API_KEY'))

# Create a research agent
researcher = Agent(
    role='Research Analyst',
    goal='Find accurate and comprehensive information on topics',
    backstory='You are an expert researcher skilled at finding and synthesizing information.',
    tools=[search_tool],
    verbose=True
)

# Create a research task
research_task = Task(
    description='Research the latest developments in quantum computing and its applications',
    expected_output='A comprehensive report on quantum computing with recent developments and applications',
    agent=researcher
)

# Create and run the crew
crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=True
)

# Execute the crew
result = crew.kickoff()
print(result)