import os
import requests
import langextract as lx

@lx.providers.registry.register(
    r'^deepseek',              # 支持 model_id 以 deepseek 开头，例如 deepseek-chat
    r'^deepseek\-llm',         # 支持 deepseek-llm
    r'^DeepSeekLanguageModel$',# 显式 class 名称
    priority=10                # 可调节优先级
)
class DeepSeekLanguageModel(lx.inference.BaseLanguageModel):
    """
    LangExtract provider for DeepSeek API.
    Supports: model_id='deepseek-chat', 'deepseek-llm', explicit provider selection.
    """

    def __init__(
        self,
        model_id: str = "deepseek-chat",
        api_key: str = None,
        endpoint: str = "https://api.deepseek.com/v1/chat/completions",
        response_schema: dict = None,
        structured_output: bool = False,
        **kwargs
    ):
        super().__init__()
        self.model_id = model_id
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.endpoint = endpoint or os.getenv("DEEPSEEK_API_URL", endpoint)
        self.response_schema = response_schema
        self.structured_output = structured_output

        if not self.api_key:
            raise ValueError("DeepSeek API key must be set via api_key or DEEPSEEK_API_KEY environment variable.")

    def infer(self, batch_prompts, **kwargs):
        # provider-specific: prompt_description, temperature, etc.
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Prepare DeepSeek API payload
        for prompt in batch_prompts:
            payload = {
                "model": self.model_id,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.2),
                "max_tokens": kwargs.get("max_output_tokens", 1024),
            }
            # Schema constraints
            if self.response_schema and self.structured_output:
                payload["response_schema"] = self.response_schema
                payload["structured_output"] = True

            response = requests.post(self.endpoint, headers=headers, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"DeepSeek API error: {response.status_code}: {response.text}")
            result = response.json()
            # 通用兼容 LangExtract 格式
            output = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            yield [lx.inference.ScoredOutput(score=1.0, output=output)]
    
    @classmethod
    def get_schema_class(cls):
        try:
            from langextract_deepseek.schema import DeepSeekSchema
            return DeepSeekSchema
        except ImportError:
            return None

    def apply_schema(self, schema_instance):
        """Apply or clear schema configuration."""
        super().apply_schema(schema_instance)
        if schema_instance:
            config = schema_instance.to_provider_config()
            self.response_schema = config.get('response_schema')
            self.structured_output = config.get('structured_output', False)
        else:
            self.response_schema = None
            self.structured_output = False
