from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Agentic Support Ticket Assistant"
    llm_provider: str = "openai"  # openai | bedrock | azure
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    azure_openai_endpoint: str = ""
    azure_openai_key: str = ""
    azure_openai_deployment: str = "gpt-4o"
    chroma_path: str = "./data/chroma"
    knowledge_base_dir: str = "./data/kb"
    log_level: str = "INFO"
    require_human_approval: bool = True
    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()
