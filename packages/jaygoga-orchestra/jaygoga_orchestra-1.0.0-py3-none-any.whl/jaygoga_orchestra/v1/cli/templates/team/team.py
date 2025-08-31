from rich.console import Console
console = Console()
from jaygoga_orchestra.v1 import Agent, Squad, Process, Task
from jaygoga_orchestra.v1.project import CrewBase, agent, squad, task
from jaygoga_orchestra.v1.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the squad starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.jaygoga_orchestra.v1.com/concepts/crews#example-squad-class-with-decorators

@CrewBase
class {{crew_name}}():
    """{{crew_name}} squad"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.jaygoga_orchestra.v1.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.jaygoga_orchestra.v1.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.jaygoga_orchestra.v1.com/concepts/agents#agent-tools
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.jaygoga_orchestra.v1.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )

    @squad
    def squad(self) -> Squad:
        """Creates the {{crew_name}} squad"""
        # To learn how to add knowledge sources to your squad, check out the documentation:
        # https://docs.jaygoga_orchestra.v1.com/concepts/knowledge#what-is-knowledge

        return Squad(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.jaygoga_orchestra.v1.com/how-to/Hierarchical/
        )
