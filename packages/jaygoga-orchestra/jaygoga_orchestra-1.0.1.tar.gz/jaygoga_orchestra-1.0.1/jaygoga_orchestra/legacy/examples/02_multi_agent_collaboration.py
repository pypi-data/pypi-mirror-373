import asyncio
from jaygoga_orchestra import Agent, Task, Team, WebSearchTool

async def main():
    # Create web search tool for real research
    web_search = WebSearchTool(
        search_engine="duckduckgo",
        max_results=5,
        timeout=15
    )

    # Create two agents: one for research and one for writing using Gemini
    # Note: Set GOOGLE_API_KEY environment variable or pass api_key in llm config
    researcher = Agent(
        name="Researcher",
        description="Expert renewable energy researcher with deep knowledge of solar, wind, hydro, geothermal, and emerging clean technologies. Specializes in analyzing market trends, policy impacts, and technological innovations. Uses web search to find current information.",
        llm={
            "model_provider": "google",
            "model_name": "gemini-2.0-flash",
            # Remove hardcoded API key - use environment variable instead
            # "api_key": os.getenv("GOOGLE_API_KEY")  # Uncomment if needed
        },
        memory_enabled=True,
        tools=[web_search],  # Add web search capability
        temperature=0.3  # Lower temperature for more factual research
    )

    writer = Agent(
        name="Writer",
        description="Professional blog writer specializing in clean energy and sustainability topics. Creates engaging, informative content for general audiences while maintaining technical accuracy.",
        llm={
            "model_provider": "google",
            "model_name": "gemini-2.0-flash",
            # Remove hardcoded API key - use environment variable instead
            # "api_key": os.getenv("GOOGLE_API_KEY")  # Uncomment if needed
        },
        memory_enabled=True,
        temperature=0.7  # Higher temperature for more creative writing
    )

    # Create tasks for research and writing with detailed descriptions
    research_task = Task(
        description="""Conduct comprehensive research on renewable energy trends for 2024. Use web search to find current information on:

1. **Solar Energy**: Latest photovoltaic technologies, efficiency improvements, cost reductions, and major installations
   - Search for: "solar energy trends 2024", "photovoltaic efficiency 2024", "solar installations 2024"

2. **Wind Energy**: Offshore wind developments, turbine innovations, capacity additions globally
   - Search for: "wind energy developments 2024", "offshore wind projects 2024", "wind turbine innovations"

3. **Energy Storage**: Battery technology advances, grid-scale storage projects, cost trends
   - Search for: "battery storage technology 2024", "grid scale energy storage", "battery cost trends 2024"

4. **Policy & Investment**: Government incentives, climate policies, private investment flows
   - Search for: "renewable energy policy 2024", "clean energy investment 2024", "climate policy updates"

5. **Emerging Technologies**: Green hydrogen, floating solar, vertical axis wind turbines
   - Search for: "green hydrogen projects 2024", "floating solar technology", "renewable energy innovations 2024"

**Instructions**:
- Use TOOL_CALL: web_search(query="your search query") to search for current information
- Perform multiple searches to cover all areas thoroughly
- Compile findings into a comprehensive research report with specific data, statistics, and examples
- Include sources and key insights for each category""",
        agent=researcher,
        expected_output="Comprehensive research report with data, trends, and insights across all renewable energy sectors",
        memory_key="research_data"
    )

    writing_task = Task(
        description="""Write an engaging 800-1000 word blog post based on the research findings. The blog post should:

1. **Title**: Create a compelling, SEO-friendly title
2. **Introduction**: Hook readers with a striking statistic or trend
3. **Main Sections**:
   - Cover 3-4 key renewable energy trends from the research
   - Include specific data points and examples
   - Explain why each trend matters
4. **Future Outlook**: What to expect in the coming years
5. **Conclusion**: Summarize key takeaways and call-to-action

**Style Guidelines**:
- Write for a general audience interested in sustainability
- Use clear, accessible language while maintaining accuracy
- Include subheadings for better readability
- Add engaging transitions between sections
- Maintain an optimistic but realistic tone""",
        agent=writer,
        depends_on=[research_task],
        context_from=[research_task],
        expected_output="Well-structured, engaging blog post about renewable energy trends",
        memory_key="blog_post"
    )

    # Execute with team - enhanced configuration
    team = Team(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        session_name="renewable_energy_blog",
        save_work_log=True,
        enable_agent_conversations=True,  # Allow agents to communicate
        parallel_execution=False,  # Sequential execution for dependencies
        max_concurrent_tasks=1  # One task at a time for better output
    )

    print("🚀 Starting renewable energy blog generation...")
    print("📊 Phase 1: Research (this may take a few minutes)")
    print("✍️  Phase 2: Writing blog post")
    print("=" * 60)

    results = await team.async_go(stream=True)

    if results["success"]:
        print("\n" + "=" * 60)
        print("✅ Blog generation completed successfully!")
        print(f"⏱️  Total execution time: {results['execution_time']:.2f}s")
        print(f"📋 Tasks completed: {results['metrics']['completed_tasks']}")

        # Display final results
        if 'task_results' in results:
            for task_id, task_result in results['task_results'].items():
                if task_result.get('agent_name') == "Writer":
                    print(f"\n📝 Final Blog Post Preview:")
                    print("-" * 40)
                    # Show first 200 characters of the blog post
                    content = task_result.get('content', '')
                    preview = content[:200] + "..." if len(content) > 200 else content
                    print(preview)
                    print("-" * 40)
                elif task_result.get('agent_name') == "Researcher":
                    print(f"\n📊 Research Report Preview:")
                    print("-" * 40)
                    content = task_result.get('content', '')
                    preview = content[:300] + "..." if len(content) > 300 else content
                    print(preview)
                    print("-" * 40)
    else:
        print("❌ Blog generation failed!")
        if 'error' in results:
            print(f"Error: {results['error']}")

    await team.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
