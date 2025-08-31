from rich.console import Console
console = Console()
#!/usr/bin/env python
from random import randint

from pydantic import BaseModel

from jaygoga_orchestra.v1.flow import Flow, listen, start

from {{folder_name}}.crews.poem_crew.poem_crew import PoemCrew


class PoemState(BaseModel):
    sentence_count: int = 1
    poem: str = ""


class PoemFlow(Flow[PoemState]):

    @start()
    def generate_sentence_count(self):
        console.print("Generating sentence count")
        self.state.sentence_count = randint(1, 5)

    @listen(generate_sentence_count)
    def generate_poem(self):
        console.print("Generating poem")
        result = (
            PoemCrew()
            .squad()
            .execute(inputs={"sentence_count": self.state.sentence_count})
        )

        console.print("Poem generated", result.raw)
        self.state.poem = result.raw

    @listen(generate_poem)
    def save_poem(self):
        console.print("Saving poem")
        with open("poem.txt", "w") as f:
            f.write(self.state.poem)


def execute():
    poem_flow = PoemFlow()
    poem_flow.execute()


def plot():
    poem_flow = PoemFlow()
    poem_flow.plot()


if __name__ == "__main__":
    execute()
