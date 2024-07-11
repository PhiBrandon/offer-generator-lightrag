import os
import polars as pl
import json
import uuid
import boto3
import xlsxwriter
from models.models import OfferGenerationPack

# Adjust this import path as needed

BUCKET_NAME = "bpdata-offers-exports"


def expand_data(data: OfferGenerationPack):
    # Convert OfferGenerationPack to a format suitable for Polars DataFrame
    converted_data = {
        "problem": [prob.problem for prob in data.problem.problems],
        "sub_problems": [
            [sp.sub_problem for sp in sps.sub_problems] for sps in data.sub_problems
        ],
        "objections": [
            [obj.objection for obj in objs.objections] for objs in data.objections
        ],
        "done_with_you_solutions": [
            sol.done_with_you_solutions for sol in data.solutions
        ],
        "done_for_you_solutions": [
            sol.done_for_you_solutions for sol in data.solutions
        ],
        "do_it_yourself_solutions": [
            sol.do_it_yourself_solutions for sol in data.solutions
        ],
    }

    df = pl.DataFrame(converted_data)
    exploded = df.explode("objections").explode("sub_problems")
    unpacked = exploded.select(
        pl.all()
    )  # No need to unnest as we're already using flat structures

    dw_explode = (
        unpacked.select(
            pl.all().exclude(["do_it_yourself_solutions", "done_for_you_solutions"])
        ).explode("done_with_you_solutions")
    ).unique(
        subset=["done_with_you_solutions", "objections"],
        maintain_order=True,
    )
    diy_explode = (
        unpacked.select(
            pl.all().exclude(["done_with_you_solutions", "done_for_you_solutions"])
        ).explode("do_it_yourself_solutions")
    ).unique(
        subset=["do_it_yourself_solutions", "objections"],
        maintain_order=True,
    )
    dfy_explode = (
        unpacked.select(
            pl.all().exclude(["done_with_you_solutions", "do_it_yourself_solutions"])
        ).explode("done_for_you_solutions")
    ).unique(
        subset=["done_for_you_solutions", "objections"],
        maintain_order=True,
    )
    problems_subprobs = unpacked.select(
        [pl.col("problem"), pl.col("sub_problems"), pl.col("objections")]
    ).unique(["sub_problems", "objections"])

    id = str(uuid.uuid4())
    file_name = f"gen-{id}.xlsx"
    path = "./"
    full = path + file_name
    with xlsxwriter.Workbook(full) as book:
        dw_explode.write_excel(workbook=book, worksheet="done-with-you", position="A1")
        diy_explode.write_excel(
            workbook=book, worksheet="do-it-yourself", position="A1"
        )
        dfy_explode.write_excel(workbook=book, worksheet="done-for-you", position="A1")
        problems_subprobs.write_excel(
            workbook=book, worksheet="problems-objections", position="A1"
        )
    print(full)
    return {"file_name": file_name, "full_path": full}


def upload_s3(file_name_and_path):
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(
            file_name_and_path["full_path"],
            BUCKET_NAME,
            file_name_and_path["file_name"],
        )
        presigned = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": file_name_and_path["file_name"]},
            ExpiresIn=7200,
        )
        os.remove(file_name_and_path["full_path"])
        return presigned
    except Exception as e:
        print(e)
        raise e
