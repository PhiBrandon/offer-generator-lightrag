from src.custom_sequence import CustomSequence
from lightrag.core.model_client import ModelClient
from typing import Dict

# Import necessary libraries and modules
from dotenv import load_dotenv
from lightrag.core.component import Component

from lightrag.components.output_parsers import JsonOutputParser
from lightrag.core.base_data_class import DataClassFormatType
from lightrag.core.types import GeneratorOutput
from src.models import *
from src.offer_prompts import *
from src.custom_generator import CustomGenerator
from src.custom_sequence import CustomSequence
import asyncio


# Define a class for generating problems
class ProblemGenerator(CustomGenerator):
    def __init__(
        self,
        prompt: str,
        model_client: ModelClient,
        model_kwargs: Dict,
        data_class: DataClass,
    ):
        super().__init__(
            model_client=model_client,
            model_kwargs=model_kwargs,
            template=prompt,
            prompt_kwargs={
                "output_format_str": data_class.format_class_str(
                    DataClassFormatType.SIGNATURE_JSON
                )
            },
            output_processors=JsonOutputParser(data_class=data_class),
        )
        # Create a JSON parser for the Solution data class
        # Set up the generator with specific parameters

    # Define the main function to generate problems
    async def call(self, text: str, model_kwargs: dict = {}) -> Problems:
        response: GeneratorOutput = await self.acall(
            prompt_kwargs={"job_description": text}, model_kwargs=model_kwargs
        )
        if response.error is None:
            output = Problems.from_dict(response.data)
            return output
        else:
            print("No output")
            return None


# Define a class for generating sub-problems
class SubProblemGenerator(CustomGenerator):
    def __init__(
        self,
        prompt: str,
        model_client: ModelClient,
        model_kwargs: Dict,
        data_class: DataClass,
    ):
        super().__init__(
            model_client=model_client,
            model_kwargs=model_kwargs,
            template=prompt,
            prompt_kwargs={
                "output_format_str": data_class.format_class_str(
                    DataClassFormatType.SIGNATURE_JSON
                )
            },
            output_processors=JsonOutputParser(data_class=data_class),
        )

    # Define the main function to generate sub-problems
    async def call(
        self, problems: Problems, model_kwargs: dict = {}
    ) -> SubProblemsOutput:
        sub_problems = []

        # Define an inner function to process each problem
        async def process_problem(p):
            response: GeneratorOutput = await self.acall(
                prompt_kwargs={"problem": p.problem}, model_kwargs=model_kwargs
            )
            if response.error is None:
                output = SubProblems.from_dict(response.data)
                sub_problems.append(output)
            else:
                None

        # Process all problems concurrently
        await asyncio.gather(*(process_problem(p) for p in problems.problems))
        return SubProblemsOutput(problems=problems, subproblems=sub_problems)


# Define a class for generating objections
class ObjectionGenerator(CustomGenerator):
    def __init__(
        self,
        prompt: str,
        model_client: ModelClient,
        model_kwargs: Dict,
        data_class: DataClass,
    ):
        super().__init__(
            model_client=model_client,
            model_kwargs=model_kwargs,
            template=prompt,
            prompt_kwargs={
                "output_format_str": data_class.format_class_str(
                    DataClassFormatType.SIGNATURE_JSON
                )
            },
            output_processors=JsonOutputParser(data_class=data_class),
        )

    # Define the main function to generate objections
    async def call(
        self,
        input: SubProblemsOutput,
        model_kwargs: dict = {},
    ) -> ObjectionsOutput:
        all_objections = []

        # Define an inner function to process each objection
        async def process_objection(p, s):
            response: GeneratorOutput = await self.acall(
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
                None

        # Process all objections concurrently
        await asyncio.gather(
            *(
                process_objection(p, s)
                for p, s in zip(input.problems.problems, input.subproblems)
            )
        )
        return ObjectionsOutput(
            problems=input.problems,
            subproblems=input.subproblems,
            objections=all_objections,
        )


# Define a class for generating solutions
class SolutionsGenerator(CustomGenerator):
    def __init__(
        self,
        prompt: str,
        model_client: ModelClient,
        model_kwargs: Dict,
        data_class: DataClass,
    ):
        super().__init__(
            model_client=model_client,
            model_kwargs=model_kwargs,
            template=prompt,
            prompt_kwargs={
                "output_format_str": data_class.format_class_str(
                    DataClassFormatType.SIGNATURE_JSON
                )
            },
            output_processors=JsonOutputParser(data_class=data_class),
        )

    # Define the main function to generate solutions
    async def call(
        self,
        input: ObjectionsOutput,
        model_kwargs: dict = {},
    ) -> OfferGenerationPack:
        all_solutions = []

        # Define an inner function to process each solution
        async def process_solution(p, s, o):
            response: GeneratorOutput = await self.acall(
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
                None

        # Process all solutions concurrently
        await asyncio.gather(
            *(
                process_solution(p, s, o)
                for p, s, o in zip(
                    input.problems.problems, input.subproblems, input.objections
                )
            )
        )
        return OfferGenerationPack(
            problem=input.problems,
            sub_problems=input.subproblems,
            objections=input.objections,
            solutions=all_solutions,
        )


class OfferGenerator(Component):
    def __init__(self, model_client: ModelClient, model_kwargs: Dict):
        super().__init__()
        self.seq = CustomSequence(
            ProblemGenerator(
                prompt=promblem_template,
                model_client=model_client,
                model_kwargs=model_kwargs,
                data_class=Problems,
            ),
            SubProblemGenerator(
                prompt=sub_problem_template,
                model_client=model_client,
                model_kwargs=model_kwargs,
                data_class=SubProblems,
            ),
            ObjectionGenerator(
                prompt=objections_template,
                model_client=model_client,
                model_kwargs=model_kwargs,
                data_class=Objections,
            ),
            SolutionsGenerator(
                prompt=solutions_template,
                model_client=model_client,
                model_kwargs=model_kwargs,
                data_class=Solution,
            ),
        )

    async def acall(self, job_description: OfferInput) -> OfferGenerationPack:

        return await self.seq.call(job_description.job_description)
