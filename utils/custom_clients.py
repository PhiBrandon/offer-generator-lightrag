from lightrag.components.model_client import AnthropicAPIClient


class CustomAnthropicAPIClient(AnthropicAPIClient):
    def __init__(self, observation_name="completion"):
        super().__init__()
        self.observation_name = observation_name
        

    
    def parse_chat_completion(self, completion: dict) -> str:
        # do anything you want with the raw completion.
        print(f"do anything you want with the raw completion: {completion}")
        return completion.content[0].text