import asyncio
import jaygoga_orchestra

async def main():
    # Create agents that will communicate
    product_manager = aiflow.Agent(
        name="ProductManager",
        description="Product strategy and requirements expert",
        llm={
            "model_provider": "openai",
            "model_name": "gpt-4o"
        }
    )

    developer = aiflow.Agent(
        name="Developer",
        description="Senior software developer and architect",
        llm={
            "model_provider": "google",
            "model_name": "gemini-2.0-flash-exp"
        }
    )

    designer = aiflow.Agent(
        name="Designer",
        description="UX/UI designer focused on user experience",
        llm={
            "model_provider": "anthropic",
            "model_name": "claude-3-5-haiku-20241022"
        }
    )
    
    # Tasks that encourage agent communication
    requirements_task = aiflow.Task(
        description="Define product requirements for a mobile app. Communicate with Developer and Designer to gather technical and design constraints.",
        agent=product_manager,
        expected_output="Product requirements document"
    )
    
    architecture_task = aiflow.Task(
        description="Design technical architecture. Discuss with ProductManager about requirements and Designer about UI constraints.",
        agent=developer,
        depends_on=[requirements_task],
        expected_output="Technical architecture plan"
    )
    
    design_task = aiflow.Task(
        description="Create UX/UI design. Collaborate with ProductManager on user needs and Developer on technical feasibility.",
        agent=designer,
        depends_on=[requirements_task],
        expected_output="UX/UI design specifications"
    )
    
    # Enable agent conversations
    team = aiflow.Team(
        agents=[product_manager, developer, designer],
        tasks=[requirements_task, architecture_task, design_task],
        session_name="app_development",
        enable_agent_conversations=True,
        parallel_execution=True,
        save_work_log=True
    )
    
    print("Starting collaborative app development...")
    print("Agents will communicate with each other during execution")
    
    results = await team.async_go(stream=True)
    
    if results["success"]:
        print("Collaborative development completed!")
        
        # Show agent conversations
        conversations = team.get_agent_conversations()
        if conversations:
            print(f"Agent conversations: {len(conversations)}")
            for conv in conversations:
                print(f"- {conv['from_agent_name']} → {conv['to_agent_name']}: {conv['message'][:50]}...")
        else:
            print("No agent conversations occurred")
    
    await team.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
