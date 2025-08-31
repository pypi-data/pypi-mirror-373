import asyncio
import jaygoga_orchestra

async def main():
    # Create a single agent with new LLM format
    agent = aiflow.Agent(
        name="Writer",
        description="Professional content writer",
        llm={
            "model_provider": "google",
            "model_name": "gemini-2.0-flash-exp"  # Latest experimental model
        },
    )
    
    # Create a simple task
    task = aiflow.Task(
        description="Write a short blog post about the benefits of AI automation",
        agent=agent,
        expected_output="A 200-word blog post"
    )
    
    # Create team and execute
    team = aiflow.Team(
        agents=[agent],
        tasks=[task],
        session_name="basic_writing"
    )
    
    results = await team.async_go(stream=True)
    
    if results["success"]:
        print("Task completed successfully!")
        print(f"Execution time: {results['execution_time']:.2f}s")
    
    await team.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
