from pydantic import BaseModel


class LLMConfig(BaseModel):
    model: str
    provider: str
    baseUrl: str
    maxTokens: int
    vision: bool
    callFunction: bool

    @classmethod
    def from_config(cls, model_name: str):
        from sycommon.config.Config import Config
        llm_config = Config().get_llm_config(model_name)
        return cls(**llm_config)
