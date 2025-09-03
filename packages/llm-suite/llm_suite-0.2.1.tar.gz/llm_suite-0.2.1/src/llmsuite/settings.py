from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PromptSettings(BaseSettings):
    templates_dir: str = Field(default="./prompts")


class LLMProviderSettings(BaseSettings):
    temperature: float | None = Field(alias="DEFAULT_TEMPERATURE", default=None)
    max_tokens: int | None = Field(alias="DEFAULT_MAX_TOKENS", default=None)
    top_p: float | None = Field(alias="DEFAULT_TOP_P", default=None)
    max_retries: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class OpenAISettings(LLMProviderSettings):
    api_key: str | None = Field(alias="OPENAI_API_KEY", default=None)
    base_url: str = "https://api.openai.com/v1"


class AnthropicSettings(LLMProviderSettings):
    api_key: str | None = Field(alias="ANTHROPIC_API_KEY", default=None)


class TogetherAISettings(LLMProviderSettings):
    api_key: str | None = Field(alias="TOGETHER_API_KEY", default=None)
    base_url: str = "https://api.together.xyz/v1"


class PerplexitySettings(LLMProviderSettings):
    api_key: str | None = Field(alias="PERPLEXITY_API_KEY", default=None)
    base_url: str = "https://api.perplexity.ai"


class GroqSettings(LLMProviderSettings):
    api_key: str | None = Field(alias="GROQ_API_KEY", default=None)
    base_url: str = "https://api.groq.com/openai/v1"


class OllamaSettings(LLMProviderSettings):
    api_key: str = "ollama"
    base_url: str = "http://localhost:11434/v1"


class LMStudioSettings(LLMProviderSettings):
    api_key: str = "lmstudio"
    base_url: str = "http://localhost:1234/v1"


class Settings(BaseSettings):
    default_provider: str | None = Field(alias="DEFAULT_PROVIDER", default=None)
    default_model: str | None = Field(alias="DEFAULT_MODEL", default=None)

    # Provider-specific settings
    prompt: PromptSettings = PromptSettings()
    openai: OpenAISettings = OpenAISettings()
    ollama: OllamaSettings = OllamaSettings()
    groq: GroqSettings = GroqSettings()
    anthropic: AnthropicSettings = AnthropicSettings()
    lmstudio: LMStudioSettings = LMStudioSettings()
    perplexity: PerplexitySettings = PerplexitySettings()
    together: TogetherAISettings = TogetherAISettings()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings():
    return Settings()
