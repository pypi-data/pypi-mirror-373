import asyncio
import jaygoga_orchestra

async def main():
    # Create specialized agents
    market_analyst = aiflow.Agent(
        name="MarketAnalyst",
        description="Financial market analysis expert",
        llm={
            "model_provider": "openai",
            "model_name": "gpt-4o"
        }
    )

    tech_analyst = aiflow.Agent(
        name="TechAnalyst",
        description="Technology trends analyst",
        llm={
            "model_provider": "google",
            "model_name": "gemini-1.5-pro"
        }
    )

    social_analyst = aiflow.Agent(
        name="SocialAnalyst",
        description="Social media and consumer behavior analyst",
        llm={
            "model_provider": "anthropic",
            "model_name": "claude-3-5-sonnet-20241022"
        }
    )
    
    # Create parallel tasks (no dependencies)
    market_task = aiflow.Task(
        description="Analyze current stock market trends for tech companies",
        agent=market_analyst,
        expected_output="Market analysis report"
    )
    
    tech_task = aiflow.Task(
        description="Analyze emerging technology trends for 2024",
        agent=tech_analyst,
        expected_output="Technology trends report"
    )
    
    social_task = aiflow.Task(
        description="Analyze social media sentiment about AI technology",
        agent=social_analyst,
        expected_output="Social sentiment analysis"
    )
    
    # Execute in parallel
    team = aiflow.Team(
        agents=[market_analyst, tech_analyst, social_analyst],
        tasks=[market_task, tech_task, social_task],
        session_name="parallel_analysis",
        parallel_execution=True,
        max_concurrent_tasks=3
    )
    
    results = await team.async_go(stream=True)
    
    if results["success"]:
        print("Parallel execution completed!")
        print(f"Total execution time: {results['execution_time']:.2f}s")
        print("All analyses completed simultaneously")
    
    await team.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
