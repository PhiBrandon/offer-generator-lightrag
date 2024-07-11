from lightrag.core.base_data_class import DataClass, field
from typing import List
from dataclasses import dataclass

@dataclass
class OfferInput(DataClass):
    job_description: str = field(metadata={"desc": "description of the job"})

@dataclass
class Problem(DataClass):
    id: int = field(metadata={"desc": "unique identifier for the problem"})
    problem: str = field(metadata={"desc": "description of the problem"})

@dataclass
class Problems(DataClass):
    problems: List[Problem] = field(metadata={"desc": "list of problems"})

@dataclass
class SubProblem(DataClass):
    id: int = field(metadata={"desc": "unique identifier for the sub-problem"})
    sub_problem: str = field(metadata={"desc": "description of the sub-problem"})

@dataclass
class SubProblems(DataClass):
    sub_problems: List[SubProblem] = field(metadata={"desc": "list of sub-problems"})

@dataclass
class SubProblemsOutput(DataClass):
    problems: Problems
    subproblems: list[SubProblems]


@dataclass
class Objection(DataClass):
    id: int = field(metadata={"desc": "unique identifier for the objection"})
    objection: str = field(metadata={"desc": "description of the objection"})

@dataclass
class Objections(DataClass):
    objections: List[Objection] = field(metadata={"desc": "list of objections"})

@dataclass
class ObjectionsOutput(DataClass):
    problems: Problems
    subproblems: list[SubProblems]
    objections: list[Objections] = field(metadata={"desc": "list of objections"})

@dataclass
class Solution(DataClass):
    done_with_you_solutions: List[str] = field(default_factory=list, metadata={"desc": "list of done-with-you solutions"})
    done_for_you_solutions: List[str] = field(default_factory=list, metadata={"desc": "list of done-for-you solutions"})
    do_it_yourself_solutions: List[str] = field(default_factory=list, metadata={"desc": "list of do-it-yourself solutions"})

@dataclass
class OfferGenerationPack(DataClass):
    problem: Problems = field(metadata={"desc": "problems for the offer"})
    sub_problems: List[SubProblems] = field(metadata={"desc": "list of sub-problems for the offer"})
    objections: List[Objections] = field(metadata={"desc": "list of objections for the offer"})
    solutions: List[Solution] = field(metadata={"desc": "list of solutions for the offer"})