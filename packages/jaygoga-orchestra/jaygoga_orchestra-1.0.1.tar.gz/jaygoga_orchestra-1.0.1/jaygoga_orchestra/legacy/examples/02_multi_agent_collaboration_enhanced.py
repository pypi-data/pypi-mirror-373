import asyncio
from jaygoga_orchestra import Agent, Task, Team

async def main():
    # Enhanced version with better research simulation and web search guidance
    
    # Create researcher agent with enhanced capabilities
    researcher = Agent(
        name="Researcher",
        description="""Expert renewable energy researcher and data analyst. You have access to comprehensive knowledge about:
        - Solar energy technologies and market trends
        - Wind energy developments and innovations  
        - Energy storage solutions and battery technologies
        - Government policies and investment flows
        - Emerging clean technologies
        
        When conducting research, provide specific data points, statistics, and real-world examples. 
        Structure your findings with clear categories and actionable insights.""",
        llm={
            "model_provider": "google",
            "model_name": "gemini-2.0-flash",
            # Use environment variable: export GOOGLE_API_KEY="your_key_here"
        },
        memory_enabled=True,
        temperature=0.2  # Lower temperature for factual accuracy
    )

    writer = Agent(
        name="Writer",
        description="""Professional content writer specializing in clean energy and sustainability. 
        You excel at transforming technical research into engaging, accessible content for general audiences.
        
        Your writing style:
        - Clear, engaging, and informative
        - Uses compelling headlines and subheadings
        - Includes specific examples and data points
        - Maintains optimistic but realistic tone
        - Follows SEO best practices""",
        llm={
            "model_provider": "google", 
            "model_name": "gemini-2.0-flash",
            # Use environment variable: export GOOGLE_API_KEY="your_key_here"
        },
        memory_enabled=True,
        temperature=0.7  # Higher temperature for creativity
    )

    # Enhanced research task with specific data requirements
    research_task = Task(
        description="""Conduct comprehensive research on renewable energy trends for 2024. 

        **IMPORTANT**: Since you don't have real-time web access, use your extensive training knowledge to provide detailed, realistic information about 2024 renewable energy trends. Focus on:

        🔍 **RESEARCH AREAS**:
        1. **Solar Energy (25% of report)**:
           - Latest efficiency improvements in photovoltaic cells
           - Cost reduction trends and grid parity achievements
           - Major solar installations and capacity additions
           - Emerging technologies (perovskite cells, bifacial panels)

        2. **Wind Energy (25% of report)**:
           - Offshore wind expansion and floating platforms
           - Turbine size and efficiency improvements
           - Grid integration challenges and solutions
           - Regional capacity growth (US, Europe, Asia)

        3. **Energy Storage (20% of report)**:
           - Battery cost reductions and density improvements
           - Grid-scale storage project deployments
           - Alternative storage technologies (pumped hydro, compressed air)
           - Integration with renewable sources

        4. **Policy & Investment (15% of report)**:
           - Government incentives and climate commitments
           - Private investment flows and venture capital
           - International cooperation and agreements
           - Regulatory changes affecting deployment

        5. **Emerging Technologies (15% of report)**:
           - Green hydrogen production and applications
           - Floating solar installations
           - Agrivoltaics and dual-use systems
           - Smart grid and AI integration

        📊 **OUTPUT REQUIREMENTS**:
        - Provide specific statistics and data points for each area
        - Include realistic cost figures and capacity numbers
        - Mention key companies and projects by name
        - Identify regional differences and leading markets
        - Highlight both opportunities and challenges
        - Structure as a comprehensive research report with clear sections

        **Format**: Well-organized research report with executive summary, detailed sections, and key findings.""",
        agent=researcher,
        expected_output="Comprehensive renewable energy research report with specific data and insights",
        memory_key="research_data",
        max_execution_time=300  # 5 minutes for thorough research
    )
    
    writing_task = Task(
        description="""Create an engaging, informative blog post based on the research findings.

        📝 **BLOG POST REQUIREMENTS**:

        **Structure** (800-1000 words):
        1. **Compelling Title**: SEO-friendly, includes "2024" and "renewable energy"
        2. **Hook Introduction** (100 words): Start with striking statistic or trend
        3. **Main Content** (600-700 words): 3-4 key sections covering top trends
        4. **Future Outlook** (100 words): What to expect in coming years
        5. **Conclusion** (100 words): Key takeaways and call-to-action

        **Content Guidelines**:
        - Transform research data into accessible insights
        - Use specific examples and statistics from the research
        - Include compelling subheadings for each major trend
        - Explain why each trend matters to readers
        - Maintain optimistic but realistic tone
        - Add smooth transitions between sections

        **Style Requirements**:
        - Write for educated general audience interested in sustainability
        - Use active voice and engaging language
        - Include numbers and percentages to support points
        - Avoid overly technical jargon
        - Create scannable content with bullet points where appropriate

        **SEO Elements**:
        - Include relevant keywords naturally
        - Use descriptive subheadings
        - Add meta description suggestion at the end

        The blog post should inspire readers about renewable energy progress while providing concrete, actionable information.""",
        agent=writer,
        depends_on=[research_task],
        context_from=[research_task],
        expected_output="Professional, engaging blog post about 2024 renewable energy trends",
        memory_key="blog_post",
        max_execution_time=240  # 4 minutes for writing
    )

    # Create team with optimized settings
    team = Team(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        session_name="renewable_energy_blog_enhanced",
        save_work_log=True,
        enable_agent_conversations=True,
        parallel_execution=False,  # Sequential for dependencies
        max_concurrent_tasks=1
    )
    
    print("🚀 Enhanced Renewable Energy Blog Generation")
    print("=" * 60)
    print("📊 Phase 1: Comprehensive Research (5 min max)")
    print("   - Solar energy trends and innovations")
    print("   - Wind energy developments") 
    print("   - Energy storage breakthroughs")
    print("   - Policy and investment analysis")
    print("   - Emerging technologies")
    print()
    print("✍️  Phase 2: Professional Blog Writing (4 min max)")
    print("   - Engaging title and introduction")
    print("   - Structured content with data")
    print("   - Future outlook and conclusions")
    print("=" * 60)
    
    try:
        results = await team.async_go(stream=True)
        
        if results["success"]:
            print("\n" + "=" * 60)
            print("✅ Blog generation completed successfully!")
            print(f"⏱️  Total execution time: {results['execution_time']:.2f}s")
            print(f"📋 Tasks completed: {results['metrics']['completed_tasks']}")
            
            # Enhanced results display
            if 'task_results' in results:
                research_content = ""
                blog_content = ""
                
                for task_result in results['task_results']:
                    if task_result.agent_name == "Researcher":
                        research_content = task_result.content
                        print(f"\n📊 Research Report Summary:")
                        print("-" * 40)
                        # Show first 300 characters
                        preview = research_content[:300] + "..." if len(research_content) > 300 else research_content
                        print(preview)
                        
                    elif task_result.agent_name == "Writer":
                        blog_content = task_result.content
                        print(f"\n📝 Final Blog Post:")
                        print("-" * 40)
                        # Show first 400 characters
                        preview = blog_content[:400] + "..." if len(blog_content) > 400 else blog_content
                        print(preview)
                
                print("-" * 40)
                print(f"📄 Research report: {len(research_content)} characters")
                print(f"📝 Blog post: {len(blog_content)} characters")
                
        else:
            print("❌ Blog generation failed!")
            if 'error' in results:
                print(f"Error: {results['error']}")
                
    except Exception as e:
        print(f"❌ Execution error: {str(e)}")
        print("💡 Tip: Make sure your GOOGLE_API_KEY environment variable is set")
    
    finally:
        await team.cleanup()

if __name__ == "__main__":
    print("🌱 AIFlow Enhanced Multi-Agent Renewable Energy Blog Generator")
    print("💡 Tip: Set environment variable GOOGLE_API_KEY before running")
    print()
    asyncio.run(main())
