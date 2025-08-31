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
class PoemCrew:
    """Poem Squad"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.jaygoga_orchestra.v1.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.jaygoga_orchestra.v1.com/concepts/tasks#yaml-configuration-recommended
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # If you would lik to add tools to your squad, you can learn more about it here:
    # https://docs.jaygoga_orchestra.v1.com/concepts/agents#agent-tools
    @agent
    def poem_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["poem_writer"],  # type: ignore[index]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.jaygoga_orchestra.v1.com/concepts/tasks#overview-of-a-task
    @task
    def write_poem(self) -> Task:
        return Task(
            config=self.tasks_config["write_poem"],  # type: ignore[index]
        )

    @squad
    def squad(self) -> Squad:
        """Creates the Research Squad"""
        # To learn how to add knowledge sources to your squad, check out the documentation:
        # https://docs.jaygoga_orchestra.v1.com/concepts/knowledge#what-is-knowledge

        return Squad(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
