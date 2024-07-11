sub_problem_template = """
Break down this problem/obstacle into very intricate steps that the job poster would have to do/take in order to be successful.
---
Follow the following format.
Problem: ${problem}
Sub-problems: ${sub_problems}. 
Respond with a single JSON object. JSON Schema: {{output_format_str}}
---
Problem: {{problem}}
Sub-problems:
"""



promblem_template = """Given a job description, list all of the perceived and real problems and obstacles that the job poster could or is currently facing.
---
Follow the following format.
Job Description: ${job_description}
Problems: ${problems}. 
Respond with a single JSON object. JSON Schema: {{output_format_str}}
---
Job Description: {{job_description}}
Problems:
"""


objections_template = """
Given this problem and sub-problems, generate a list of all possible objections that the customer may have for why they think they couldn't solve that problem.
---
Follow the following format.
Problem and Sub-problems: ${problem_and_sub_problems}
Objections: ${objections}. Respond with a single JSON object. JSON Schema: {{output_format_str}}
---
Problem and Sub-problems:
Problem: {{problem}}
Sub-problems: {{sub_problems}}
Objections:
"""

solutions_template = """
Given this problem, sub-problems, and objections, generate single sentences on how a single person service provider would deliver one-on-one solutions. Generate solutions for the following delivery methods: done with you, done for you, and done by you solutions for the given objections. Generate 5 solutions for each method.
---
Follow the following format.
Problem, Sub-problems, and Objections: ${problem_sub_problems_objections}
Solutions: ${solutions}. Respond with a single JSON object. JSON Schema: {{output_format_str}}
---
Problem, Sub-problems, and Objections:
Problem: {{problem}}
Sub-problems: {{sub_problems}}
Objections: {{objections}}
Solutions:
"""

