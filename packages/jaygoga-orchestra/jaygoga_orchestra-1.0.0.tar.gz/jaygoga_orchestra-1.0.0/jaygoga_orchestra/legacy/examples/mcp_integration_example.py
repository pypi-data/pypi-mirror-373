"""
AIFlow MCP Integration Example - Professional Implementation

This example demonstrates how AIFlow now supports Model Context Protocol (MCP)
just like Govinda, allowing agents to use tools from external MCP servers.

Features demonstrated:
- Multiple MCP server connections (Stdio, SSE, HTTP)
- Tool filtering and selection
- Professional error handling
- Performance monitoring
- Real-world MCP server integration

Equivalent to Govinda's MCP capabilities.
"""

import asyncio
import os
import jaygoga_orchestra
from jaygoga_orchestra.tools import (
    MCPServerAdapter, 
    StdioServerParameters, 
    SSEServerParameters, 
    StreamableHTTPServerParameters
)


async def main():
    """
    Demonstrate AIFlow's MCP integration capabilities.
    
    Shows how to connect to multiple MCP servers and use their tools
    in a professional multi-agent workflow.
    """
    
    print("🔌 AIFlow MCP Integration Demo")
    print("🚀 Professional Model Context Protocol Support")
    print("=" * 60)
    
    # Configure MCP servers (multiple transports)
    mcp_server_configs = [
        # Stdio Server (local file operations)
        StdioServerParameters(
            command="python3",
            args=["mcp_servers/file_server.py"],
            env={"UV_PYTHON": "3.12", **os.environ}
        ),
        
        # SSE Server (remote database access)
        {
            "url": "http://localhost:8000/sse",
            "transport": "sse",
            "headers": {"Authorization": "Bearer your-token"}
        },
        
        # Streamable HTTP Server (external API integration)
        {
            "url": "http://localhost:8001/mcp",
            "transport": "streamable-http",
            "headers": {"X-API-Key": os.getenv("MCP_API_KEY")}
        }
    ]
    
    # Create agents with different specializations
    file_specialist = aiflow.Agent(
        name="FileSpecialist",
        description="Expert in file operations and data management using MCP tools",
        llm={
            "model_provider": "openai",
            "model_name": "gpt-4o",
            "api_key": os.getenv("OPENAI_API_KEY")
        },
        memory_enabled=True
    )
    
    database_analyst = aiflow.Agent(
        name="DatabaseAnalyst", 
        description="Database specialist using MCP database tools",
        llm={
            "model_provider": "anthropic",
            "model_name": "claude-3-5-sonnet-20241022",
            "api_key": os.getenv("ANTHROPIC_API_KEY")
        },
        memory_enabled=True
    )
    
    api_integrator = aiflow.Agent(
        name="APIIntegrator",
        description="External API integration specialist using MCP HTTP tools",
        llm={
            "model_provider": "google",
            "model_name": "gemini-2.0-flash-exp", 
            "api_key": os.getenv("GOOGLE_API_KEY")
        },
        memory_enabled=True
    )
    
    # Create team with MCP server configuration
    team = aiflow.Team(
        agents=[file_specialist, database_analyst, api_integrator],
        tasks=[],  # Will add tasks after MCP connection
        session_name="mcp_integration_demo",
        mcp_server_params=mcp_server_configs,
        parallel_execution=True,
        max_concurrent_tasks=3,
        save_work_log=True,
        enable_human_intervention=False
    )
    
    try:
        print("🔌 Connecting to MCP servers...")
        
        # Connect to MCP servers
        await team.connect_mcp_servers()
        
        print(f"✅ Connected to {len(team.mcp_adapters)} MCP servers")
        print(f"📦 Total MCP tools available: {len(team.mcp_tools)}")
        
        # Show available tools
        print("\n🛠️  Available MCP Tools:")
        for tool in team.mcp_tools:
            print(f"   - {tool.name}: {tool.description}")
        
        # Assign specific MCP tools to agents
        file_tools = team.get_mcp_tools("read_file", "write_file", "list_directory")
        db_tools = team.get_mcp_tools("query_database", "update_records", "create_table")
        api_tools = team.get_mcp_tools("fetch_data", "send_webhook", "process_api")
        
        # Update agents with MCP tools
        file_specialist.tools.extend(file_tools)
        database_analyst.tools.extend(db_tools)
        api_integrator.tools.extend(api_tools)
        
        print(f"\n👤 Agent Tool Assignments:")
        print(f"   FileSpecialist: {len(file_tools)} MCP tools")
        print(f"   DatabaseAnalyst: {len(db_tools)} MCP tools")
        print(f"   APIIntegrator: {len(api_tools)} MCP tools")
        
        # Create tasks that use MCP tools
        file_task = aiflow.Task(
            description="""
            Use MCP file tools to:
            1. Read configuration files from the project directory
            2. Create a summary report of all configuration settings
            3. Write the summary to 'config_summary.json'
            
            Use only MCP file tools - no built-in file operations.
            """,
            agent=file_specialist,
            expected_output="Configuration summary file created using MCP tools",
            memory_key="file_operations",
            max_execution_time=120
        )
        
        database_task = aiflow.Task(
            description="""
            Use MCP database tools to:
            1. Query user activity data from the last 30 days
            2. Calculate engagement metrics and trends
            3. Create a new table with aggregated results
            
            Use only MCP database tools for all operations.
            """,
            agent=database_analyst,
            expected_output="Database analysis completed with MCP tools",
            memory_key="database_analysis",
            max_execution_time=180
        )
        
        api_task = aiflow.Task(
            description="""
            Use MCP API tools to:
            1. Fetch latest market data from external APIs
            2. Process and validate the data
            3. Send processed results via webhook to reporting system
            
            Use only MCP API tools for external integrations.
            """,
            agent=api_integrator,
            expected_output="API integration completed using MCP tools",
            memory_key="api_integration",
            max_execution_time=150
        )
        
        # Add tasks to team
        team.tasks = {
            task.id: task for task in [file_task, database_task, api_task]
        }
        
        print("\n🚀 Executing MCP-powered workflow...")
        
        # Execute the workflow
        results = await team.async_go(stream=True, save_session=True)
        
        print("\n" + "=" * 60)
        print("✅ MCP INTEGRATION DEMO COMPLETED")
        print("=" * 60)
        
        # Get performance metrics
        performance_metrics = team.get_performance_metrics()
        validation_summary = team.get_validation_summary()
        
        print(f"📊 Execution Summary:")
        print(f"   Tasks Completed: {performance_metrics['task_metrics']['completed_tasks']}")
        print(f"   Success Rate: {performance_metrics['task_metrics']['success_rate']:.1%}")
        print(f"   Total Execution Time: {performance_metrics['execution_summary']['total_duration_seconds']:.1f}s")
        print(f"   MCP Tools Used: {len(team.mcp_tools)}")
        print(f"   MCP Servers Connected: {len(team.mcp_adapters)}")
        
        print(f"\n🔍 Validation Summary:")
        print(f"   Validation Rate: {validation_summary['success_rate']:.1%}")
        print(f"   Failed Validations: {validation_summary['failed_validations']}")
        
        # Show MCP-specific metrics
        print(f"\n🔌 MCP Integration Metrics:")
        mcp_tool_calls = sum(1 for tool in team.mcp_tools if hasattr(tool, 'call_count'))
        print(f"   MCP Tool Calls: {mcp_tool_calls}")
        print(f"   Active MCP Connections: {len([a for a in team.mcp_adapters if a.connected])}")
        
        if results["success"]:
            print("\n🎉 MCP INTEGRATION SUCCESSFUL!")
            print("✅ All MCP tools executed without issues")
            print("✅ Professional MCP server management")
            print("✅ Govinda-equivalent MCP capabilities")
        else:
            print("\n❌ MCP INTEGRATION FAILED")
            print("Check logs for MCP connection or tool execution issues")
            
    except Exception as e:
        print(f"\n❌ MCP INTEGRATION ERROR: {str(e)}")
        
    finally:
        # Always disconnect MCP servers
        print("\n🔌 Disconnecting from MCP servers...")
        await team.disconnect_mcp_servers()
        await team.cleanup()
        print("✅ MCP cleanup completed")


