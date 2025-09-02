from rara_linker.config import EMS_CONFIG, PER_CONFIG, LOC_CONFIG, ORG_CONFIG, TITLE_CONFIG


class Config:
    def __init__(self, default_config: dict, **custom_config):
        self.default_config = default_config
        self.custom_config = custom_config
        self.es_host = self._get_value("es_host").strip("/")
        self.es_index = self._get_value("es_index")
        self.search_field = self._get_value("search_field")
        self.alt_search_field = self._get_value("alt_search_field")
        self.key_field = self._get_value("key_field")
        self.json_field = self._get_value("json_field")
        self.marc_field = self._get_value("marc_field")
        self.identifier_field = self._get_value("identifier_field")
        self.vector_field = self._get_value("vector_field")
        self.viaf_field = self._get_value("viaf_field")
        
    def _get_value(self, key: str) -> str:
        value = self.custom_config.get(key, "")
        if not value:
            value = self.default_config.get(key, "")
        return value
    
    def to_dict(self) -> dict:
        conf_dict = dict(self.__dict__)
        conf_dict.pop("default_config")
        conf_dict.pop("custom_config")
        return conf_dict
    
    
class PERConfig(Config):
    def __init__(self, **custom_config):
        super().__init__(default_config=PER_CONFIG, **custom_config)
        
class LOCConfig(Config):
    def __init__(self, **custom_config):
        super().__init__(default_config=LOC_CONFIG, **custom_config)
        
class ORGConfig(Config):
    def __init__(self, **custom_config):
        super().__init__(default_config=ORG_CONFIG, **custom_config)
        
class EMSConfig(Config):
    def __init__(self, **custom_config):
        super().__init__(default_config=EMS_CONFIG, **custom_config)
        
class TITLEConfig(Config):
    def __init__(self, **custom_config):
        super().__init__(default_config=TITLE_CONFIG, **custom_config)
        

    