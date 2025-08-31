import asyncio
import jaygoga_orchestra

async def main():
    # Create data analyst agent
    analyst = aiflow.Agent(
        name="DataAnalyst",
        description="Expert data analyst specializing in structured reports",
        llm={
            "model_provider": "google",
            "model_name": "gemini-1.5-pro"
        }
    )
    
    # Task with JSON output format
    json_task = aiflow.Task(
        description="Analyze sales data and provide insights in JSON format with metrics, trends, and recommendations",
        agent=analyst,
        output_format=aiflow.OutputFormat.STRUCTURED_JSON,
        expected_output="Structured JSON analysis"
    )
    
    # Task with markdown output format
    markdown_task = aiflow.Task(
        description="Create a comprehensive report based on the JSON analysis",
        agent=analyst,
        depends_on=[json_task],
        context_from=[json_task],
        output_format=aiflow.OutputFormat.MARKDOWN,
        expected_output="Markdown formatted report"
    )
    
    # Task with executive summary format
    summary_task = aiflow.Task(
        description="Create an executive summary of the analysis",
        agent=analyst,
        depends_on=[markdown_task],
        context_from=[json_task, markdown_task],
        output_format=aiflow.OutputFormat.EXECUTIVE_SUMMARY,
        expected_output="Executive summary"
    )
    
    # Execute with structured outputs
    team = aiflow.Team(
        agents=[analyst],
        tasks=[json_task, markdown_task, summary_task],
        session_name="structured_analysis",
        save_work_log=True
    )
    
    results = await team.async_go(stream=True)
    
    if results["success"]:
        print("Structured output analysis completed!")
        print("Check the work log for formatted outputs")
        
        # Display task results with their formats
        for task_id, task_result in results["task_results"].items():
            output_format = task_result["metadata"].get("output_format", "text")
            print(f"Task format: {output_format}")
    
    await team.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