async def demonstrate_mcp_adapter_direct():
    """
    Demonstrate direct MCP adapter usage (like Govinda's MCPServerAdapter).
    """
    print("\n" + "=" * 60)
    print("🔧 Direct MCP Adapter Demo (Govinda Style)")
    print("=" * 60)
    
    # Example 1: Stdio Server
    stdio_params = StdioServerParameters(
        command="python3",
        args=["mcp_servers/calculator.py"],
        env={"UV_PYTHON": "3.12", **os.environ}
    )
    
    try:
        # Use context manager (recommended approach)
        async with MCPServerAdapter(stdio_params, connect_timeout=30) as mcp_tools:
            print(f"📦 Stdio MCP Tools: {[tool.name for tool in mcp_tools]}")
            
            # Use specific tool
            if "calculate" in [tool.name for tool in mcp_tools]:
                calc_tool = mcp_tools["calculate"]
                result = await calc_tool.execute(expression="2 + 2 * 3")
                print(f"🧮 Calculator result: {result}")
                
    except Exception as e:
        print(f"❌ Stdio MCP error: {e}")
    
    # Example 2: HTTP Server with tool filtering
    http_params = {
        "url": "http://localhost:8001/mcp",
        "transport": "streamable-http"
    }
    
    try:
        # Filter to specific tools only
        async with MCPServerAdapter(http_params, "weather", "news", connect_timeout=60) as filtered_tools:
            print(f"📦 Filtered HTTP MCP Tools: {[tool.name for tool in filtered_tools]}")
            
            # Use weather tool if available
            if "weather" in [tool.name for tool in filtered_tools]:
                weather_tool = filtered_tools["weather"]
                result = await weather_tool.execute(location="San Francisco")
                print(f"🌤️  Weather result: {result}")
                
    except Exception as e:
        print(f"❌ HTTP MCP error: {e}")


if __name__ == "__main__":
    print("🔌 AIFLOW MCP INTEGRATION")
    print("🚀 Govinda-Compatible Model Context Protocol Support")
    print()
    
    # Check for MCP server availability
    print("⚠️  MCP Server Requirements:")
    print("   - Local MCP servers running on specified ports")
    print("   - Proper MCP server implementations")
    print("   - Network connectivity for remote servers")
    print()
    
    # Run main demo
    asyncio.run(main())
    
    # Run direct adapter demo
    asyncio.run(demonstrate_mcp_adapter_direct())
