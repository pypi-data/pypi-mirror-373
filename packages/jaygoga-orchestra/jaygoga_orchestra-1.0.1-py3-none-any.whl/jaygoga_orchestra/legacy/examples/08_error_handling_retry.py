import asyncio
import jaygoga_orchestra

async def main():
    # Create agent with retry configuration
    resilient_agent = aiflow.Agent(
        name="ResilientAgent",
        description="Agent designed to handle errors gracefully",
        llm={
            "model_provider": "google",
            "model_name": "gemini-2.0-flash-exp"
        },
        retry_attempts=3,
        retry_delay=2.0
    )
    
    # Task that might fail initially
    challenging_task = aiflow.Task(
        description="Analyze complex data that might require multiple attempts",
        agent=resilient_agent,
        expected_output="Data analysis results",
        max_retries=3,
        max_execution_time=60  # 60 second timeout
    )
    
    # Backup task if first fails
    fallback_task = aiflow.Task(
        description="Provide alternative analysis if the primary task fails",
        agent=resilient_agent,
        expected_output="Alternative analysis"
    )
    
    # Error handling callbacks
    async def on_task_error(task, error_message):
        print(f"Task {task.description[:30]}... encountered error: {error_message}")
        print("Attempting recovery...")
    
    async def on_task_retry(task, retry_count):
        print(f"Retrying task {task.description[:30]}... (attempt {retry_count})")
    
    # Configure error handling
    challenging_task.on_error = on_task_error
    challenging_task.on_progress = lambda task, progress, message: print(f"Progress: {progress:.1%} - {message}")
    
    team = aiflow.Team(
        agents=[resilient_agent],
        tasks=[challenging_task, fallback_task],
        session_name="error_handling_demo"
    )
    
    print("Starting error handling demonstration...")
    print("This example shows how AIFlow handles errors and retries")
    
    try:
        results = await team.async_go(stream=True)
        
        if results["success"]:
            print("Tasks completed successfully!")
        else:
            print("Some tasks failed, but system remained stable")
            
        # Show execution metrics
        print(f"Total execution time: {results['execution_time']:.2f}s")
        print(f"Completed tasks: {results['metrics']['completed_tasks']}")
        print(f"Failed tasks: {results['metrics']['failed_tasks']}")
        
    except Exception as e:
        print(f"Team execution failed: {e}")
        print("This demonstrates graceful error handling")
    
    await team.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
