import asyncio
import jaygoga_orchestra

async def main():
    # Create agent with memory enabled
    consultant = aiflow.Agent(
        name="BusinessConsultant",
        description="Expert business strategy consultant",
        llm={
            "model_provider": "openai",
            "model_name": "gpt-4o"
        },
        memory_enabled=True
    )
    
    # First session - gather requirements
    requirements_task = aiflow.Task(
        description="Analyze business requirements for a new e-commerce startup",
        agent=consultant,
        expected_output="Business requirements analysis",
        memory_key="requirements"
    )
    
    team1 = aiflow.Team(
        agents=[consultant],
        tasks=[requirements_task],
        session_name="requirements_gathering"
    )
    
    print("Phase 1: Gathering requirements...")
    await team1.async_go(stream=True)
    
    # Second session - create strategy (agent remembers previous context)
    strategy_task = aiflow.Task(
        description="Create a comprehensive business strategy based on the previous requirements analysis",
        agent=consultant,
        expected_output="Detailed business strategy",
        memory_key="strategy"
    )
    
    team2 = aiflow.Team(
        agents=[consultant],
        tasks=[strategy_task],
        session_name="strategy_development"
    )
    
    print("\nPhase 2: Developing strategy...")
    await team2.async_go(stream=True)
    
    # Third session - implementation plan
    implementation_task = aiflow.Task(
        description="Create an implementation roadmap based on the strategy and requirements",
        agent=consultant,
        expected_output="Implementation roadmap"
    )
    
    team3 = aiflow.Team(
        agents=[consultant],
        tasks=[implementation_task],
        session_name="implementation_planning"
    )
    
    print("\nPhase 3: Implementation planning...")
    results = await team3.async_go(stream=True)
    
    # Show memory summary
    memory_summary = await consultant.get_memory_summary()
    print(f"\nMemory Summary: {memory_summary}")
    
    if results["success"]:
        print("Multi-session workflow completed with persistent memory!")
    
    await team3.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
