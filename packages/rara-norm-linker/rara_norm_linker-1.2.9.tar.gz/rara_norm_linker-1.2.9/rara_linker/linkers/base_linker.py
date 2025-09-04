from abc import abstractmethod

from rara_linker.config import LOGGER, VIAF_ENTITY_TYPES, YEAR_EXCEPTION_VALUE, MIN_AUTHOR_SIMILARITY
from rara_linker.kata_config import Config
from rara_linker.linkers.es_linker import ElasticLinker
from rara_linker.linkers.linking_result import LinkingResult
from rara_tools.normalizers.viaf import VIAFClient
from rara_tools.constants.normalizers import (
    VIAF_ENTITY_MAP, DEFAULT_VIAF_FIELD, MAX_VIAF_RECORDS_TO_VERIFY
)
from rara_linker.tools.filters import Filter
logger = LOGGER

DEFAULT_LINKING_CONFIG = {
    "fuzziness": 2,
    "prefix_length": 1,
    "min_similarity": 0.9
}

get_intersection = lambda x, y: list(set(x).intersection(set(y)))

class BaseLinker:
    def __init__(self, config: Config, **kwargs):
        self.config = config
        self.es_linker = ElasticLinker(config, **kwargs)
        self.viaf_linker = VIAFClient()
        self.json_field = self.config.json_field
        self.marc_field = self.config.marc_field
        self.id_field = self.config.identifier_field
        self.viaf_field = self.config.viaf_field
        self.filter = Filter(
            min_author_similarity=MIN_AUTHOR_SIMILARITY,
            year_exception_value=YEAR_EXCEPTION_VALUE
        )

    @abstractmethod
    def entity_type(self) -> str:
        pass

    @abstractmethod
    def link(self) -> LinkingResult:
        pass

    def _add_viaf_info(self, entity: str, es_doc: dict = {}) -> dict:
        """ Adds information from VIAF.

        Parameters
        -----------
        entity: str
            Entity to search from VIAF. NB! If identifier
            can be found from `doc`, this will be used
            for VIAF search instead.
        es_doc:
            Elastic linker output doc.

        Returns
        ----------
        dict
            Document with VIAF information added to it,
            if (verified) matches are found.
        """
        LOGGER.debug(f"Adding information from VIAF for entity '{entity}'.")
        identifier = es_doc.get(self.id_field, "")

        viaf_record = None

        if identifier:
            viaf_record = self.viaf_linker.get_normalized_data_by_search_term(
                search_term=identifier,
                verify=False
            )

        else:
            viaf_record = self.viaf_linker.get_normalized_data_by_search_term(
                search_term=entity,
                field=self.viaf_field,
                verify=True,
                max_records=MAX_VIAF_RECORDS_TO_VERIFY
            )

        if viaf_record:
            LOGGER.debug(
               f"Found the following VIAF reford for entity '{entity}': " \
                f"{viaf_record.all_fields}"
            )
            # TODO: What information to add? original record, record object? parsed record?
            es_doc["viaf"] = {
                #"viaf_record_obj": viaf_record
                "original": viaf_record.record,
                "parsed": viaf_record.all_fields
            }
            if not es_doc.get(self.config.key_field, ""):
                es_doc["linked_entity"] = viaf_record.name

            LOGGER.debug(f"VIAF information added!")

        return es_doc



    def link_entity(self, entity: str, **kwargs) -> LinkingResult:
        es_linker_config = {
            "entity": entity,
            "fuzziness": kwargs.get(
                "fuzziness",
                DEFAULT_LINKING_CONFIG["fuzziness"]
            ),
            "prefix_length": kwargs.get(
                "prefix_length",
                DEFAULT_LINKING_CONFIG["prefix_length"]
            ),
            "min_similarity": kwargs.get(
                "min_similarity",
                DEFAULT_LINKING_CONFIG["min_similarity"]
            ),
            "context": kwargs.get("context", None),
            "keep_highest_only": kwargs.get("keep_highest_only", True),
            "query_vector": kwargs.get("query_vector", [])
        }
        allowed_categories = kwargs.get("categories", [])
        LOGGER.info(f"Entity to link: {entity}")
        LOGGER.debug(f"Allowed categories are: {allowed_categories}")

        es_linking_result = self.es_linker.link(**es_linker_config)
        if not es_linking_result:
            LOGGER.debug(
                f"No matches detected from norm data in Elastic for entity '{entity}'."
            )

        if allowed_categories:
            linked = []
            for es_doc in es_linking_result:
                entity_categories = es_doc.get("subject_fields_et", [])
                intersection = get_intersection(entity_categories, allowed_categories)
                if intersection:
                    linked.append(es_doc)
                LOGGER.debug(f"Entity belongs to the following categories: {entity_categories}")
                LOGGER.debug(f"Intersection with allowed categories: {intersection}")

            if not linked:
                LOGGER.debug(f"Elastic results: {es_linking_result}")
                linked = es_linking_result if es_linking_result else []

        else:
            LOGGER.debug(
                f"No allowed categories passed along with entity '{entity}'. " \
                f"Skipping filtering by category."
            )
            linked = es_linking_result

        add_viaf_info = kwargs.get("add_viaf_info", False)

        if add_viaf_info and self.viaf_field and self.entity_type in VIAF_ENTITY_TYPES:
            if linked:
                linked = [
                    self._add_viaf_info(entity=entity, es_doc=doc)
                    for doc in linked
                ]
            else:
                doc = self._add_viaf_info(entity=entity, es_doc={})
                linked = [doc] if doc else []


        linking_config = es_linker_config
        linking_config.update({"add_viaf_info": add_viaf_info})

        result = LinkingResult(
            entity=entity,
            entity_type=self.entity_type,
            linked_docs=linked,
            config=self.config,
            linking_config=linking_config
        )
        return result
