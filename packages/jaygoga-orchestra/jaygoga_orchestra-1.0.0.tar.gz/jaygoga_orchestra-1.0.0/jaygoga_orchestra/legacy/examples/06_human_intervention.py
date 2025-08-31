import asyncio
import jaygoga_orchestra

async def main():
    # Create creative agent
    creative_agent = aiflow.Agent(
        name="CreativeDirector",
        description="Creative director for marketing campaigns",
        llm={
            "model_provider": "anthropic",
            "model_name": "claude-3-5-sonnet-20241022"
        }
    )
    
    # Create tasks that may need human input
    concept_task = aiflow.Task(
        description="Develop creative concepts for a new product launch campaign",
        agent=creative_agent,
        expected_output="Creative campaign concepts"
    )
    
    refinement_task = aiflow.Task(
        description="Refine the campaign concept based on feedback",
        agent=creative_agent,
        depends_on=[concept_task],
        context_from=[concept_task],
        expected_output="Refined campaign concept"
    )
    
    # Enable human intervention
    team = aiflow.Team(
        agents=[creative_agent],
        tasks=[concept_task, refinement_task],
        session_name="creative_campaign",
        enable_human_intervention=True,
        save_work_log=True
    )
    
    print("Starting creative campaign development...")
    print("Press 'i' during execution for human intervention")
    print("You can provide feedback, guidance, or modifications")
    
    results = await team.async_go(stream=True)
    
    if results["success"]:
        print("Creative campaign completed with human collaboration!")
        
        # Show intervention history
        interventions = team.get_human_interventions()
        if interventions:
            print(f"Human interventions: {len(interventions)}")
            for intervention in interventions:
                print(f"- {intervention['type']}: {intervention['response']}")
        else:
            print("No human interventions were made")
    
    await team.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
