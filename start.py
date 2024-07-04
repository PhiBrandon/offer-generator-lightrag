from dotenv import load_dotenv
from lightrag.core.component import Component, Sequential
from lightrag.core.generator import Generator
from lightrag.core.prompt_builder import Prompt
from lightrag.components.model_client import AnthropicAPIClient
from lightrag.components.output_parsers import JsonOutputParser
from dataclasses import dataclass

from lightrag.core.base_data_class import DataClass, field, DataClassFormatType
from lightrag.core.types import GeneratorOutput
from models.models import *
from prompts.offer_prompts import *


@dataclass
class Summary(DataClass):
    summary: str = field(metadata={"desc": "summary of the given text"}, default="")


class SummaryGenerator(Component):
    def __init__(self):
        super().__init__()
        json_parser = JsonOutputParser(data_class=Summary)
        self.generator = Generator(
            model_client=AnthropicAPIClient(),
            model_kwargs={"model": "claude-3-haiku-20240307"},
            prompt_kwargs={"output_format_str": json_parser.format_instructions()},
            output_processors=json_parser,
        )

    def call(self, text: str, model_kwargs: dict = {}) -> Summary:
        response: GeneratorOutput = self.generator.call(
            prompt_kwargs={"input_str": text}, model_kwargs=model_kwargs
        )
        if response.error is None:
            output = Summary.from_dict(response.data)
            return output
        else:
            None


class ProblemGenerator(Component):
    def __init__(self, prompt):
        super().__init__()
        json_parser = JsonOutputParser(data_class=Problems)
        self.prompt = prompt
        self.generator = Generator(
            template=self.prompt,
            model_client=AnthropicAPIClient(),
            model_kwargs={"model": "claude-3-haiku-20240307", "max_tokens": 4000},
            prompt_kwargs={"output_format_str": json_parser.format_instructions()},
            output_processors=json_parser,
        )

    def call(self, text: str, model_kwargs: dict = {}) -> Problems:
        response: GeneratorOutput = self.generator.call(
            prompt_kwargs={"job_description": text}, model_kwargs=model_kwargs
        )
        if response.error is None:
            output = Problems.from_dict(response.data)
            return output
        else:
            None


class SubProblemGenerator(Component):
    def __init__(self, prompt):
        super().__init__()
        json_parser = JsonOutputParser(data_class=SubProblems)
        self.prompt = prompt
        self.generator = Generator(
            template=self.prompt,
            model_client=AnthropicAPIClient(),
            model_kwargs={"model": "claude-3-haiku-20240307", "max_tokens": 4000},
            prompt_kwargs={
                "output_format_str": SubProblems.format_class_str(
                    DataClassFormatType.SIGNATURE_JSON
                )
            },
            output_processors=json_parser,
        )

    def call(self, problems: Problems, model_kwargs: dict = {}) -> SubProblemsOutput:
        sub_problems = []
        for p in problems.problems:
            response: GeneratorOutput = self.generator.call(
                prompt_kwargs={"problem": p.problem}, model_kwargs=model_kwargs
            )
            if response.error is None:
                output = SubProblems.from_dict(response.data)
                sub_problems.append(output)
            else:
                None
        return SubProblemsOutput(problems=problems, subproblems=sub_problems)


class ObjectionGenerator(Component):
    def __init__(self, prompt):
        super().__init__()
        json_parser = JsonOutputParser(data_class=Objections)
        self.prompt = prompt
        self.generator = Generator(
            template=self.prompt,
            model_client=AnthropicAPIClient(),
            model_kwargs={"model": "claude-3-haiku-20240307", "max_tokens": 4000},
            prompt_kwargs={
                "output_format_str": Objections.format_class_str(
                    DataClassFormatType.SIGNATURE_JSON
                )
            },
            output_processors=json_parser,
        )

    def call(
        self,
        input: SubProblemsOutput,
        model_kwargs: dict = {},
    ) -> ObjectionsOutput:
        all_objections = []
        for p, s in zip(input.problems.problems, input.subproblems):
            response: GeneratorOutput = self.generator.call(
                prompt_kwargs={
                    "problem": p.problem,
                    "sub_problems": [sub.sub_problem for sub in s.sub_problems],
                },
                model_kwargs=model_kwargs,
            )
            if response.error is None:
                output = Objections.from_dict(response.data)
                all_objections.append(output)
            else:
                print(response.error)
        return ObjectionsOutput(
            problems=input.problems,
            subproblems=input.subproblems,
            objections=all_objections,
        )


class SolutionsGenerator(Component):
    def __init__(self, prompt):
        super().__init__()
        json_parser = JsonOutputParser(data_class=Solution)
        self.prompt = prompt
        self.generator = Generator(
            template=self.prompt,
            model_client=AnthropicAPIClient(),
            model_kwargs={"model": "claude-3-haiku-20240307", "max_tokens": 4000},
            prompt_kwargs={
                "output_format_str": Solution.format_class_str(
                    DataClassFormatType.SIGNATURE_JSON
                )
            },
            output_processors=json_parser,
        )
    def call(
        self,
        input: ObjectionsOutput,
        model_kwargs: dict = {},
    ) -> OfferGenerationPack:
        all_solutions = []
        for p, s, o in zip(
            input.problems.problems, input.subproblems, input.objections
        ):
            response: GeneratorOutput = self.generator.call(
                prompt_kwargs={
                    "problem": p.problem,
                    "sub_problems": [sub.sub_problem for sub in s.sub_problems],
                    "objections": [obj.objection for obj in o.objections],
                },
                model_kwargs=model_kwargs,
            )
            if response.error is None:
                output = Solution.from_dict(response.data)
                all_solutions.append(output)
            else:
                print(response.error)
        return OfferGenerationPack(problem=input.problems, sub_problems=input.subproblems, objections=input.objections, solutions=all_solutions)
        


# [sub.sub_problem for sub in subs.sub_problems]

seq = Sequential(
    ProblemGenerator(prompt=promblem_template),
    SubProblemGenerator(prompt=sub_problem_template),
    ObjectionGenerator(prompt=objections_template),
    SolutionsGenerator(prompt=solutions_template)
).call("Migrate 1000 servers")
