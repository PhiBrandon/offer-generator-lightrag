from lightrag.core.generator import Generator
from lightrag.core.types import GeneratorOutputType, GeneratorOutput
from typing import Any, Dict, List, Optional, Union
from langfuse.decorators import observe, langfuse_context


class CustomGenerator(Generator):
    def __init__(
        self,
        template,
        model_client,
        model_kwargs,
        prompt_kwargs,
        output_processors,
        observation_name="completion",
    ):
        super().__init__(
            template=template,
            model_client=model_client,
            model_kwargs=model_kwargs,
            prompt_kwargs=prompt_kwargs,
            output_processors=output_processors,
        )
        self.observation_name = observation_name

    @observe(as_type="generation")
    def call(
        self,
        prompt_kwargs: Optional[Dict] = {},  # the input need to be passed to the prompt
        model_kwargs: Optional[Dict] = {},
    ) -> GeneratorOutputType:
        langfuse_context.update_current_observation(name=self.observation_name)
        r"""
        Call the model_client by formatting prompt from the prompt_kwargs,
        and passing the combined model_kwargs to the model client.
        """
        api_kwargs = self._pre_call(prompt_kwargs, model_kwargs)
        output: GeneratorOutputType = None
        # call the model client
        try:
            completion = self.model_client.call(
                api_kwargs=api_kwargs, model_type=self.model_type
            )
            output = self._post_call(completion)
            langfuse_context.update_current_observation(
                model=self.model_kwargs.get("model"),
                usage={
                    "input": completion.usage.input_tokens,
                    "output": completion.usage.output_tokens,
                },
            )
        except Exception as e:

            output = GeneratorOutput(error=str(e))

        return output
