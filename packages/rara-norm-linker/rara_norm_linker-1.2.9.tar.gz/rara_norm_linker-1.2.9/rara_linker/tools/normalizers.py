import regex as re
import estnltk
import nltk
import logging

from rara_linker import config
from rara_linker.tools.russian_transliterator import Transliterate
from rara_linker.config import KeywordType
from typing import List
from abc import abstractmethod

logger = logging.getLogger(config.LOGGER_NAME)


    
class PersonalName:
    def __init__(self, name: str):
        self.__original_name = name
        self.__name: dict = {}
        self.__last_comma_first: str = ""
        self.__first_last: str = ""
        
    @property 
    def first_name(self) -> str:
        return self.name.get("first_name")
    
    @property
    def last_name(self) -> str:
        return self.name.get("last_name")
              
    @property
    def name(self) -> dict:
        if not self.__name:
            last_name = ""
            first_name = ""
            if "," in self.__original_name:
                try:
                    last_name, first_name = self.__original_name.split(",")
                except Exception as e:
                    logger.error(f"Parsing personal name {self.__original_name} failed with error: {e}.")
            else:
                name_tokens = [
                    t.strip() 
                    for t in self.__original_name.split() 
                    if t.strip()
                ]
                if len(name_tokens) > 1:
                    last_name = name_tokens[-1]
                    first_name = " ".join(name_tokens[:-1])
            self.__name = {
                "first_name": first_name.strip(), 
                "last_name": last_name.strip()
            }
        return self.__name
                   
    @property
    def last_comma_first(self) -> str:
        if not self.__last_comma_first:
            if self.last_name or self.first_name:
                self.__last_comma_first = f"{self.last_name}, {self.first_name}"
        return self.__last_comma_first.strip()
    
    @property 
    def first_last(self) -> str:
        if not self.__first_last:
            self.__first_last = f"{self.first_name} {self.last_name}"
        return self.__first_last.strip()
    
    
class Normalizer:
    def __init__(self, entity: str):
        nltk.download("punkt_tab")
        self.__entity: str = entity
        self.__lemmatized_entity: str = ""
        self.__cleaned_entity: str = ""
            

    @staticmethod    
    def has_cyrillic(entity: str) -> bool:
        return bool(re.search("[а-яА-Я]", entity))
    
    @staticmethod
    def transliterate(entity: str) -> str:
        transliterator = Transliterate()
        transliteration = transliterator([entity])[0]
        return transliteration
    
    @staticmethod
    def lemmatize(entity: str) -> str:
        layer = estnltk.Text(entity).tag_layer()
        lemma_list = [l[0] for l in list(layer.lemma)]
        lemmatized_entity = " ".join(lemma_list)
        return lemmatized_entity
    
    @staticmethod
    def remove_parenthesized_info(entity: str) -> str:
        clean_entity = re.sub(r"[(][^)]+[)]", "", entity)
        return clean_entity.strip()
    
    @staticmethod
    def clean_entity(entity: str) -> str:
        clean_entity = Normalizer.remove_parenthesized_info(entity)
        return clean_entity
    
    @property 
    def lemmatized_entity(self) -> str:
        if not self.__lemmatized_entity:
            self.__lemmatized_entity = Normalizer.lemmatize(self.__entity)
        return self.__lemmatized_entity
    
    @property
    def cleaned_entity(self) -> str:
        if not self.__cleaned_entity:
            self.__cleaned_entity = Normalizer.clean_entity(self.__entity)
        return self.__cleaned_entity
    
    @abstractmethod
    def variations(self) -> List[str]:
        pass

            
class PersonNormalizer(Normalizer):
    def __init__(self, name: str):
        super().__init__(entity=name)
        self.__name: str = name
        self.__name_object: PersonalName = PersonalName(name)
        self.__variations: List[str] = []
     
        
    @property
    def variations(self) -> List[str]:
        if not self.__variations:
            variations = []
            variations.append(self.__name_object.last_comma_first)
            variations.append(self.__name_object.first_last)
            
            if Normalizer.has_cyrillic(self.__name):
                transliterations = [Normalizer.transliterate(name) for name in variations]
                variations.extend(transliterations)
                
            # Guarantee adding one-word names as well
            if self.__name not in variations:
                variations.append(self.__name)
            _variations = [v.strip() for v in variations if v.strip()]
            self.__variations = list(set(_variations))
        return self.__variations
            
        
        
class KeywordNormalizer(Normalizer):
    def __init__(self, keyword: str, keyword_type: str = ""):
        super().__init__(entity=keyword)
        self.__keyword: str = keyword
        self.__variations: List[str] = []
        self.__keyword_type = keyword_type
            
    def transform_v_into_w(self, entity: str) -> str:
        transformed = re.sub("v", "w", entity)
        transformed = re.sub("V", "W", transformed)
        return transformed
        
    @property
    def variations(self) -> List[str]:
        if not self.__variations:
            variations = []
            variations.append(self.__keyword)
            variations.append(self.lemmatized_entity)
            variations.append(self.cleaned_entity)
            variations.append(Normalizer.lemmatize(self.cleaned_entity))
            # If keyword_type = LOC, add variations containing
            # v -> w replacements
            if self.__keyword_type == KeywordType.LOC:
                v_w_transformations = [
                    self.transform_v_into_w(entity)
                    for entity in variations
                ]
                variations.extend(v_w_transformations)
            variations = list(set(variations))             
            self.__variations = variations
        return self.__variations