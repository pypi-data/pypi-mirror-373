import os
from typing import List, Tuple
from rara_linker.config import (
    LOGGER, EntityType, KeywordType

)
from rara_linker.exceptions import InvalidInputError
from rara_linker.linkers.ems_linker import EMSLinker
from rara_linker.linkers.linking_result import LinkingResult, LinkedDoc
from rara_linker.linkers.loc_linker import LocationLinker
from rara_linker.linkers.org_linker import OrganizationLinker
from rara_linker.linkers.per_linker import PersonLinker
from rara_linker.linkers.title_linker import TitleLinker
from rara_linker.tools.vectorizer import Vectorizer

logger = LOGGER

ALLOWED_ENTITY_TYPES = [
    EntityType.PER,
    EntityType.ORG,
    EntityType.KEYWORD,
    EntityType.LOC,
    EntityType.TITLE,
    EntityType.UNK
]

DEFAULT_FUZZINESS = 2


class Linker:
    def __init__(
            self,
            add_viaf_info: bool = False,
            vectorizer_or_dir_path: str | Vectorizer = os.path.join(".", "vectorizer_data"),
            per_config: dict = {},
            org_config: dict = {},
            loc_config: dict = {},
            ems_config: dict = {},
            title_config: dict = {}
    ):
        self.vectorizer: Vectorizer = self._handle_vectorizer_load(vectorizer_or_dir_path)

        per_config.update({"vectorizer": self.vectorizer})
        org_config.update({"vectorizer": self.vectorizer})

        self.per_linker: PersonLinker = PersonLinker(**per_config)
        self.org_linker: OrganizationLinker = OrganizationLinker(**org_config)
        self.ems_linker: EMSLinker = EMSLinker(**ems_config)
        self.loc_linker: LocationLinker = LocationLinker(**loc_config)
        self.title_linker: TitleLinker = TitleLinker(**title_config)
        self.add_viaf_info: bool = add_viaf_info
        self.linkers_map: dict = {
            EntityType.PER: self.per_linker,
            EntityType.ORG: self.org_linker,
            EntityType.LOC: self.loc_linker,
            EntityType.KEYWORD: self.ems_linker,
            EntityType.TITLE: self.title_linker
        }

    def _handle_vectorizer_load(self, path_or_instance) -> Vectorizer:
        if isinstance(path_or_instance, str):
            return Vectorizer(path_or_instance)
        elif isinstance(path_or_instance, Vectorizer):
            return path_or_instance

        raise ValueError("Inserted value is not the expected str or Vectorizer type!")

    def execute_all_linkers(self, entity: str, **kwargs) -> LinkingResult:
        temp = []
        for entity_type, linker in self.linkers_map.items():
            logger.debug(f"Searching {entity_type} matches for entity '{entity}'...")
            linked = linker.link(entity=entity, add_viaf_info=self.add_viaf_info, **kwargs)
            if linked.linked_info:
                if not linked.linked_info[0].elastic:
                    LOGGER.info(
                        f"Found only VIAF matches for entity '{entity}' with entity_type='{entity_type}'. " \
                        f"Continuing until Sierra/EMS matches are detected or until all entity types are checked."
                    )
                    temp.append(linked)
                else:
                    break
        if not linked.linked_info:
            if temp:
                entity_types = [linked_doc.entity_type for linked_doc in temp]
                LOGGER.debug(
                    f"Found VIAF matches for the following entity types: {entity_types}."
                )
                LOGGER.warning(
                    f"Returning only the first match in the array (for entity_type={entity_types[0]}). " \
                    f"This might not be correct!"
                )
                linked = temp[0]
            else:
                logger.debug(f"No matches found for entity '{entity}'.")
                linked.entity_type = EntityType.UNK
        return linked

    def link(self, entity: str, **kwargs) -> LinkingResult:
        if not isinstance(entity, str) or not entity.strip():
            raise InvalidInputError(f"Invalid value for entity: '{entity}'.")

        entity_type = kwargs.get("entity_type", None)
        if entity_type:
            if entity_type not in ALLOWED_ENTITY_TYPES:
                raise InvalidInputError(
                    f"Invalid entity type '{entity_type}'. " \
                    f"Supported entity types are: {ALLOWED_ENTITY_TYPES}"
                )
            else:
                linker = self.linkers_map.get(entity_type)
                logger.debug(f"Searching {entity_type} matches for entity '{entity}'...")
                linked = linker.link(entity=entity, add_viaf_info=self.add_viaf_info, **kwargs)
        else:
            LOGGER.debug("Executing first round with fuzziness=0")
            fuzziness = kwargs.pop("fuzziness", DEFAULT_FUZZINESS)
            linked = self.execute_all_linkers(
                entity=entity,
                fuzziness=0,
                **kwargs
            )
            if not linked.linked_info:
                LOGGER.debug(f"Executing second round with fuzziness={fuzziness}")
                linked = self.execute_all_linkers(
                    entity=entity,
                    fuzziness=fuzziness,
                    **kwargs
                )
        return linked
