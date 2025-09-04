from rara_linker.linkers.linker import Linker
from rara_tools.core_formatters.formatted_keyword import FormattedKeyword
from rara_linker.config import (
    LOGGER, URLSource, KeywordSource, EntityType, KeywordType,
    KEYWORD_TYPES_TO_IGNORE, URL_SOURCE_MAP, KEYWORD_TYPE_MAP
)

from typing import List, Dict, NoReturn, Tuple


class KeywordLinker(Linker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url_source_map: dict = URL_SOURCE_MAP

    def link_keywords(self, keywords: List[dict], use_viaf: bool | None = None,
            main_taxonomy_lang: str = "et", context: str = "", query_vector: List[float] = [],
            **kwargs
    ) -> List[dict]:
        """ Applies linking onto rara-subject-indexer flat output.

        Parameters
        -----------
        keywords: List[dict]
            rara-subject-indexer `apply_indexer` output with param `flat=True`.
        use_viaf: bool
            If enabled, VIAF queries are used for linking / enriching the output.
        main_taxnomy_lang: str
            Language of the linked keywords. NB! Currently assumes that only
            one language is used, but might not be true in the future +
            keyword linked only via VIAF might not be in the specifiad language
            as well.
        context: str
            Additional context used, if multiple entities with the same similarity
            score are detected.
        query_vector: List[float]
            Vectorized context. If this field is non-empy, param `context` has no
            impact.
        **kwargs
            Same params can be used as in `Linker.link()`, e.g. `fuzziness`,
            `prefix_length` etc.


        Returns
        ----------
        List[dict]
            List of enriched keyword dicts. NB! Returns only filtered keywords, categories,
            UDC etc will be ignored.

        """
        if use_viaf !=None:
            self.add_viaf_info = use_viaf

        linked_keywords = []
        filtered_keywords = []
        ignored_keywords = []
        categories = []

        for keyword_dict in keywords:
            keyword_type = keyword_dict.get("entity_type")
            keyword = keyword_dict.get("keyword")

            if keyword_type in KEYWORD_TYPES_TO_IGNORE:
                if keyword_type == KeywordType.CATEGORY:
                    categories.append(keyword)
                ignored_keywords.append(keyword_dict)
            else:
                filtered_keywords.append(keyword_dict)


        for keyword_dict in filtered_keywords:
            keyword = keyword_dict.get("keyword")
            keyword_type = keyword_dict.get("entity_type")
            entity_type = KEYWORD_TYPE_MAP.get(keyword_type, "")
            lang = keyword_dict.get("language", "")


            # Keep highest only:
            # if enabled, only results with max similarity are returned
            # otherwise all that surpass the min threshold
            if keyword_type == KeywordType.TOPIC:
                allowed_categories = categories
                keep_highest_only = False
            else:
                allowed_categories = []
                keep_highest_only = True

            linking_result = self.link(
                entity=keyword,
                entity_type=entity_type,
                lang=lang,
                categories=allowed_categories,
                keep_highest_only=keep_highest_only,
                context=context,
                query_vector=query_vector,
                **kwargs
            )

            if linking_result.linked_info:
                linked_doc = linking_result.linked_info[0]
            else:
                linked_doc = None

            linked_keyword = FormattedKeyword(
                object_dict=keyword_dict,
                linked_doc=linked_doc,
                main_taxnomy_lang=main_taxonomy_lang,
                url_source_map=self.url_source_map
            ).to_dict()
            linked_keywords.append(linked_keyword)

        # NB! Returns only filtered keywords, categories, UDC etc will be ignored
        return linked_keywords
