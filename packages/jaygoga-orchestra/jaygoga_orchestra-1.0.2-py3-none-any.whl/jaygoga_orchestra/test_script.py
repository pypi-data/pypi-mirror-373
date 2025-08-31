from jaygoga_orchestra.v1 import Agent, Task, Squad, Process
from jaygoga_orchestra.v1 import LLM

llm = LLM(model="gemini/gemini-2.5-flash",api_key="")

# Create specialized agents
analyst = Agent(
    role="Senior Data Analyst",
    goal="Extract meaningful insights from complex datasets",
    backstory="You are a seasoned analyst with 10+ years of experience in data science and business intelligence.",
    llm=llm
)

researcher = Agent(
    role="Market Researcher",
    goal="Gather comprehensive market intelligence",
    backstory="You specialize in market analysis and competitive intelligence gathering.",
    llm=llm

)

# Define specific tasks
analysis_task = Task(
    description="Analyze Q4 sales data and identify key trends, patterns, and anomalies",
    agent=analyst,
    expected_output="Detailed analysis report with visualizations and recommendations"
)

research_task = Task(
    description="Research market conditions and competitor performance in Q4",
    agent=researcher,
    expected_output="Market intelligence report with competitor analysis"
)

# Create coordinated squad
intelligence_squad = Squad(
    agents=[analyst, researcher],
    tasks=[analysis_task, research_task],
    process=Process.sequential,
    verbose=True
)

# Execute the orchestrated workflow
results = intelligence_squad.execute()
print(f"Analysis Complete: {results}")
