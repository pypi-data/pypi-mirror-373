from pydantic import BaseModel


class EmbeddingConfig(BaseModel):
    model: str
    provider: str
    baseUrl: str
    maxTokens: int
    dimension: int

    @classmethod
    def from_config(cls, model_name: str):
        from sycommon.config.Config import Config
        llm_config = Config().get_embedding_config(model_name)
        return cls(**llm_config)
