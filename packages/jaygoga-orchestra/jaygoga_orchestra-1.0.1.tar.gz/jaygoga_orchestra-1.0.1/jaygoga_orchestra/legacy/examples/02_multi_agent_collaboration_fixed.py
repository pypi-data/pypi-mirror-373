import asyncio
import os
from jaygoga_orchestra import Agent, Task, Team, WebSearchTool

async def main():
    # Create web search tool for real research
    web_search = WebSearchTool(
        search_engine="duckduckgo",
        max_results=3,
        timeout=10
    )
    
    # Create two agents: one for research and one for writing
    # Set your API key: export GOOGLE_API_KEY="your_key_here"
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set!")
        print("💡 Set it with: export GOOGLE_API_KEY='your_key_here'")
        print("🔄 Continuing with demo mode (limited functionality)...")
    
    researcher = Agent(
        name="Researcher",
        description="Expert renewable energy researcher. Uses web search to find current information about solar, wind, energy storage, and clean technology trends.",
        llm={
            "model_provider": "google",
            "model_name": "gemini-2.0-flash",
            "api_key": api_key  # Will use environment variable if available
        },
        memory_enabled=True,
        tools=[web_search],  # Add web search capability
        temperature=0.3  # Lower temperature for factual research
    )

    writer = Agent(
        name="Writer",
        description="Professional blog writer specializing in clean energy topics. Creates engaging, informative content for general audiences.",
        llm={
            "model_provider": "google",
            "model_name": "gemini-2.0-flash",
            "api_key": api_key  # Will use environment variable if available
        },
        memory_enabled=True,
        temperature=0.7  # Higher temperature for creative writing
    )

    # Create research task with web search instructions
    research_task = Task(
        description="""Research renewable energy trends for 2024 using web search. 

**SEARCH STRATEGY**:
1. Search for "renewable energy trends 2024" to get overview
2. Search for "solar energy developments 2024" for solar updates  
3. Search for "wind energy projects 2024" for wind developments
4. Search for "energy storage technology 2024" for storage advances

**INSTRUCTIONS**:
- Use TOOL_CALL: web_search(query="your search query") for each search
- Perform at least 3-4 searches to cover different renewable energy sectors
- Compile findings into a comprehensive research report
- Include specific data, statistics, and recent developments
- Note sources and key insights for each area

**OUTPUT**: Structured research report with current renewable energy trends, data, and insights.""",
        agent=researcher,
        expected_output="Comprehensive research report with current renewable energy data and trends",
        memory_key="research_data",
        max_execution_time=180  # 3 minutes for research
    )
    
    writing_task = Task(
        description="""Write an engaging 600-800 word blog post based on the research findings.

**REQUIREMENTS**:
- Create compelling title with "2024" and "renewable energy"
- Write engaging introduction with striking statistic
- Cover 3-4 key trends from the research with specific data
- Include future outlook section
- End with strong conclusion and call-to-action

**STYLE**:
- Write for educated general audience
- Use clear, accessible language
- Include specific numbers and examples from research
- Maintain optimistic but realistic tone
- Use subheadings for better readability

Transform the research data into an inspiring, informative blog post.""",
        agent=writer,
        depends_on=[research_task],
        context_from=[research_task],
        expected_output="Professional blog post about 2024 renewable energy trends",
        memory_key="blog_post",
        max_execution_time=120  # 2 minutes for writing
    )

    # Create team with optimized settings
    team = Team(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        session_name="renewable_energy_blog_fixed",
        save_work_log=True,
        enable_agent_conversations=True,
        parallel_execution=False,  # Sequential execution
        max_concurrent_tasks=1,
        enable_human_intervention=False  # Disable to avoid UI issues
    )
    
    print("🚀 AIFlow Multi-Agent Blog Generator with Web Search")
    print("=" * 60)
    print("📊 Phase 1: Web Research (up to 3 minutes)")
    print("   - Searching for renewable energy trends")
    print("   - Gathering current data and statistics")
    print("✍️  Phase 2: Blog Writing (up to 2 minutes)")
    print("   - Creating engaging blog post")
    print("   - Incorporating research findings")
    print("=" * 60)
    
    try:
        results = await team.async_go(stream=True)
        
        if results["success"]:
            print("\n" + "=" * 60)
            print("✅ Blog generation completed successfully!")
            print(f"⏱️  Total execution time: {results['execution_time']:.2f}s")
            print(f"📋 Tasks completed: {results['metrics']['completed_tasks']}")
            
            # Display results
            if 'task_results' in results:
                research_content = ""
                blog_content = ""
                
                for _, task_result in results['task_results'].items():
                    agent_name = task_result.get('agent_name', '')
                    content = task_result.get('content', '')
                    
                    if agent_name == "Researcher":
                        research_content = content
                        print(f"\n📊 Research Report Summary:")
                        print("-" * 40)
                        preview = content[:400] + "..." if len(content) > 400 else content
                        print(preview)
                        
                    elif agent_name == "Writer":
                        blog_content = content
                        print(f"\n📝 Final Blog Post:")
                        print("-" * 40)
                        print(content)  # Show full blog post
                
                print("-" * 40)
                print(f"📄 Research: {len(research_content)} characters")
                print(f"📝 Blog post: {len(blog_content)} characters")
                
        else:
            print("❌ Blog generation failed!")
            if 'error' in results:
                print(f"Error: {results['error']}")
                
    except Exception as e:
        print(f"❌ Execution error: {str(e)}")
        if "API key" in str(e) or "authentication" in str(e).lower():
            print("💡 This error is likely due to missing or invalid API key")
            print("   Set GOOGLE_API_KEY environment variable with your Gemini API key")
        else:
            print("💡 Check the error details above for troubleshooting")
    
    finally:
        await team.cleanup()

if __name__ == "__main__":
    print("🌱 AIFlow Enhanced Multi-Agent Blog Generator")
    print("🔧 Features: Real web search, structured research, professional writing")
    print("💡 Tip: Set GOOGLE_API_KEY environment variable for full functionality")
    print()
    asyncio.run(main())
