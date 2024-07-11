from lightrag.core.generator import Generator
from lightrag.core.types import GeneratorOutputType, GeneratorOutput
from typing import Any, Dict, List, Optional, Union


class CustomGenerator(Generator):
    def __init__(
        self,
        template,
        model_client,
        model_kwargs,
        prompt_kwargs,
        output_processors,
    ):
        super().__init__(
            template=template,
            model_client=model_client,
            model_kwargs=model_kwargs,
            prompt_kwargs=prompt_kwargs,
            output_processors=output_processors,
        )

    async def acall(
        self,
        prompt_kwargs: Optional[Dict] = {},  # the input need to be passed to the prompt
        model_kwargs: Optional[Dict] = {},
    ) -> GeneratorOutputType:
        r"""
        Call the model_client by formatting prompt from the prompt_kwargs,
        and passing the combined model_kwargs to the model client.
        """
        api_kwargs = self._pre_call(prompt_kwargs, model_kwargs)
        output: GeneratorOutputType = None
        # call the model client
        try:
            completion = await self.model_client.acall(
                api_kwargs=api_kwargs, model_type=self.model_type
            )
            output = self._post_call(completion)
        except Exception as e:

            output = GeneratorOutput(error=str(e))

        return output
