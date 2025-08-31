import asyncio
import jaygoga_orchestra

async def main():
    # Advanced workflow with multiple providers and complex dependencies
    
    # Research team
    market_researcher = aiflow.Agent(
        name="MarketResearcher",
        description="Market research and competitive analysis expert",
        llm={
            "model_provider": "openai",
            "model_name": "gpt-4o"
        },
        memory_enabled=True
    )

    tech_researcher = aiflow.Agent(
        name="TechResearcher",
        description="Technology research and innovation analyst",
        llm={
            "model_provider": "google",
            "model_name": "gemini-1.5-pro"
        },
        memory_enabled=True
    )

    # Strategy team
    strategist = aiflow.Agent(
        name="Strategist",
        description="Business strategy and planning expert",
        llm={
            "model_provider": "anthropic",
            "model_name": "claude-3-5-sonnet-20241022"
        },
        memory_enabled=True
    )

    # Execution team
    project_manager = aiflow.Agent(
        name="ProjectManager",
        description="Project management and execution specialist",
        llm={
            "model_provider": "openai",
            "model_name": "gpt-4o-mini"
        },
        memory_enabled=True
    )
    
    # Phase 1: Research (parallel)
    market_research = aiflow.Task(
        description="Conduct comprehensive market research for AI-powered productivity tools",
        agent=market_researcher,
        expected_output="Market research report",
        memory_key="market_data",
        output_format=aiflow.OutputFormat.STRUCTURED_JSON
    )
    
    tech_research = aiflow.Task(
        description="Research latest AI technologies and their applications in productivity",
        agent=tech_researcher,
        expected_output="Technology research report",
        memory_key="tech_data",
        output_format=aiflow.OutputFormat.STRUCTURED_JSON
    )
    
    # Phase 2: Strategy (depends on research)
    strategy_development = aiflow.Task(
        description="Develop comprehensive business strategy based on market and tech research",
        agent=strategist,
        depends_on=[market_research, tech_research],
        context_from=[market_research, tech_research],
        expected_output="Business strategy document",
        memory_key="strategy",
        output_format=aiflow.OutputFormat.MARKDOWN
    )
    
    # Phase 3: Planning (depends on strategy)
    project_planning = aiflow.Task(
        description="Create detailed project plan and roadmap based on the strategy",
        agent=project_manager,
        depends_on=[strategy_development],
        context_from=[strategy_development, market_research, tech_research],
        expected_output="Project roadmap and implementation plan",
        output_format=aiflow.OutputFormat.EXECUTIVE_SUMMARY
    )
    
    # Advanced team configuration
    team = aiflow.Team(
        agents=[market_researcher, tech_researcher, strategist, project_manager],
        tasks=[market_research, tech_research, strategy_development, project_planning],
        session_name="ai_productivity_startup",
        parallel_execution=True,  # Research phase runs in parallel
        max_concurrent_tasks=2,
        save_work_log=True,
        enable_human_intervention=True,
        enable_agent_conversations=True
    )
    
    print("Starting advanced multi-phase workflow...")
    print("Phase 1: Parallel research")
    print("Phase 2: Strategy development")
    print("Phase 3: Project planning")
    print("Press 'i' for human intervention during execution")
    
    results = await team.async_go(stream=True, save_session=True)
    
    if results["success"]:
        print("Advanced workflow completed successfully!")
        print(f"Total execution time: {results['execution_time']:.2f}s")
        print(f"Agents used: {results['metrics']['agents_used']}")
        print(f"Tasks completed: {results['metrics']['completed_tasks']}")
        print(f"Total tokens used: {results['metrics']['total_tokens_used']}")
        
        # Show agent conversations
        conversations = team.get_agent_conversations()
        if conversations:
            print(f"Agent conversations: {len(conversations)}")
        
        # Show human interventions
        interventions = team.get_human_interventions()
        if interventions:
            print(f"Human interventions: {len(interventions)}")
        
        print("Check output.md for complete session results")
        print("Check work log for detailed execution trace")
    
    await team.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
