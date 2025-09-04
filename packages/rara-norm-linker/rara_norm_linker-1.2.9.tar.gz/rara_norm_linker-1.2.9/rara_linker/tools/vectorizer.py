import pathlib
from pathlib import Path
from typing import Any, List, Optional

from FlagEmbedding import BGEM3FlagModel
from huggingface_hub import snapshot_download

from rara_linker.config import LOGGER

logger = LOGGER
VECTOR_FIELD_NAME = "vector"
FIELD_TO_VECTORIZE = "description"


class Vectorizer:
    def __init__(
            self,
            model_directory: str = "../vectorizer_data",
            model_name: str = "BAAI/bge-m3",
            system_configuration: dict = {
                "use_fp16": False,
                "devices": None,
                "normalize_embeddings": True
            },
            inference_configuration: dict = {
                "batch_size": 12,
                "return_dense": True,
                "max_length": 1000
            }
    ):
        self.model_directory = Path(model_directory)
        self.model_name = model_name
        self.system_configuration = system_configuration
        self.inference_configuration = inference_configuration
        self.model_interface: Optional[BGEM3FlagModel] = None

    @property
    def model_path(self) -> pathlib.Path:
        return self.model_directory / self.model_name

    def _load_model_interface(self, **kwargs: Any) -> None:
        self.model_interface = BGEM3FlagModel(
            str(self.model_path), **self.system_configuration, **kwargs
        )

    def _model_exists(self, model_directory: Path, model_name: str) -> bool:
        directory_exists = (model_directory / model_name).exists()
        model_exists = (model_directory / model_name / "pytorch_model.bin").exists()
        config_exists = (model_directory / model_name / "config.json").exists()
        return all((directory_exists, model_exists, config_exists))

    def download_model(self, model_name: Optional[str] = None) -> None:
        if model_name is None:
            model_name = self.model_name

        if not self._model_exists(self.model_directory, model_name):
            # This method is used within FlagEmbedding to download the model.
            snapshot_download(
                repo_id=model_name,
                local_dir=str(self.model_path),
                ignore_patterns=["flax_model.msgpack", "rust_model.ot", "tf_model.h5"],
            )

    def vectorize(self, text: str, **kwargs: Any) -> List[float]:
        texts = [text]
        self.download_model(self.model_name)
        if self.model_interface is None:
            logger.warning(
                "Trying to vectorize without initialising the interference interface, "
                "loading it automatically!"
            )
            self._load_model_interface()

        if self.model_interface is None:
            raise RuntimeError

        inference_kwargs = {**self.inference_configuration, **kwargs}
        result = self.model_interface.encode(texts, **inference_kwargs)

        # We actually have only one vector as the function takes in a single text
        vector = result["dense_vecs"][0]
        # Translate numpy floats into regular ones
        float_vector = [float(c) for c in vector]
        return float_vector
    
    def vectorize_records(self, records: List[dict], **kwargs: Any) -> List[dict]:
        """ Vectorize in batches for faster execution. """
        
        self.download_model(self.model_name)
        
        if self.model_interface is None:
            logger.warning(
                "Trying to vectorize without initialising the inference interface, "
                "loading it automatically!"
            )
            self._load_model_interface()

        if self.model_interface is None:
            raise RuntimeError("Model interface could not be initialized.")
        
        batch_size = 1000
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            texts = [record.get(FIELD_TO_VECTORIZE) for record in batch]
            inference_kwargs = {**self.inference_configuration, **kwargs}
            result = self.model_interface.encode(texts, **inference_kwargs)

            for j, vector in enumerate(result["dense_vecs"]):
                # Translate numpy floats into regular ones
                float_vector = [float(c) for c in vector]
                records[i + j][VECTOR_FIELD_NAME] = float_vector
                
        return records