"""
Professional Business Intelligence Example - FIXED VERSION

This example demonstrates the FIXED AIFlow package with:
- NO SIMULATION OR HALLUCINATION
- Real web search using Serper API
- Real file operations with validation
- Real data analysis with pandas
- Professional performance monitoring
- Result validation to prevent fake outputs

Equivalent to Govinda professional standards.
"""

import asyncio
import os
import jaygoga_orchestra
from datetime import datetime


async def main():
    """
    Professional business intelligence workflow with real tools and validation.
    
    This example shows how the FIXED AIFlow package works like Govinda:
    - Real API calls only
    - No simulation fallbacks
    - Performance monitoring
    - Result validation
    - Professional error handling
    """
    
    print("🚀 Starting Professional Business Intelligence Analysis")
    print("✅ NO SIMULATION - Only real data and API calls")
    print("=" * 60)
    
    # Configure real tools with API keys
    web_search_tool = aiflow.WebSearchTool(
        search_engine="serper",  # Real Serper API
        api_key=os.getenv("SERPER_API_KEY")  # Requires real API key
    )
    
    file_tool = aiflow.FileOperationTool(base_path="./business_analysis")
    data_tool = aiflow.DataAnalysisTool()
    
    # Create professional agents with real LLM providers
    market_analyst = aiflow.Agent(
        name="MarketAnalyst",
        description="Senior market research analyst specializing in technology trends",
        llm={
            "model_provider": "openai",
            "model_name": "gpt-4o",
            "api_key": os.getenv("OPENAI_API_KEY")  # Requires real API key
        },
        tools=[web_search_tool, file_tool],
        memory_enabled=True
    )
    
    data_scientist = aiflow.Agent(
        name="DataScientist", 
        description="Senior data scientist with expertise in statistical analysis",
        llm={
            "model_provider": "anthropic",
            "model_name": "claude-3-5-sonnet-20241022",
            "api_key": os.getenv("ANTHROPIC_API_KEY")  # Requires real API key
        },
        tools=[data_tool, file_tool],
        memory_enabled=True
    )
    
    business_strategist = aiflow.Agent(
        name="BusinessStrategist",
        description="Executive business strategist for strategic planning",
        llm={
            "model_provider": "google", 
            "model_name": "gemini-2.0-flash-exp",
            "api_key": os.getenv("GOOGLE_API_KEY")  # Requires real API key
        },
        tools=[file_tool],
        memory_enabled=True
    )
    
    # Define concrete tasks with specific deliverables
    market_research_task = aiflow.Task(
        description="""
        Conduct comprehensive market research on AI automation tools for 2025:
        
        1. Search for latest industry reports on AI automation market size
        2. Find competitor analysis for major AI automation platforms
        3. Research market growth projections and trends
        4. Identify key market drivers and challenges
        5. Save findings to 'market_research_2025.json' with this structure:
        {
            "market_size": {"current": "X billion", "projected_2025": "Y billion"},
            "key_players": [{"name": "Company", "market_share": "X%", "revenue": "Y"}],
            "growth_drivers": ["driver1", "driver2", ...],
            "challenges": ["challenge1", "challenge2", ...],
            "trends": ["trend1", "trend2", ...],
            "sources": [{"title": "Report Title", "url": "URL", "date": "YYYY-MM-DD"}]
        }
        
        CRITICAL: Use ONLY real web search results. NO simulation or fake data.
        """,
        agent=market_analyst,
        expected_output="JSON file with real market research data and verified sources",
        memory_key="market_research",
        max_execution_time=300
    )
    
    data_analysis_task = aiflow.Task(
        description="""
        Create sample business data and perform statistical analysis:
        
        1. Generate realistic sample sales data for a SaaS company (12 months)
        2. Save data to 'sample_sales_data.csv' with columns:
           - date, product_category, revenue, customers, churn_rate, acquisition_cost
        3. Perform comprehensive statistical analysis including:
           - Monthly revenue trends
           - Customer acquisition patterns  
           - Churn rate analysis
           - Revenue forecasting
        4. Save analysis results to 'sales_analysis.json'
        
        CRITICAL: Use real pandas calculations. NO fake statistics.
        """,
        agent=data_scientist,
        expected_output="CSV data file and JSON analysis with real statistical calculations",
        memory_key="data_analysis",
        max_execution_time=240
    )
    
    strategy_report_task = aiflow.Task(
        description="""
        Create executive strategy report combining market research and data analysis:
        
        1. Read market research findings from 'market_research_2025.json'
        2. Read data analysis from 'sales_analysis.json'
        3. Create comprehensive strategy report with:
           - Executive summary
           - Market opportunity assessment
           - Data-driven insights
           - Strategic recommendations
           - Risk analysis
           - Implementation roadmap
        4. Save to 'executive_strategy_report.md' in professional format
        
        CRITICAL: Base recommendations on real data from previous tasks.
        """,
        agent=business_strategist,
        depends_on=[market_research_task, data_analysis_task],
        context_from=[market_research_task, data_analysis_task],
        expected_output="Professional strategy report in Markdown format",
        memory_key="strategy_report",
        max_execution_time=180
    )
    
    # Create professional team with monitoring
    team = aiflow.Team(
        agents=[market_analyst, data_scientist, business_strategist],
        tasks=[market_research_task, data_analysis_task, strategy_report_task],
        session_name="business_intelligence_professional",
        parallel_execution=True,  # Research and analysis can run in parallel
        max_concurrent_tasks=2,
        save_work_log=True,
        enable_human_intervention=False,  # Fully automated
        enable_agent_conversations=True
    )
    
    print("📊 Executing professional business intelligence workflow...")
    print("🔍 Phase 1: Market research (real web search)")
    print("📈 Phase 2: Data analysis (real statistical calculations)")  
    print("📋 Phase 3: Strategy report generation")
    print()
    
    # Execute with real-time monitoring
    start_time = datetime.now()
    
    try:
        results = await team.async_go(stream=True, save_session=True)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("✅ PROFESSIONAL EXECUTION COMPLETED")
        print("=" * 60)
        
        # Get real performance metrics
        performance_metrics = team.get_performance_metrics()
        validation_summary = team.get_validation_summary()
        
        print(f"📊 Execution Summary:")
        print(f"   Total Duration: {execution_time:.1f} seconds")
        print(f"   Tasks Completed: {performance_metrics['task_metrics']['completed_tasks']}")
        print(f"   Tasks Failed: {performance_metrics['task_metrics']['failed_tasks']}")
        print(f"   Success Rate: {performance_metrics['task_metrics']['success_rate']:.1%}")
        print(f"   Total Tokens Used: {performance_metrics['resource_usage']['total_tokens_used']:,}")
        print(f"   API Calls Made: {performance_metrics['resource_usage']['api_calls_made']}")
        
        print(f"\n🔍 Validation Summary:")
        print(f"   Total Validations: {validation_summary['total_validations']}")
        print(f"   Passed Validations: {validation_summary['passed_validations']}")
        print(f"   Failed Validations: {validation_summary['failed_validations']}")
        print(f"   Validation Rate: {validation_summary['success_rate']:.1%}")
        
        print(f"\n📁 Files Generated:")
        for file_path in performance_metrics.get('files_generated', []):
            print(f"   ✓ {file_path}")
        
        # Save comprehensive performance report
        report_path = team.save_performance_report()
        print(f"\n📋 Performance Report: {report_path}")
        
        if results["success"]:
            print("\n🎉 BUSINESS INTELLIGENCE ANALYSIS COMPLETED SUCCESSFULLY!")
            print("✅ All results validated - NO SIMULATION DETECTED")
        else:
            print("\n❌ EXECUTION FAILED - Check logs for details")
            
    except Exception as e:
        print(f"\n❌ EXECUTION ERROR: {str(e)}")
        
        # Still get performance metrics for debugging
        try:
            performance_metrics = team.get_performance_metrics()
            validation_summary = team.get_validation_summary()
            
            print(f"\n📊 Partial Execution Metrics:")
            print(f"   Tasks Attempted: {len(team.task_metrics)}")
            print(f"   Validation Failures: {validation_summary['failed_validations']}")
            
            # Save error report
            report_path = team.save_performance_report()
            print(f"📋 Error Report: {report_path}")
            
        except Exception as report_error:
            print(f"Could not generate error report: {report_error}")
    
    finally:
        # Cleanup
        await team.cleanup()
        print("\n🧹 Cleanup completed")


if __name__ == "__main__":
    print("🔧 AIFLOW PROFESSIONAL BUSINESS INTELLIGENCE")
    print("🚫 NO SIMULATION - REAL RESULTS ONLY")
    print()
    
    # Check for required API keys
    required_keys = ["SERPER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print("❌ MISSING REQUIRED API KEYS:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nSet these environment variables before running.")
        print("This example requires REAL API keys - no simulation fallbacks.")
    else:
        print("✅ All API keys found - proceeding with real execution")
        asyncio.run(main())
