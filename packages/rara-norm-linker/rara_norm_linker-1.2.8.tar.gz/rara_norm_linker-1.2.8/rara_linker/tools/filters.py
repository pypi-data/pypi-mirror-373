from rara_linker.config import EntityType, Filters, ALLOWED_FILTERS_MAP, LOGGER, MIN_AUTHOR_SIMILARITY, YEAR_EXCEPTION_VALUE
from rara_tools.parsers.marc_records.person_record import PersonRecord
from rara_tools.parsers.marc_records.organization_record import OrganizationRecord
from rara_tools.parsers.marc_records.title_record import TitleRecord
from rara_tools.parsers.marc_records.ems_record import EMSRecord
from rara_tools.parsers.tools.entity_normalizers import PersonNormalizer
from rara_linker.linkers.linking_result import LinkingResult, LinkedDoc
from jellyfish import jaro_winkler_similarity as jw
from copy import deepcopy
from math import inf
from typing import List, NoReturn


class Filter:
    def __init__(self,
            min_author_similarity: float = MIN_AUTHOR_SIMILARITY,
            year_exception_value: bool = YEAR_EXCEPTION_VALUE
    ) -> NoReturn:

        self.__record_class_map = {
            EntityType.TITLE: TitleRecord,
            EntityType.PER: PersonRecord,
            EntityType.ORG: OrganizationRecord,
            EntityType.LOC: EMSRecord,
            EntityType.KEYWORD: EMSRecord

        }
        self.__filters = {
            Filters.YEAR: self.apply_year_filter,
            Filters.AUTHOR: self.apply_author_filter
        }
        self._min_author_similarity: float = min_author_similarity
        self._year_exception_value: bool = year_exception_value

        self.entity_type = None



    def _get_year(self, record_object: PersonRecord | TitleRecord) -> str | int:
        """ Retrieves year from the record object.
        """
        if self.entity_type == EntityType.PER:
            year = record_object.birth_year
        elif self.entity_type == EntityType.TITLE:
            year = record_object.year
        else:
            year = ""
        return year

    def _get_author(self, record_object: TitleRecord) -> str:
        """ Retrieves author from the record object.
        """
        if self.entity_type == EntityType.TITLE:
            author = record_object.author_name
        else:
            author = ""
        return author

    def _passes_similarity_threshold(self, x: str, y: str, threshold: float) -> bool:
        """ Measures Jaro-Winkler similarity between lowercased
        `x` and `y`. Returns True, if the similarity score of `x` and
        `y` is higher than minimum required similarity (`self._min_author_similarity`)
        and False otherwise.

        Parameters
        -----------
        x: str
            The first string entity to compare.
        y: str
            The second string entity to compare.

        Returns
        -----------
        bool:
            A boolean value indicating if `x` and `y` are sufficiently similar.
        """
        similarity = jw(x.lower(), y.lower())
        if similarity >= threshold:
            LOGGER.debug(
                f"'{x}' sufficiently similary to '{y}' " \
                f"(similarity score = {similarity}, required similarity score = " \
                f"{threshold}.)"
            )
            return True
        return False

    def _passes_year_range(self, year: str, min_year: int = -inf, max_year: int = inf) -> bool:
        """ Makes sure that the given year is in the allowed year range.

        Parameters
        -----------
        year: str
            Year derived from a TitleRecord instance. Can be something
            like "345 eKr" as well, hence we excpect it to be a string.
        min_year: int
            Minimum allowed value for the year.
        max_year: int
            Maximum allowed value for theyear.

        Returns
        -----------
        bool:
            A boolean value indicating if year `year` is in range [min_year, max_year].
        """
        try:
            year = int(year)
        except Exception as e:
            LOGGER.exception(
                f"Year from the record ('{year}') could not be converted into integer " \
                f"and no comparisions can be made. Returning the set default value for " \
                f"function `passes_year_range`: {self._year_exception_value}."
            )
            return self._year_exception_value
        if min_year <= year <= max_year:
            LOGGER.debug(
                f"Year {year} in allowed year range [{min_year}, {max_year}]."
            )
            return True
        return False


    def apply_author_filter(self, linked_docs: List[LinkedDoc], entity: str,
            author: str = "", **kwargs
    ) -> List[LinkedDoc]:
        """ Applies author filter.

        Parameters
        -----------
        linked_docs: List[LinkedDoc]
            List of LinkedDoc instances.
        entity: str
            Original title entity. Necessary only for logging.
        author: str
            Required authors.

        Returns
        -----------
        List[LinkedDoc]
            Filtered list of LinkedDoc instances with matching authors.
        """
        filtered_docs = []
        linked_authors = []
        n_linked = len(linked_docs)
        if linked_docs:
            if not author:
                LOGGER.debug(
                    f"No author is given. All linked documents automatically " \
                    f"pass the author filter."
                )
                return linked_docs

            LOGGER.debug(
                f"Found {n_linked} linked matches for entity '{entity}'. " \
                f"Applying filtering based on author name '{author}'."
            )

            author_variations = PersonNormalizer(author).variations

            for linked_doc in linked_docs:
                marc_json = deepcopy(linked_doc.json)

                record_object = self.record_class(marc_json)

                author_from_record = self._get_author(record_object)
                linked_authors.append(author_from_record)

                author_check_passed = False

                for author_variation in author_variations:
                    if self._passes_similarity_threshold(
                            x=author_variation,
                            y=author_from_record,
                            threshold=self._min_author_similarity
                    ):
                        filtered_docs.append(linked_doc)
                        author_check_passed = True
                        break

            if not filtered_docs:
                LOGGER.info(
                    f"Could not detect sufficiently similar author match from " \
                    f"any of the linked records. Searched match for author '{author}'; " \
                    f"candidates were:  {list(set(linked_authors))}."
                )
        return filtered_docs



    def apply_year_filter(self, linked_docs: List[LinkedDoc], entity: str,
            min_year: int = -inf, max_year: int = inf, **kwargs
    ) -> List[LinkedDoc]:
        """ Applies year filter.

        Parameters
        -----------
        linked_docs: List[LinkedDoc]
            List of LinkedDoc instances.
        entity: str
            Original entity to link. Necessary only for logging.
        min_year: int
            Minimum allowed value for the year.
        max_year: int
            Maximum allowed value for theyear.

        Returns
        -----------
        List[LinkedDoc]
            Filtered list of LinkedDoc instances with years
            in the allowed year range.
        """
        n_linked = len(linked_docs)

        filtered_docs = []
        linked_years = []

        if linked_docs:
            if not (min_year > -inf or max_year < inf):
                LOGGER.debug(
                    f"No year range is given. All linked documents automatically " \
                    f"pass the year range filter."
                )
                return linked_docs

            LOGGER.debug(
                f"Found {n_linked} linked matches for entity '{entity}'. " \
                f"Applying filtering based on year range [{min_year}, {max_year}]."
            )

            for linked_doc in linked_docs:
                marc_json = deepcopy(linked_doc.json)

                record_object = self.record_class(marc_json)

                year = self._get_year(record_object)
                linked_years.append(year)

                if self._passes_year_range(year=year, min_year=min_year, max_year=max_year):
                    filtered_docs.append(linked_doc)

            if not filtered_docs:
                LOGGER.info(
                    f"Could not detect any record with year in the " \
                    f"allowed range [{min_year, max_year}]. " \
                    f"Years tied to linked records were: {list(set(linked_years))}."
                )
        return filtered_docs

    def apply_filters(self, entity_type: str, linked_docs: List[LinkedDoc], **kwargs) -> List[LinkedDoc]:
        """ Applies all available filters for the given entity type.

        Parameters
        ------------
        entity_type: str
            Entity typeself.
        linked_docs: List[LinkedDoc]
            List of LinkedDoc instances.
        **kwargs:
            entity: str
                The original entity to link.
            author: str
                Author of the record (used for TitleRecords).
            min_year: int
                Minimum allowed value for a year
                (birth year for authors, original release year for titles).
            max_year: int
                Maximum allowed value for a year
                (birth year for authors, original release year for titles).

        Returns
        ------------
        List[LinkedDoc]
            List of filtered LinkedDoc instances.
        """
        # Set record class
        self.record_class = self.__record_class_map.get(entity_type, None)

        # Set entity type
        self.entity_type = entity_type

        available_filters = ALLOWED_FILTERS_MAP.get(entity_type)
        LOGGER.debug(f"Applying available filters: {available_filters}.")
        filtered_docs = linked_docs
        for filter in available_filters:
            filter_func = self.__filters.get(filter)
            filtered_docs = filter_func(linked_docs=filtered_docs, **kwargs)

        # Set entity type back to default
        self.entity_type = None
        return filtered_docs
