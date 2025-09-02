from rara_linker.kata_config import EMSConfig
from rara_linker.config import LOGGER, EntityType
from rara_linker.linkers.base_linker import BaseLinker
from rara_linker.linkers.linking_result import LinkingResult
import logging

logger = LOGGER


class EMSLinker(BaseLinker):
    def __init__(self, **config) -> None:
        conf = EMSConfig(**config)
        super().__init__(conf)
        
        
    @property
    def entity_type(self) -> str:
        return EntityType.KEYWORD
    
    def link(self, entity: str, **kwargs) -> LinkingResult:
        lang = kwargs.get("lang", "")
        if lang == "en":
            self.es_linker.search_field = self.config.alt_search_field
        else:
            self.es_linker.search_field = self.config.search_field
        result = self.link_entity(entity=entity, **kwargs)
        if not result.linked_info and lang == "":
            logger.debug(
                f"Could not find any Estonian matches for entity '{entity}'. " \
                f"Searching English matches..."
            )
            self.es_linker.search_field = self.config.alt_search_field
            result = self.link_entity(entity=entity, **kwargs)
            
        return result
