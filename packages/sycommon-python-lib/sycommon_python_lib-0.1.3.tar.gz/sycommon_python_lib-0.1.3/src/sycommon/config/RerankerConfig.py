from pydantic import BaseModel


class RerankerConfig(BaseModel):
    model: str
    provider: str
    baseUrl: str

    @classmethod
    def from_config(cls, model_name: str):
        from sycommon.config.Config import Config
        llm_config = Config().get_reranker_config(model_name)
        return cls(**llm_config)
