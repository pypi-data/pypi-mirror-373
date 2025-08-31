#!/usr/bin/env python3

import asyncio
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from jaygoga_orchestra.core.agent import Agent
from jaygoga_orchestra.core.task import Task
from jaygoga_orchestra.core.team import Team

os.environ["GOOGLE_API_KEY"] = "your-google-api-key-here"

async def create_product_launch_team():
    # Market Researcher
    market_researcher = Agent(
        name="Market Researcher",
        role="Market Analysis Specialist",
        goal="Analyze market conditions and target audience",
        backstory="Expert market researcher who identifies opportunities, analyzes competition, and understands customer needs",
        config={
            "llm": {
                "model_name": "gemini-2.5-flash",
                "temperature": 0.3,
                "max_tokens": 2000
            }
        }
    )
    
    # Marketing Strategist
    marketing_strategist = Agent(
        name="Marketing Strategist",
        role="Marketing Strategy Expert",
        goal="Develop comprehensive marketing strategies",
        backstory="Strategic marketing professional who creates effective go-to-market strategies and campaigns",
        config={
            "llm": {
                "model_name": "gemini-2.5-flash",
                "temperature": 0.5,
                "max_tokens": 2500
            }
        }
    )
    
    # Content Creator
    content_creator = Agent(
        name="Content Creator",
        role="Marketing Content Specialist",
        goal="Create compelling marketing content",
        backstory="Creative content specialist who produces engaging marketing materials across multiple channels",
        config={
            "llm": {
                "model_name": "gemini-2.5-flash",
                "temperature": 0.7,
                "max_tokens": 3000
            }
        }
    )
    
    # Launch Coordinator
    launch_coordinator = Agent(
        name="Launch Coordinator",
        role="Project Management Specialist",
        goal="Coordinate and plan product launch execution",
        backstory="Experienced project manager who ensures smooth product launches with proper timing and coordination",
        config={
            "llm": {
                "model_name": "gemini-2.5-flash",
                "temperature": 0.4,
                "max_tokens": 2000
            }
        }
    )
    
    return [market_researcher, marketing_strategist, content_creator, launch_coordinator]

async def create_launch_tasks(product_name: str, product_type: str):
    # Market Research Task
    research_task = Task(
        description=f"Conduct comprehensive market research for '{product_name}', a {product_type}. Analyze target audience, market size, competition, pricing strategies, and identify key market opportunities and challenges.",
        expected_output="Detailed market research report with target audience analysis, competitive landscape, market opportunities, and strategic recommendations",
        agent_name="Market Researcher"
    )
    
    # Marketing Strategy Task
    strategy_task = Task(
        description=f"Develop a comprehensive marketing strategy for launching '{product_name}'. Include positioning, messaging, channel strategy, budget allocation, and success metrics based on the market research.",
        expected_output="Complete marketing strategy document with positioning, messaging framework, channel mix, timeline, and KPIs",
        agent_name="Marketing Strategist",
        dependencies=[research_task.id]
    )
    
    # Content Creation Task
    content_task = Task(
        description=f"Create compelling marketing content for '{product_name}' launch. Include website copy, social media posts, email campaigns, press releases, and promotional materials aligned with the marketing strategy.",
        expected_output="Complete set of marketing materials including website copy, social media content, email templates, and press materials",
        agent_name="Content Creator",
        dependencies=[strategy_task.id]
    )
    
    # Launch Plan Task
    launch_task = Task(
        description=f"Create a detailed launch plan for '{product_name}' incorporating the marketing strategy and content. Include timeline, resource allocation, risk management, and coordination requirements.",
        expected_output="Comprehensive launch plan with detailed timeline, resource requirements, risk mitigation strategies, and success metrics",
        agent_name="Launch Coordinator",
        dependencies=[strategy_task.id, content_task.id]
    )
    
    return [research_task, strategy_task, content_task, launch_task]

async def run_product_launch_planning(product_name: str, product_type: str):
    print(f"🚀 Starting product launch planning")
    print(f"Product: {product_name}")
    print(f"Type: {product_type}")
    
    # Create agents and tasks
    agents = await create_product_launch_team()
    tasks = await create_launch_tasks(product_name, product_type)
    
    # Create team
    team = Team(
        name="Product Launch Team",
        agents=agents,
        tasks=tasks,
        session_name=f"launch_{product_name.replace(' ', '_').lower()}"
    )
    
    # Execute team
    results = await team.run(stream=True)
    
    print(f"✅ Product launch planning completed!")
    print(f"📄 Results saved to: results.md")
    
    return results

async def main():
    product_examples = [
        ("EcoSmart Water Bottle", "Smart Consumer Product"),
        ("CloudSync Pro", "SaaS Platform"),
        ("FitTracker Elite", "Wearable Device"),
        ("GreenEnergy Home Kit", "Renewable Energy Solution"),
        ("CodeMaster AI", "Developer Tool")
    ]
    
    print("🎯 Product Launch Planning Team Demo")
    print("Choose a product to plan launch for:")
    
    for i, (name, type_) in enumerate(product_examples, 1):
        print(f"{i}. {name} ({type_})")
    
    print("6. Custom product")
    
    try:
        choice = int(input("Enter choice (1-6): "))
        
        if 1 <= choice <= 5:
            product_name, product_type = product_examples[choice - 1]
        elif choice == 6:
            product_name = input("Enter product name: ").strip()
            product_type = input("Enter product type: ").strip()
            if not product_name or not product_type:
                print("Product name and type are required")
                return
        else:
            print("Invalid choice")
            return
        
        await run_product_launch_planning(product_name, product_type)
        
    except ValueError:
        print("Please enter a valid number")

if __name__ == "__main__":
    asyncio.run(main())
