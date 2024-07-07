from dotenv import load_dotenv
from lightrag.core.component import Component
from lightrag.components.model_client import AnthropicAPIClient
from lightrag.components.output_parsers import JsonOutputParser
from lightrag.core.base_data_class import DataClassFormatType
from lightrag.core.types import GeneratorOutput
from models.models import *
from prompts.offer_prompts import *
from langfuse.decorators import observe, langfuse_context
from utils.custom_generator import CustomGenerator
from utils.custom_sequence import CustomSequence
from fastapi import FastAPI, HTTPException
from utils.utils import expand_data, upload_s3 
import asyncio


class ProblemGenerator(Component):
    def __init__(self, prompt):
        super().__init__()
        json_parser = JsonOutputParser(data_class=Problems)
        self.prompt = prompt
        self.generator = CustomGenerator(
            template=self.prompt,
            model_client=AnthropicAPIClient(),
            model_kwargs={"model": "claude-3-haiku-20240307", "max_tokens": 4000},
            prompt_kwargs={"output_format_str": json_parser.format_instructions()},
            output_processors=json_parser,
            observation_name="problems",
        )

    async def call(self, text: str, model_kwargs: dict = {}) -> Problems:
        response: GeneratorOutput = await self.generator.acall(
            prompt_kwargs={"job_description": text}, model_kwargs=model_kwargs
        )
        if response.error is None:
            print("Got output")
            print(response.raw_response)
            output = Problems.from_dict(response.data)
            return output
        else:
            print("No output")
            None


class SubProblemGenerator(Component):
    def __init__(self, prompt):
        super().__init__()
        json_parser = JsonOutputParser(data_class=SubProblems)
        self.prompt = prompt
        self.generator = CustomGenerator(
            template=self.prompt,
            model_client=AnthropicAPIClient(),
            model_kwargs={"model": "claude-3-haiku-20240307", "max_tokens": 4000},
            prompt_kwargs={
                "output_format_str": SubProblems.format_class_str(
                    DataClassFormatType.SIGNATURE_JSON
                )
            },
            output_processors=json_parser,
            observation_name="sub_problems",
        )

    async def call(
        self, problems: Problems, model_kwargs: dict = {}
    ) -> SubProblemsOutput:
        sub_problems = []
        """ for p in problems.problems:
            response: GeneratorOutput = await self.generator.acall(
                prompt_kwargs={"problem": p.problem}, model_kwargs=model_kwargs
            )
            if response.error is None:
                try:
                    output = SubProblems.from_dict(response.data)
                    sub_problems.append(output)
                except:
                    try:
                        output = SubProblems.from_json(response.data)
                        sub_problems.append(output)
                    except:
                        print("parse failed...")
                        pass
            else:
                None """

        async def process_problem(p):
            response: GeneratorOutput = await self.generator.acall(
                prompt_kwargs={"problem": p.problem}, model_kwargs=model_kwargs
            )
            if response.error is None:
                try:
                    output = SubProblems.from_dict(response.data)
                    sub_problems.append(output)
                except:
                    try:
                        output = SubProblems.from_json(response.data)
                        sub_problems.append(output)
                    except:
                        print("parse failed...")
            else:
                None

        await asyncio.gather(*(process_problem(p) for p in problems.problems))
        return SubProblemsOutput(problems=problems, subproblems=sub_problems)


