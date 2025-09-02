from rara_linker.kata_config import Config
import json

class LinkedDoc:
    def __init__(self, linked_doc: dict, config: Config):
        self.viaf: dict = linked_doc.pop("viaf", {})
        self.json: dict = json.loads(linked_doc.pop(config.json_field, "{}"))
        self.marc: str = linked_doc.pop(config.marc_field, "")
        self.similarity_score: float  = linked_doc.pop("similarity_score", None)
        self.linked_entity: str = linked_doc.pop("linked_entity") if "linked_entity" in linked_doc else linked_doc.get(config.key_field, "")
        self.elastic: dict = linked_doc
    
    def to_dict(self):
        return dict(self.__dict__)
    
    def __str__(self):
        return self.linked_entity
    

class LinkingResult:
    def __init__(self, 
            entity: str, 
            entity_type: str, 
            linked_docs: dict, 
            config: Config,
            linking_config: dict
        ):
        self.original_entity: str = entity
        self.entity_type: str = entity_type
        self.linked_info: List[LinkedDoc] = [
            LinkedDoc(linked_doc=doc, config=config)
            for doc in linked_docs
        ]
        self.linking_config: dict = linking_config
        self.n_linked: int = len(self.linked_info)
        self.similarity_score: float = self.linked_info[0].similarity_score if self.linked_info else 0
            
    def to_dict(self) -> dict:
        result_dict = dict(self.__dict__)
        linked_info = result_dict.pop("linked_info")
        linked_info_dicts = [doc.to_dict() for doc in linked_info]
        result_dict["linked_info"] = linked_info_dicts
        return result_dict