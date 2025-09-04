import requests
import json
import logging
from jellyfish import jaro_winkler_similarity, levenshtein_distance
from typing import List, NoReturn
from pathlib import Path
from rara_linker.config import LOGGER
from rara_linker.kata_config import Config
from rara_linker.tools.vectorizer import Vectorizer
from rara_tools.elastic import KataElastic

logger = LOGGER
        
        

class ElasticLinker:
    def __init__(self, config: Config, **kwargs) -> NoReturn:
        """
        Initialize ElasticLinker object.

        Parameters
        ----------
        es_host : str
            Elasticsearch host URL.
        es_index: str
            Elasticsearch index containing linking data.
        search_field: str
            Field in `es_index` used for linkining.
        key_field: str
            Field containing the normalized entity.
        vector_field: str | None
            Field containing vectorized data.
        """
        self.elastic: KataElastic = KataElastic(config.es_host)
        self.es_index: str = config.es_index
        self.search_field: str = config.search_field
        self.key_field: str = config.key_field
        self.vector_field: str = config.vector_field
        self.vectorizer: Vectorizer = kwargs.get("vectorizer", None)

    
    def _get_jw_similarity(self, doc: dict, entity: str) -> float:
        """ Calculate Jaro-Winkler similarity based on best-matching
        entity in the search field.
        """
        variations = doc[self.search_field]
        max_similarity = 0
        for match in variations:
            jw_similarity = jaro_winkler_similarity(entity.lower(), match.lower())
            if jw_similarity > max_similarity:
                max_similarity=jw_similarity
        return max_similarity
    
    def _add_similarity_scores(self, docs: List[dict], entity: str) -> List[dict]:
        for doc in docs:
            doc["similarity_score"] = self._get_jw_similarity(doc, entity)
        return docs 
    
    def _filter_based_on_similarity(self, docs: List[dict], min_similarity: float, 
                                    keep_highest_only: bool=True) -> List[dict]:
        """ Filter out documents with the highest similarity score that
        also surpass the minimum similarity requirement.
        
        Parameters
        ------------
        docs: List[dict] 
            List of Elastic documents. 
        min_similarity: float
            Minimum Jaro-Winkler similarity to keep the document. 
        keep_highest_only: bool
            If enabled, only the documents with the highest scores
            are returned; otherwise all that surpass the min similarity
            threshold.
        
        """
        filtered = []
        logger.debug(f"Filtering docs: {docs}")
        if docs:
            sorted_docs = sorted(docs, key=lambda x: x["similarity_score"], reverse=True)
            max_similarity_score = sorted_docs[0].similarity_score

            if max_similarity_score >= min_similarity:
                filtered.append(sorted_docs[0])
                for doc in sorted_docs[1:]:
                    if keep_highest_only:
                        if doc.similarity_score == max_similarity_score:
                            filtered.append(doc)
                        else:
                            break
                    else:
                        if doc.similarity_score >= min_similarity:
                            filtered.append(doc)
                        else:
                            break
                        
        return filtered
    
    def link(self, 
            entity: str, 
            fuzziness: int = 2, 
            prefix_length: int = 1, 
            max_expansions: int = 50,
            min_similarity: float = 0.9,
            context: str = None,
            query_vector: List[dict] = [],
            keep_highest_only: bool = True          
    ) -> dict:
        """
        Execute the full linking pipeline. Steps:
        
        1. Try finding only exact matches
        2. If no matches were found during step 1, 
           execute fuzzy search (if `fuzziness` > 0)
        3. Use Jaro-Winkler distance to filter out matches 
           that do not pass the given similarity threshold 
           (`min_similarity`).
        4. Filter out matches with highest similarity scores.
        5. If more than one match remains after step 4,
           vector field was specified during the object's
           initialization and `context` is not None, 
           execute a vector search.
        TODO: additional restrictions, e.g. years
        
        Parameters
        ----------
        entity: str
            Entity to link.
        fuzziness: int
            Maximum edit distance for a match.
        prefix_length: int
            Number of characters in the prefix that should overlap 
            with the original entity's prefix.
        max_expansions: int
            TODO
        min_similarity: float
            Minimum allowed Jaro-Winkler similarity.
        context: str | None
            Context to use for vector search, if necessary.
        query_vector: List[float]
            Vectorized text to use for vector search. If this is passed, context
            is ignored, even if not None / empty.
        keep_highest_only: bool
            If enabled, only the results with highest similarity
            are kept during filtering. Otherwise all results surpassing
            similarity threshold are kept.
            
          
        Returns
        -------
        
        dict
            
        """
        # search both lowercased and the original entity
        # as alternative linking fields contain original (uppercase)
        # versions 
        # UPDATE: search only lowercase version, but rethink this logic maybe
        #search_entities = [entity.lower(), entity]
        search_entities = [entity.lower()]
        docs = []
        for search_entity in search_entities:
            _docs = []
            if keep_highest_only:
                # Step 1: Try finding only exact matches at first (fuzziness=0)
                _docs = self.elastic.execute_fuzzy_search(
                    index=self.es_index,
                    field=self.search_field,
                    entity=search_entity, 
                    fuzziness=0, 
                    prefix_length=prefix_length, 
                    max_expansions=max_expansions
                )


            # Step 2: If no matches were found, try again with some fuzziness
            if len(_docs) == 0 and (fuzziness > 0 or not keep_highest_only):
                logger.debug(
                    f"Exact matches were not found for entity '{entity}'. " \
                    f"Executing a fuzzy search with fuzziness = {fuzziness}..."
                )

                _docs = self.elastic.execute_fuzzy_search(
                    index=self.es_index,
                    field=self.search_field,
                    entity=search_entity, 
                    fuzziness=fuzziness, 
                    prefix_length=prefix_length, 
                    max_expansions=max_expansions
                )
            docs.extend(_docs)
            
        # Stp 3: Add similarity score to each doc
        docs = self._add_similarity_scores(docs, search_entity)

        # Step 4: Filter based on similarity.
        # Keep only docs that
        # a) surpass the required similarity threshold
        # b) have the highest similarity compared to others
        logger.debug(f"Filtering documents with highest_only = {keep_highest_only}")
        docs = self._filter_based_on_similarity(docs, min_similarity, keep_highest_only)
        

        # Step 5: If more than one match remains, execute an additional vector search
        if len(docs) > 1 and (query_vector or context) and self.vector_field and self.vectorizer != None:
            logger.debug(f"Running a vector search to determine the best candidate...")
            elastic_ids = [doc.meta.id for doc in docs]
            if not query_vector:
                LOGGER.debug(
                    f"Query vector was not passed, generating the vector " \
                    f"based on context {context[:20]}..."
                )
                query_vector = self.vectorizer.vectorize(context)
            
            docs = self.elastic.execute_script_score_vector_search(
                index=self.es_index,
                field=self.vector_field,
                query_vector=query_vector,
                elastic_ids=elastic_ids,
                n_docs=1
            )
            docs = self._add_similarity_scores(docs, search_entity)
        
        linked = [hit.to_dict() for hit in docs]
        for doc in linked:
            if self.vector_field in doc:
                doc.pop(self.vector_field)
                
        return linked
    