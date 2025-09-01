import yaml


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    def __init__(self, config_file='app.yaml'):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        self.MaxBytes = self.config.get('MaxBytes', 209715200)
        self.Timeout = self.config.get('Timeout', 300000)
        self.OCR = self.config.get('OCR', None)
        self.INVOICE_OCR = self.config.get('INVOICE_OCR', None)
        self.UnstructuredAPI = self.config.get('UnstructuredAPI', None)
        self.MaxRetries = self.config.get('MaxRetries', 3)
        self.llm_configs = []
        self.embedding_configs = []
        self.reranker_configs = []
        self._process_config()

    def get_llm_config(self, model_name):
        for llm in self.llm_configs:
            if llm.get('model') == model_name:
                return llm
        raise ValueError(f"No configuration found for model: {model_name}")

    def get_embedding_config(self, model_name):
        for llm in self.embedding_configs:
            if llm.get('model') == model_name:
                return llm
        raise ValueError(f"No configuration found for model: {model_name}")

    def get_reranker_config(self, model_name):
        for llm in self.reranker_configs:
            if llm.get('model') == model_name:
                return llm
        raise ValueError(f"No configuration found for model: {model_name}")

    def _process_config(self):
        llm_config_list = self.config.get('LLMConfig', [])
        for llm_config in llm_config_list:
            try:
                # 延迟导入 LLMConfigModel
                from sycommon.config.LLMConfig import LLMConfig
                validated_config = LLMConfig(**llm_config)
                self.llm_configs.append(validated_config.model_dump())
            except ValueError as e:
                print(f"Invalid LLM configuration: {e}")

        embedding_config_list = self.config.get('EmbeddingConfig', [])
        for embedding_config in embedding_config_list:
            try:
                from sycommon.config.EmbeddingConfig import EmbeddingConfig
                validated_config = EmbeddingConfig(**embedding_config)
                self.embedding_configs.append(validated_config.model_dump())
            except ValueError as e:
                print(f"Invalid LLM configuration: {e}")

        reranker_config_list = self.config.get('RerankerConfig', [])
        for reranker_config in reranker_config_list:
            try:
                from sycommon.config.RerankerConfig import RerankerConfig
                validated_config = RerankerConfig(**reranker_config)
                self.reranker_configs.append(validated_config.model_dump())
            except ValueError as e:
                print(f"Invalid LLM configuration: {e}")
