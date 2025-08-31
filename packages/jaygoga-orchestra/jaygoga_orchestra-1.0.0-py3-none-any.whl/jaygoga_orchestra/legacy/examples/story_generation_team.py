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

async def create_story_team():
    # Plot Creator
    plot_creator = Agent(
        name="Plot Creator",
        role="Story Architect",
        goal="Create compelling story plots and narrative structures",
        backstory="Creative storyteller who excels at developing engaging plots with strong character arcs and narrative tension",
        config={
            "llm": {
                "model_name": "gemini-2.5-flash",
                "temperature": 0.8,
                "max_tokens": 2000
            }
        }
    )
    
    # Character Developer
    character_dev = Agent(
        name="Character Developer",
        role="Character Specialist",
        goal="Create rich, believable characters with depth",
        backstory="Expert in character development who creates memorable characters with realistic motivations and backgrounds",
        config={
            "llm": {
                "model_name": "gemini-2.5-flash",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }
    )
    
    # Story Writer
    story_writer = Agent(
        name="Story Writer",
        role="Narrative Writer",
        goal="Write engaging stories with vivid descriptions",
        backstory="Skilled writer who brings stories to life with compelling prose and engaging dialogue",
        config={
            "llm": {
                "model_name": "gemini-2.5-flash",
                "temperature": 0.8,
                "max_tokens": 4000
            }
        }
    )
    
    # Story Editor
    story_editor = Agent(
        name="Story Editor",
        role="Editorial Specialist",
        goal="Polish stories for maximum impact",
        backstory="Professional editor who enhances story flow, pacing, and overall narrative quality",
        config={
            "llm": {
                "model_name": "gemini-2.5-flash",
                "temperature": 0.3,
                "max_tokens": 2000
            }
        }
    )
    
    return [plot_creator, character_dev, story_writer, story_editor]

async def create_story_tasks(genre: str, theme: str):
    # Plot Development Task
    plot_task = Task(
        description=f"Create a compelling {genre} story plot centered around the theme of '{theme}'. Include main conflict, character motivations, key plot points, and resolution. Ensure the plot has proper pacing and narrative tension.",
        expected_output="Detailed story outline with plot structure, main conflict, key scenes, and character motivations",
        agent_name="Plot Creator"
    )
    
    # Character Development Task
    character_task = Task(
        description=f"Based on the plot, develop rich characters for this {genre} story. Create protagonist, antagonist, and supporting characters with detailed backgrounds, motivations, and character arcs that serve the theme of '{theme}'.",
        expected_output="Complete character profiles with backgrounds, motivations, personality traits, and character development arcs",
        agent_name="Character Developer",
        dependencies=[plot_task.id]
    )
    
    # Story Writing Task
    writing_task = Task(
        description=f"Write a complete {genre} story incorporating the plot and characters. Focus on the theme of '{theme}'. Include vivid descriptions, engaging dialogue, and proper story structure. Target 2000-3000 words.",
        expected_output="Complete story with engaging narrative, dialogue, descriptions, and proper story structure",
        agent_name="Story Writer",
        dependencies=[plot_task.id, character_task.id]
    )
    
    # Story Editing Task
    editing_task = Task(
        description="Edit and polish the story for maximum impact. Improve flow, pacing, dialogue, and overall narrative quality. Ensure consistency and emotional resonance.",
        expected_output="Polished final story with improved flow, pacing, and narrative quality",
        agent_name="Story Editor",
        dependencies=[writing_task.id]
    )
    
    return [plot_task, character_task, writing_task, editing_task]

async def run_story_generation(genre: str, theme: str):
    print(f"📚 Starting story generation")
    print(f"Genre: {genre}")
    print(f"Theme: {theme}")
    
    # Create agents and tasks
    agents = await create_story_team()
    tasks = await create_story_tasks(genre, theme)
    
    # Create team
    team = Team(
        name="Story Generation Team",
        agents=agents,
        tasks=tasks,
        session_name=f"story_{genre}_{theme}".replace(' ', '_').lower()
    )
    
    # Execute team
    results = await team.run(stream=True)
    
    print(f"✅ Story generation completed!")
    print(f"📄 Results saved to: results.md")
    
    return results

async def main():
    genres = ["Science Fiction", "Mystery", "Romance", "Fantasy", "Thriller"]
    themes = ["Redemption", "Love conquers all", "Power corrupts", "Coming of age", "Sacrifice for others"]
    
    print("📖 Story Generation Team Demo")
    
    print("\nChoose a genre:")
    for i, genre in enumerate(genres, 1):
        print(f"{i}. {genre}")
    
    try:
        genre_choice = int(input("Enter genre choice (1-5): ")) - 1
        if not (0 <= genre_choice < len(genres)):
            print("Invalid choice")
            return
        
        print("\nChoose a theme:")
        for i, theme in enumerate(themes, 1):
            print(f"{i}. {theme}")
        
        theme_choice = int(input("Enter theme choice (1-5): ")) - 1
        if not (0 <= theme_choice < len(themes)):
            print("Invalid choice")
            return
        
        selected_genre = genres[genre_choice]
        selected_theme = themes[theme_choice]
        
        await run_story_generation(selected_genre, selected_theme)
        
    except ValueError:
        print("Please enter valid numbers")

if __name__ == "__main__":
    asyncio.run(main())
