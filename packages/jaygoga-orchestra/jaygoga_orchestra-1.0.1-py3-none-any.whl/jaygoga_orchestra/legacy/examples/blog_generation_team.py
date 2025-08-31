#!/usr/bin/env python3

import asyncio
import os
from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from jaygoga_orchestra.core.agent import Agent
from jaygoga_orchestra.core.task import Task
from jaygoga_orchestra.core.team import Team
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def create_blog_team(model_name: str = "gpt-4o-mini"):
    """Create blog generation team with specified model."""

    researcher = Agent(
        name="Content Researcher",
        role="Research Specialist",
        goal="Research comprehensive information about given topics",
        backstory="Expert researcher with ability to gather accurate, up-to-date information from multiple sources",
        config={
            "llm": {
                "model_name": model_name,
                "temperature": 0.3,
                "max_tokens": 2000
            }
        }
    )

    writer = Agent(
        name="Blog Writer",
        role="Content Creator",
        goal="Create engaging, well-structured blog posts",
        backstory="Professional content writer specializing in creating compelling blog posts that engage readers",
        config={
            "llm": {
                "model_name": model_name,
                "temperature": 0.7,
                "max_tokens": 3000
            }
        }
    )

    editor = Agent(
        name="Content Editor",
        role="Editorial Specialist",
        goal="Review and improve content quality",
        backstory="Experienced editor focused on improving readability, grammar, and overall content quality",
        config={
            "llm": {
                "model_name": model_name,
                "temperature": 0.2,
                "max_tokens": 2000
            }
        }
    )

    return [researcher, writer, editor]

def create_blog_tasks(topic: str):
    """Create blog generation tasks."""

    research_task = Task(
        description=f"Research comprehensive information about '{topic}'. Include latest trends, statistics, expert opinions, and relevant case studies. Focus on accuracy and current information.",
        expected_output="Detailed research report with key findings, statistics, trends, and credible sources",
        agent_name="Content Researcher"
    )

    writing_task = Task(
        description=f"Using the research findings, write a comprehensive blog post about '{topic}'. Include engaging introduction, well-structured body with subheadings, practical examples, and compelling conclusion. Target 1500-2000 words.",
        expected_output="Complete blog post with engaging content, proper structure, and practical value for readers",
        agent_name="Blog Writer",
        dependencies=[research_task.id]
    )

    editing_task = Task(
        description="Review and edit the blog post for grammar, readability, flow, and overall quality. Ensure consistent tone and style throughout.",
        expected_output="Polished final blog post with improved grammar, readability, and professional quality",
        agent_name="Content Editor",
        dependencies=[writing_task.id]
    )

    return [research_task, writing_task, editing_task]

async def run_blog_generation(topic: str, model_name: str = "gpt-4o-mini"):
    """Generate blog post with real-time CLI output."""

    console.print(Panel(
        f"[bold cyan]🚀 Blog Generation Starting[/bold cyan]\n\n"
        f"Topic: [yellow]{topic}[/yellow]\n"
        f"Model: [green]{model_name}[/green]",
        title="Blog Generation",
        border_style="cyan"
    ))

    # Create agents and tasks
    agents = create_blog_team(model_name)
    tasks = create_blog_tasks(topic)

    # Create team
    team = Team(
        name="Blog Generation Team",
        agents=agents,
        tasks=tasks,
        session_name=f"blog_{topic.replace(' ', '_').lower()}"
    )

    # Execute team with progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task_progress = progress.add_task("Generating blog post...", total=None)

        results = await team.run(stream=True)

        progress.update(task_progress, description="✅ Blog generation completed!")

    # Save final blog post
    if results and results.get("success"):
        final_content = extract_final_blog(results)
        save_blog_to_file(final_content, topic)

        console.print(Panel(
            f"[bold green]✅ Blog Generation Complete![/bold green]\n\n"
            f"📄 Blog saved to: [cyan]blog_{topic.replace(' ', '_').lower()}.md[/cyan]\n"
            f"📊 Full results: [cyan]results.md[/cyan]",
            title="Success",
            border_style="green"
        ))
    else:
        console.print("[red]❌ Blog generation failed![/red]")

    return results

def extract_final_blog(results):
    """Extract the final blog post from team results."""
    if not results or not results.get("task_results"):
        return "No blog content generated."

    # Get the last task result (should be the edited blog post)
    task_results = results["task_results"]
    final_task_result = None

    for task_id, result in task_results.items():
        if isinstance(result, dict) and result.get("agent_name") == "Content Editor":
            final_task_result = result
            break

    if not final_task_result:
        # Fallback to any content
        for task_id, result in task_results.items():
            if isinstance(result, dict) and result.get("content"):
                final_task_result = result
                break

    return final_task_result.get("content", "No content available") if final_task_result else "No content available"

def save_blog_to_file(content, topic):
    """Save blog content to markdown file."""
    filename = f"blog_{topic.replace(' ', '_').lower()}.md"

    blog_content = f"""# {topic}

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

---

{content}

---

*Generated by AIFlow Blog Generation Team*
"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(blog_content)

async def main():
    """Main function with model selection."""

    console.print(Panel(
        "[bold cyan]🎯 Blog Generation Team[/bold cyan]\n\n"
        "Generate professional blog posts using AI agents",
        title="AIFlow Blog Generator",
        border_style="cyan"
    ))

    # Model selection
    models = {
        "1": ("gpt-4o-mini", "OpenAI GPT-4o Mini (Fast & Cost-effective)"),
        "2": ("gpt-4o", "OpenAI GPT-4o (High Quality)"),
        "3": ("claude-3-5-sonnet-20241022", "Anthropic Claude 3.5 Sonnet"),
        "4": ("gemini-2.5-flash", "Google Gemini 2.5 Flash"),
        "5": ("llama-3.1-70b-versatile", "Groq Llama 3.1 70B")
    }

    console.print("\n[bold]Choose AI Model:[/bold]")
    for key, (model, desc) in models.items():
        console.print(f"{key}. {desc}")

    model_choice = console.input("\nEnter model choice (1-5): ").strip()
    selected_model = models.get(model_choice, ("gpt-4o-mini", "OpenAI GPT-4o Mini"))[0]

    # Topic selection
    topics = [
        "The Future of Artificial Intelligence in Healthcare",
        "Sustainable Technology Trends in 2024",
        "Remote Work Best Practices for Tech Teams",
        "Blockchain Technology and Its Real-World Applications",
        "The Rise of Edge Computing in IoT"
    ]

    console.print("\n[bold]Choose Blog Topic:[/bold]")
    for i, topic in enumerate(topics, 1):
        console.print(f"{i}. {topic}")
    console.print("6. Custom topic")

    try:
        choice = console.input("\nEnter choice (1-6): ").strip()

        if choice == "6":
            topic = console.input("Enter custom topic: ").strip()
            if not topic:
                console.print("[red]Topic cannot be empty![/red]")
                return
        else:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(topics):
                topic = topics[choice_idx]
            else:
                console.print("[red]Invalid choice![/red]")
                return

        await run_blog_generation(topic, selected_model)

    except ValueError:
        console.print("[red]Please enter a valid number![/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Blog generation cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(main())
