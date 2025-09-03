# LangExtract DeepSeek Provider Plugin

## Features
- Plug-and-play DeepSeek API provider for LangExtract
- Supports model_id pattern: `deepseek-*`, `DeepSeekLanguageModel`
- Schema constraints for structured output
- Compatible with lazy plugin discovery and explicit provider selection

## Usage

```bash
pip install langextract-deepseek
```

```python
import langextract as lx
result = lx.extract(
    text="请抽取这段话中的所有实体。",
    model_id="deepseek-chat",
    api_key="your-deepseek-api-key"
)
```

### With Schema Constraints

```python
examples = [...]  # List of AnnotatedDocument
result = lx.extract(
    text="抽取实体与属性",
    model_id="deepseek-chat",
    use_schema_constraints=True,
    examples=examples,
    api_key="your-deepseek-api-key"
)
```

## Environment Variables

- `DEEPSEEK_API_KEY`: DeepSeek API key
- `DEEPSEEK_API_URL`: Custom API endpoint (optional)

## Supported Parameters

- `model_id`: e.g. `deepseek-chat`
- `temperature`, `max_output_tokens`, etc.

## Advanced: Explicit Provider Selection

```python
from langextract.factory import ModelConfig, create_model

config = ModelConfig(
    model_id="deepseek-chat",
    provider="DeepSeekLanguageModel",
    provider_kwargs={"api_key": "sk-xxx"}
)
model = create_model(config)
outputs = model.infer(["你的抽取任务"])
```
