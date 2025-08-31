#!/usr/bin/env python3

from jaygoga_orchestra import CrewAgent as Agent, CrewTask as Task, Squad, Process
import os

# Set up your LLM (OpenAI API key required)
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"

# Define the Research Agent
research_agent = Agent(
    role='Market Research Specialist',
    goal='Conduct thorough research on trending topics and market insights',
    backstory="""You are an experienced market researcher with 10+ years of experience 
    in analyzing industry trends, consumer behavior, and market dynamics. You excel at 
    finding reliable data sources and extracting actionable insights.""",
    verbose=True,
    allow_delegation=False,
    tools=[]  # Add web search tools if available
)

# Define the Content Strategist Agent
content_strategist = Agent(
    role='Content Strategy Expert',
    goal='Develop comprehensive content strategies and outlines based on research',
    backstory="""You are a seasoned content strategist who has worked with Fortune 500 
    companies to develop engaging content that drives traffic and conversions. You understand 
    SEO, audience psychology, and content marketing best practices.""",
    verbose=True,
    allow_delegation=False
)

# Define the Writer Agent
writer_agent = Agent(
    role='Senior Content Writer',
    goal='Create engaging, well-structured, and SEO-optimized blog content',
    backstory="""You are a professional writer with expertise in creating compelling 
    blog posts across various industries. You have a talent for making complex topics 
    accessible and engaging while maintaining professional quality.""",
    verbose=True,
    allow_delegation=False
)

# Define the Editor Agent
editor_agent = Agent(
    role='Editorial Quality Specialist',
    goal='Review, edit, and optimize content for quality, clarity, and engagement',
    backstory="""You are a meticulous editor with an eye for detail and a deep 
    understanding of what makes content effective. You ensure all content meets 
    high editorial standards while optimizing for readability and SEO.""",
    verbose=True,
    allow_delegation=False
)

# Define Tasks
research_task = Task(
    description="""Research the latest trends in AI and automation for small businesses in 2024-2025. 
    Focus on:
    1. Current adoption rates and challenges
    2. Most popular AI tools and their use cases
    3. ROI and cost-benefit analysis
    4. Future predictions for the next 2 years
    
    Provide detailed findings with specific statistics and examples.""",
    agent=research_agent,
    expected_output="A comprehensive research report with key findings, statistics, and trend analysis"
)

strategy_task = Task(
    description="""Based on the research findings, create a content strategy and detailed outline for a blog post about 
    'AI Automation for Small Businesses: A 2025 Guide'. The strategy should include:
    1. Target audience analysis
    2. SEO keyword strategy
    3. Content structure and flow
    4. Key talking points and value propositions
    5. Call-to-action recommendations
    
    Ensure the content will appeal to small business owners who may be AI-hesitant.""",
    agent=content_strategist,
    expected_output="A detailed content strategy document with blog post outline and SEO recommendations",
    context=[research_task]
)

writing_task = Task(
    description="""Write a comprehensive 2000-word blog post following the content strategy and outline provided. 
    The blog post should be:
    1. Engaging and accessible to small business owners
    2. Well-structured with clear headings and subheadings
    3. Include practical examples and actionable advice
    4. Incorporate the identified keywords naturally
    5. Include a compelling introduction and strong conclusion
    
    Write in a conversational yet professional tone.""",
    agent=writer_agent,
    expected_output="A complete, well-written blog post ready for publication",
    context=[research_task, strategy_task]
)

editing_task = Task(
    description="""Review and edit the blog post for:
    1. Grammar, spelling, and punctuation
    2. Content flow and readability
    3. SEO optimization
    4. Fact-checking and accuracy
    5. Engagement and call-to-action effectiveness
    
    Provide the final polished version along with a brief editorial summary of changes made.""",
    agent=editor_agent,
    expected_output="A polished, publication-ready blog post with editorial notes",
    context=[writing_task],
    output_file="final_blog_post.md"
)

# Create the Squad
blog_crew = Squad(
    agents=[research_agent, content_strategist, writer_agent, editor_agent],
    tasks=[research_task, strategy_task, writing_task, editing_task],
    process=Process.sequential,
    verbose=2,
    output_log_file="crew_execution_log.md"
)

# Execute the workflow
if __name__ == "__main__":
    print("🚀 Starting AIFlow Blog Generation Workflow...")
    print("=" * 60)
    
    result = blog_crew.execute()
    
    print("\n" + "=" * 60)
    print("✅ Blog Generation Complete!")
    print("=" * 60)
    print(result)
