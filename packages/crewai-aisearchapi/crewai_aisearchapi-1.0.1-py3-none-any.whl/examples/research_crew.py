"""
Advanced research crew with multiple specialized agents
"""

import os
from crewai import Agent, Task, Crew, Process
from crewai_aisearchapi import aisearch_tool, create_fact_checker_tool

# Initialize tools
general_search = aisearch_tool(api_key=os.getenv('AISEARCHAPI_API_KEY'))
fact_checker = create_fact_checker_tool(api_key=os.getenv('AISEARCHAPI_API_KEY'))

# Create specialized agents
lead_researcher = Agent(
    role='Lead Research Analyst',
    goal='Coordinate research and ensure comprehensive coverage of topics',
    backstory='Senior researcher with expertise in synthesizing complex information.',
    tools=[general_search],
    verbose=True
)

fact_verifier = Agent(
    role='Fact Verification Specialist',
    goal='Verify all claims and ensure accuracy of information',
    backstory='Detail-oriented analyst focused on fact-checking and source verification.',
    tools=[fact_checker],
    verbose=True
)

report_writer = Agent(
    role='Technical Writer',
    goal='Create clear, well-structured reports from research findings',
    backstory='Expert writer skilled at presenting complex information clearly.',
    verbose=True
)

# Define tasks
initial_research = Task(
    description="""
    Research the topic of renewable energy storage solutions.
    Focus on:
    1. Current technologies (batteries, hydrogen, pumped hydro)
    2. Recent breakthroughs and innovations
    3. Economic viability and costs
    4. Environmental impact
    """,
    expected_output='Comprehensive research notes on renewable energy storage',
    agent=lead_researcher
)

verification = Task(
    description="""
    Review the research findings and verify all key claims.
    Check for:
    1. Accuracy of technical specifications
    2. Validity of cost estimates
    3. Credibility of sources
    4. Recent updates or corrections
    """,
    expected_output='Fact-checked and verified research with source citations',
    agent=fact_verifier
)

final_report = Task(
    description="""
    Create a professional report on renewable energy storage solutions.
    The report should include:
    1. Executive summary
    2. Technology overview
    3. Comparative analysis
    4. Future outlook
    5. References and sources
    """,
    expected_output='Professional report on renewable energy storage solutions',
    agent=report_writer
)

# Create the crew
research_crew = Crew(
    agents=[lead_researcher, fact_verifier, report_writer],
    tasks=[initial_research, verification, final_report],
    process=Process.sequential,
    verbose=True
)

# Execute the research
result = research_crew.kickoff()
print(result)