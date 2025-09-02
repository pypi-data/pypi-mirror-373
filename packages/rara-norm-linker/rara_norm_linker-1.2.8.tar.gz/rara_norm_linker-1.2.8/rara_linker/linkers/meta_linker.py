from rara_linker.linkers.linker import Linker
from rara_linker.config import (
    LOGGER, EntityType
)
from rara_tools.core_formatters.formatted_meta import (
    FormattedAuthor, FormattedTitle
)
from typing import List, Dict, NoReturn, Tuple


class MetaLinker(Linker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_primary_author(self, authors: List[dict]) -> str:
        primary_author = ""
        for author in authors:
            if author.get("is_primary", False):
                primary_author = author.get("name", "")
        return primary_author

    def link_authors(self, authors: List[dict], **kwargs) -> List[dict]:
        LOGGER.debug("Linking authors...")
        linked_authors = []
        for author in authors:
            linking_result = self.link(
                entity=author.get("name"),
                **kwargs
            )
            if linking_result.linked_info:
                linked_doc = linking_result.linked_info[0]
            else:
                linked_doc = None

            entity_type = linking_result.entity_type

            linked_author = FormattedAuthor(
                object_dict=author,
                linked_doc=linked_doc,
                entity_type=entity_type
            ).to_dict()
            linked_authors.append(linked_author)
        return linked_authors

    def link_sections(self, sections: List[dict], **kwargs) -> List[dict]:
        LOGGER.debug("Linking METS/ALTO sections...")
        for section in sections:
            authors = section.pop("authors", [])
            titles = section.pop("titles", [])
            primary_author = self.get_primary_author(authors)
            if primary_author:
                for title in titles:
                    title["author_from_title"] = primary_author
            section["titles"] = titles

            linked_authors = self.link_authors(authors, **kwargs)
            section["authors"] = linked_authors

        return sections

    def link_meta(self, meta: dict, use_viaf: bool | None = None, **kwargs) -> dict:
        """ Link meta fields.

        Parameters
        -----------
        meta: dict
            `rara_meta_extractor` output.
        use_viaf: bool
            If enabled, VIAF queries are used for linking / enriching the output.
        **kwargs
            Same params can be used as in `Linker.link()`, e.g. `fuzziness`,
            `prefix_length` etc.

        Returns
        ------------
        dict
            Enriched metadata.
        """
        LOGGER.debug("Linking metadata...")
        if use_viaf != None:
            self.add_viaf_info = use_viaf
        meta_to_link = meta.get("meta") # TODO: pass this level instead?

        authors = meta_to_link.pop("authors", [])
        sections = meta_to_link.pop("sections", [])

        linked_authors = self.link_authors(authors, **kwargs)
        linked_sections = self.link_sections(sections, **kwargs)

        if sections and linked_sections:
            meta_to_link["sections"] = linked_sections
        if authors and linked_authors:
            meta_to_link["authors"] = linked_authors

        meta["meta"] = meta_to_link
        return meta