class ObjectionGenerator(Component):
    def __init__(self, prompt):
        super().__init__()
        json_parser = JsonOutputParser(data_class=Objections)
        self.prompt = prompt
        self.generator = CustomGenerator(
            template=self.prompt,
            model_client=AnthropicAPIClient(),
            model_kwargs={"model": "claude-3-haiku-20240307", "max_tokens": 4000},
            prompt_kwargs={
                "output_format_str": Objections.format_class_str(
                    DataClassFormatType.SIGNATURE_JSON
                )
            },
            output_processors=json_parser,
            observation_name="objections",
        )

    async def call(
        self,
        input: SubProblemsOutput,
        model_kwargs: dict = {},
    ) -> ObjectionsOutput:
        """all_objections = []
        for p, s in zip(input.problems.problems, input.subproblems):
            response: GeneratorOutput = await self.generator.acall(
                prompt_kwargs={
                    "problem": p.problem,
                    "sub_problems": [sub.sub_problem for sub in s.sub_problems],
                },
                model_kwargs=model_kwargs,
            )
            if response.error is None:
                try:
                    output = Objections.from_dict(response.data)
                    all_objections.append(output)
                except:
                    try:
                        output = Objections.from_json(response.data)
                        all_objections.append(output)
                    except:
                        print("parse failed...")
                        pass
            else:
                print(response.error)
                None"""
        all_objections = []

        async def process_objection(p, s):
            response: GeneratorOutput = await self.generator.acall(
                prompt_kwargs={
                    "problem": p.problem,
                    "sub_problems": [sub.sub_problem for sub in s.sub_problems],
                },
                model_kwargs=model_kwargs,
            )
            if response.error is None:
                try:
                    output = Objections.from_dict(response.data)
                    all_objections.append(output)
                except:
                    try:
                        output = Objections.from_json(response.data)
                        all_objections.append(output)
                    except:
                        print("parse failed...")
            else:
                print(response.error)

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


class SolutionsGenerator(Component):
    def __init__(self, prompt):
        super().__init__()
        json_parser = JsonOutputParser(data_class=Solution)
        self.prompt = prompt
        self.generator = CustomGenerator(
            template=self.prompt,
            model_client=AnthropicAPIClient(),
            model_kwargs={"model": "claude-3-haiku-20240307", "max_tokens": 4000},
            prompt_kwargs={
                "output_format_str": Solution.format_class_str(
                    DataClassFormatType.SIGNATURE_JSON
                )
            },
            output_processors=json_parser,
            observation_name="solution_generation",
        )

    async def call(
        self,
        input: ObjectionsOutput,
        model_kwargs: dict = {},
    ) -> OfferGenerationPack:
        """all_solutions = []
        for p, s, o in zip(
            input.problems.problems, input.subproblems, input.objections
        ):
            response: GeneratorOutput = await self.generator.acall(
                prompt_kwargs={
                    "problem": p.problem,
                    "sub_problems": [sub.sub_problem for sub in s.sub_problems],
                    "objections": [obj.objection for obj in o.objections],
                },
                model_kwargs=model_kwargs,
            )
            if response.error is None:
                try:
                    output = Solution.from_dict(response.data)
                    all_solutions.append(output)
                except:
                    try:
                        output = Solution.from_json(response.data)
                        all_solutions.append(output)
                    except:
                        print("parse failed...")
                        pass


            else:
                print(response.error)
                None"""
        all_solutions = []

        async def process_solution(p, s, o):
            response: GeneratorOutput = await self.generator.acall(
                prompt_kwargs={
                    "problem": p.problem,
                    "sub_problems": [sub.sub_problem for sub in s.sub_problems],
                    "objections": [obj.objection for obj in o.objections],
                },
                model_kwargs=model_kwargs,
            )
            if response.error is None:
                try:
                    output = Solution.from_dict(response.data)
                    all_solutions.append(output)
                except:
                    try:
                        output = Solution.from_json(response.data)
                        all_solutions.append(output)
                    except:
                        print("parse failed...")
            else:
                print(response.error)

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


app = FastAPI()


@app.post("/generate", response_model=OfferGenerationPack)
@observe()
async def run_sequence(job_description: OfferInput) -> OfferGenerationPack:
    if job_description.job_description == "":
        raise ValueError("Job description cannot be empty")
    seq = CustomSequence(
        ProblemGenerator(prompt=promblem_template),
        SubProblemGenerator(prompt=sub_problem_template),
        ObjectionGenerator(prompt=objections_template),
        SolutionsGenerator(prompt=solutions_template),
    )
    result = await seq.call(job_description.job_description)
    langfuse_context.flush()
    return result


@app.post("/upload")
async def upload_data(offer_gen_pack: OfferGenerationPack) -> str:
    if offer_gen_pack is None:
        raise HTTPException(
            status_code=400, detail="Offer generation pack cannot be None"
        )

    try:
        # Expand data and create Excel file
        file_info = expand_data(offer_gen_pack)

        # Upload to S3 and get presigned URL
        presigned_url = upload_s3(file_info)

        return presigned_url
    except Exception as e:
        print(f"Error during upload process: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# pack = asyncio.run(run_sequence())
