import asyncio
import jaygoga_orchestra

async def main():
    # Using the quick_start helper for simple workflows
    
    # Create agents using the new LLM format
    analyst = aiflow.Agent(
        name="MarketAnalyst",
        description="Financial market analysis expert",
        llm={
            "model_provider": "openai",
            "model_name": "gpt-4o-mini"
        }
    )

    reporter = aiflow.Agent(
        name="Reporter",
        description="Financial news reporter",
        llm={
            "model_provider": "google",
            "model_name": "gemini-2.0-flash-exp"
        }
    )
    
    # Create simple tasks
    analysis_task = aiflow.Task(
        description="Analyze current cryptocurrency market trends",
        agent=analyst,
        expected_output="Market analysis"
    )
    
    report_task = aiflow.Task(
        description="Write a news report based on the market analysis",
        agent=reporter,
        depends_on=[analysis_task],
        context_from=[analysis_task],
        expected_output="News report"
    )
    
    # Use quick_start for simplified execution
    print("Using AIFlow quick_start helper...")
    
    results = await aiflow.quick_start(
        agents=[analyst, reporter],
        tasks=[analysis_task, report_task],
        stream=True,
        session_name="crypto_market_report"
    )
    
    if results["success"]:
        print("Quick start workflow completed!")
        print(f"Execution time: {results['execution_time']:.2f}s")
        print(f"Tasks completed: {len(results['task_results'])}")
        
        # Access individual task results
        for task_id, result in results["task_results"].items():
            agent_name = result["agent_name"]
            success = result["success"]
            print(f"- {agent_name}: {'✓' if success else '✗'}")

if __name__ == "__main__":
    asyncio.run(main())
