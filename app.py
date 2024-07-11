from lightrag.components.model_client import AnthropicAPIClient
from lightrag.core.model_client import ModelClient
from src.models import OfferGenerationPack, OfferInput
from task import OfferGenerator
from fastapi import FastAPI
from dotenv import load_dotenv
# Create a FastAPI application
app = FastAPI()
load_dotenv()
# Define an endpoint for generating offers
@app.post("/generate", response_model=OfferGenerationPack)
async def run_sequence(job_description: OfferInput) -> OfferGenerationPack:
    if job_description.job_description == "":
        raise ValueError("Job description cannot be empty")

    # Create a sequence of generators
    offers = OfferGenerator(
        model_client=AnthropicAPIClient(),
        model_kwargs={"model": "claude-3-haiku-20240307", "max_tokens": 4000},
    )
    # Run the sequence and return the result
    result = await offers.acall(job_description)

    return result
