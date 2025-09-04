from rara_linker.linkers.base_linker import BaseLinker
from rara_linker.linkers.linking_result import LinkingResult
from rara_linker.kata_config import ORGConfig
from rara_linker.config import LOGGER, EntityType

logger = LOGGER

class OrganizationLinker(BaseLinker):
    def __init__(self, **config) -> None:
        conf = ORGConfig(**config)
        super().__init__(conf, **{"vectorizer": config.get("vectorizer", None)})
        
        
    @property
    def entity_type(self) -> str:
        return EntityType.ORG
    
    def link(self, entity: str, **kwargs) -> LinkingResult:
        self.es_linker.search_field = self.config.search_field
        result = self.link_entity(entity=entity, **kwargs)
        if not result.linked_info:
            logger.debug(
                f"Could not find full name matches for entity '{entity}'. " \
                f"Treating it as an acronym and trying again..."
            )
            kwargs.pop("fuzziness", 0)
            self.es_linker.search_field = self.config.alt_search_field
            result = self.link_entity(entity=entity, fuzziness=0, **kwargs)
            
        return result


if __name__ == "__main__":
    from pprint import pprint

    LOGGER.setLevel(logging.DEBUG)
    ol = OrganizationLinker()
    linked = ol.link(entity="NASA", add_viaf_info=True)#entity="NASA")

    pprint(linked)
