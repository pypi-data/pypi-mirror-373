# ========================================================================================
#  Copyright (C) 2025 CryptoLab Inc. All rights reserved.
#
#  This software is proprietary and confidential.
#  Unauthorized use, modification, reproduction, or redistribution is strictly prohibited.
#
#  Commercial use is permitted only under a separate, signed agreement with CryptoLab Inc.
#
#  For licensing inquiries or permission requests, please contact: pypi@cryptolab.co.kr
# ========================================================================================

"""
Index Module

This module provides classes and methods for managing index configurations and operations.

Classes:
    IndexConfig: Configuration class for index settings.
    Index: Class for managing index operations.

"""

from itertools import accumulate
from typing import List, Optional, Union

import numpy as np
from tqdm import tqdm

from es2.api import Indexer
from es2.crypto.block import CipherBlock
from es2.crypto.cipher import Cipher
from es2.crypto.parameter import ContextParameter, IndexParameter, KeyParameter
from es2.utils.logging_config import logger
from es2.utils.utils import topk

ENCRYPTION_BATCH_SIZE = 128


class IndexConfig:
    """
    Configuration class for index settings.

    Parameters
    ----------
    index_name : str, optional
        Name of the index.
    dim : int, optional
        Dimensionality of the index.
    key_path : str, optional
        Path to the key.
    key_id : str, optional
        ID of the key.
    seal_mode : str, optional
        Seal mode for the key.
    preset : str, optional
        Preset for the index.
    eval_mode : str, optional
        Evaluation mode for the index.
    query_encryption : str, optional
        The encryption type for query, e.g. "plain", "cipher", "hybrid".
    index_encryption : str, optional
        The encryption type for database, e.g. "plain", "cipher", "hybrid".
    index_type : str, optional
        Type of the index.

    Examples
    --------
    >>> from es2.index import IndexConfig, Index
    >>> index_config = IndexConfig(
    ...   key_path="./keys",
    ...   key_id="example_key",
    ...   preset="ip",
    ...   query_encryption="plain",
    ...   index_encryption="cipher",
    ...   index_type="flat",
    ...   index_name="test_index",
    ...   dim=128
    ... )
    >>> from es2.api import Indexer
    >>> indexer = Indexer.connect(address="localhost:50050")
    >>> index = Index.create_index(indexer=indexer, index_config=index_config)
    """

    def __init__(
        self,
        index_name: Optional[str] = None,
        dim: Optional[int] = None,
        key_path: Optional[str] = None,
        key_id: Optional[str] = None,
        seal_mode: Optional[str] = None,
        preset: Optional[str] = None,
        eval_mode: Optional[str] = None,
        query_encryption: Optional[str] = None,
        index_encryption: Optional[str] = None,
        index_type: Optional[str] = None,
    ):
        """
        Initializes the IndexConfig class.
        """
        self.index_name = index_name
        self.context_param = ContextParameter(preset=preset, dim=dim, eval_mode=eval_mode)
        self.key_param = KeyParameter(key_path=key_path, key_id=key_id, seal_mode=seal_mode)
        self.index_param = IndexParameter(
            index_encryption=index_encryption, query_encryption=query_encryption, index_type=index_type
        )

    @property
    def index_name(self) -> str:
        """
        Returns the index name.

        Returns:
            ``str``: Name of the index.
        """
        return self._index_name

    @index_name.setter
    def index_name(self, index_name: str):
        """
        Sets the index name.

        Args:
            index_name (str): Name of the index.
        """
        self._index_name = index_name
        return self

    @property
    def context_param(self) -> ContextParameter:
        """
        Returns the context parameter object.

        Returns:
            ContextParameter: The parameter object for this context.
        """
        return self._context_param

    @context_param.setter
    def context_param(self, context_param: ContextParameter):
        """
        Sets the context parameter object.

        Args:
            context_param (ContextParameter): The parameter object for this context.
        """
        self._context_param = context_param
        return self

    @property
    def key_param(self) -> KeyParameter:
        """
        Returns the key parameter object.

        Returns:
            KeyParameter: The parameter object for the key.
        """
        return self._key_param

    @key_param.setter
    def key_param(self, key_param: KeyParameter):
        """
        Sets the key parameter object.

        Args:
            key_param (KeyParameter): The parameter object for the key.
        """
        self._key_param = key_param
        return self

    @property
    def index_param(self) -> IndexParameter:
        """
        Returns the index parameter object.

        Returns:
            IndexParameter: The parameter object for the index.
        """
        return self._index_param

    @index_param.setter
    def index_param(self, index_param: IndexParameter):
        """
        Sets the index parameter object.

        Args:
            index_param (IndexParameter): The parameter object for the index.
        """
        self._index_param = index_param
        return self

    @property
    def preset(self) -> str:
        """
        Returns the preset.

        Returns:
            ``str``: Preset for the index.
        """
        return self.context_param.preset_name

    @preset.setter
    def preset(self, preset: str):
        """
        Sets the preset.

        Args:
            preset (str): Preset for the index.
        """
        self.context_param = ContextParameter(preset=preset, dim=self.dim, eval_mode=self.eval_mode)
        return self

    @property
    def dim(self) -> int:
        """
        Returns the dimensionality of the index.

        Returns:
            ``int``: Dimensionality of the index.
        """
        return self.context_param.dim

    @dim.setter
    def dim(self, dim: int):
        """
        Sets the dimensionality of the index.

        Args:
            dim (int): Dimensionality of the index.
        """
        self.context_param = ContextParameter(preset=self.preset, dim=dim, eval_mode=self.context_param.eval_mode)
        return self

    @property
    def eval_mode(self) -> str:
        """
        Returns the evaluation mode.

        Returns:
            ``str``: Evaluation mode for the context.
        """
        return self.context_param.eval_mode_name

    @eval_mode.setter
    def eval_mode(self, eval_mode: str):
        """
        Sets the evaluation mode.

        Args:
            eval_mode (str): Evaluation mode for the context.
        """
        self.context_param = ContextParameter(preset=self.preset, dim=self.dim, eval_mode=eval_mode)
        return self

    @property
    def search_type(self) -> str:
        """
        Returns the search type.

        Returns:
            ``str``: Search type for the index.
        """
        return self.context_param.search_type

    @property
    def index_encryption(self) -> str:
        """
        Returns whether database encryption is enabled.

        Returns:
            ``str``: The encryption type for database, e.g. "plain", "cipher", "hybrid".
        """
        return self.index_param.index_encryption

    @index_encryption.setter
    def index_encryption(self, index_encryption: str):
        """
        Sets whether database encryption is enabled.

        Args:
            index_encryption (str): The encryption type for database, e.g. "plain", "cipher", "hybrid".
        """
        self.index_param = IndexParameter(
            index_encryption=index_encryption,
            query_encryption=self.query_encryption,
            index_type=self.index_type,
        )
        return self

    @property
    def query_encryption(self) -> str:
        """
        Returns whether query encryption is enabled.

        Returns:
            ``str``: The encryption type for query, e.g. "plain", "cipher", "hybrid".
        """
        return self.index_param.query_encryption

    @query_encryption.setter
    def query_encryption(self, query_encryption: str):
        """
        Sets whether query encryption is enabled.

        Args:
            query_encryption (str): The encryption type for query, e.g. "plain", "cipher", "hybrid".
        """
        self.index_param = IndexParameter(
            index_encryption=self.index_encryption,
            query_encryption=query_encryption,
            index_type=self.index_type,
        )
        return self

    @property
    def index_type(self) -> str:
        """
        Returns the index type.

        Returns:
            ``str``: Type of the index.
        """
        return self.index_param.index_type

    @index_type.setter
    def index_type(self, index_type: str):
        """
        Sets the index type.

        Args:
            index_type (str): Type of the index.
        """
        self.index_param = IndexParameter(
            index_encryption=self.index_encryption,
            query_encryption=self.query_encryption,
            index_type=index_type,
        )
        return self

    @property
    def key_path(self) -> str:
        """
        Returns the key path.

        Returns:
            ``str``: Path to the key.
        """
        return self.key_param.key_path

    @key_path.setter
    def key_path(self, key_path: str):
        """
        Sets the key path.

        Args:
            key_path (str): Path to the key.
        """
        if self.key_path is not None:
            raise ValueError("Key path is already set. Please re-initialize the IndexConfig.")
        self.key_param = KeyParameter(key_path=key_path, key_id=self.key_id)
        return self

    @property
    def key_id(self) -> str:
        """
        Returns the key ID.

        Returns:
            ``str``: ID of the key.
        """
        return self.key_param.key_id

    @key_id.setter
    def key_id(self, key_id: str):
        """
        Sets the key ID.

        Args:
            key_id (str): ID of the key.
        """
        self.key_param = KeyParameter(key_path=self.key_path, key_id=key_id)
        return self

    @property
    def seal_mode(self) -> str:
        """
        Returns the seal mode.

        Returns:
            ``str``: Seal mode for the keys.
        """
        return self.key_param.seal_mode_name

    @seal_mode.setter
    def seal_mode(self, seal_mode: str):
        """
        Sets the seal mode.

        Args:
            seal_mode (str): Seal mode for the keys.
        """
        self.key_param = KeyParameter(key_path=self.key_path, key_id=self.key_id, seal_mode=seal_mode)
        return self

    @property
    def eval_key_path(self) -> str:
        """
        Returns the evaluation key path.

        Returns:
            ``str``: Path to the evaluation key.
        """
        return self.key_param.eval_key_path

    @property
    def enc_key_path(self) -> str:
        """
        Returns the encryption key path.

        Returns:
            ``str``: Path to the encryption key.
        """
        return self.key_param.enc_key_path

    @property
    def sec_key_path(self) -> str:
        """
        Returns the secret key path.

        Returns:
            ``str``: Path to the secret key.
        """
        return self.key_param.sec_key_path

    @property
    def key_dir(self) -> str:
        """
        Returns the directory where the keys are stored.

        Returns:
            ``str``: Directory for the keys.
        """
        return self.key_param.key_dir

    @property
    def need_cipher(self) -> bool:
        """
        Returns whether cipher operations are needed.

        Returns:
            ``bool``: True if cipher operations are needed, False otherwise.
        """
        return self.query_encryption in ["cipher", "hybrid"] or self.index_encryption in ["cipher", "hybrid"]

    def deepcopy(
        self,
        index_name: Optional[str] = None,
        dim: Optional[int] = None,
        key_path: Optional[str] = None,
        key_id: Optional[str] = None,
        seal_mode: Optional[str] = None,
        preset: Optional[str] = None,
        eval_mode: Optional[str] = None,
        query_encryption: Optional[str] = None,
        index_encryption: Optional[str] = None,
        index_type: Optional[str] = None,
    ) -> "IndexConfig":
        """
        Creates a deep copy of the index configuration.

        Returns:
            IndexConfig: A deep copy of the index configuration.
        """
        new_config = IndexConfig(
            index_name=self._index_name if index_name is None else index_name,
            dim=self.context_param.dim if dim is None else dim,
            key_path=self.key_param.key_path if key_path is None else key_path,
            key_id=self.key_param.key_id if key_id is None else key_id,
            seal_mode=self.key_param.seal_mode if seal_mode is None else seal_mode,
            preset=self.context_param.preset if preset is None else preset,
            eval_mode=self.context_param.eval_mode if eval_mode is None else eval_mode,
            query_encryption=self.index_param.query_encryption if query_encryption is None else query_encryption,
            index_encryption=self.index_param.index_encryption if index_encryption is None else index_encryption,
            index_type=self.index_param.index_type if index_type is None else index_type,
        )
        return new_config

    def __repr__(self):
        return (
            "IndexConfig(\n"
            f"  index_name={self.index_name!r},\n"
            f"  dim={self.dim!r},\n"
            f"  key_path={self.key_path!r},\n"
            f"  key_id={self.key_id!r},\n"
            ")"
        )


class Index:
    """
    Class for managing index operations.

    Attributes
    ----------
    index_config : IndexConfig
        Configuration for the index.
    indexer : Indexer
        Indexer object for managing connections.
    num_entities : ``int``
        Number of entities in the index.
    cipher : Cipher
        Cipher object for encryption and decryption.

    Examples
    --------
    >>> from es2.index import IndexConfig, Index
    >>> from es2.api import Indexer
    >>> # Initialize index configuration
    >>> index_config = IndexConfig(
    ...   key_path="./keys",
    ...   key_id="example_key",
    ...   preset="ip",
    ...   query_encryption="plain",
    ...   index_encryption="cipher",
    ...   index_type="flat",
    ...   index_name="test_index",
    ...   dim=128
    ... )
    >>> # Connect to ES2
    >>> indexer = Indexer.connect(address="localhost:50050")
    >>> index = Index.create_index(indexer=indexer, index_config=index_config)
    >>> # Insert data into the index
    >>> data = [[0.001, 0.02, 0.03, ..., 0.127]]
    >>> metadata = ["example_metadata"]
    >>> index.insert(data=data, metadata=metadata)
    >>> # Encrypted Search in the index
    >>> query = [0.001, 0.02, 0.03, ..., 0.127]
    >>> results = index.search(query=query, top_k=3, output_fields=["metadata"])
    >>> print(results)
    """

    _default_key_path: Optional[str] = None
    _default_indexer: Optional[Indexer] = None

    def __init__(self, index_name: str, index_config: Optional[IndexConfig] = None):
        """
        Initializes the Index class.
        Check server connection and check if the index exists.

        Args:
            index_name (str): Name of the index.
        """
        if Index._default_indexer is None:
            raise ValueError("Indexer not connected. Please call Index.connect() first.")
        if Index._default_key_path is None:
            raise ValueError("Key path not set. Please call Index.init_key_path() first.")
        indexer = Index._default_indexer
        if index_name not in indexer.get_index_list():
            raise ValueError(f"Index '{index_name}' does not exist. Please run create_index first.")
        metadata = indexer.get_index_info(index_name)
        self.indexer = indexer
        self.index_config = index_config or IndexConfig(
            index_name=metadata["index_name"],
            dim=metadata["dim"],
            key_path=Index._default_key_path,
            key_id=metadata["key_id"],
            index_encryption=metadata["index_encryption"],
            query_encryption=metadata["query_encryption"],
        )
        self.num_entities = metadata["row_count"]
        self.cipher = Cipher._create_from_index_config(self.index_config) if self.index_config.need_cipher else None

    @classmethod
    def init_connect(cls, address: str, access_token: Optional[str] = None) -> "Indexer":
        """
        Connects to the indexer.

        Args:
            address (``str``): Address of the indexer.

        Returns:
            Indexer: Connected indexer object.
        """
        indexer = Indexer.connect(address=address, access_token=access_token)
        cls._default_indexer = indexer
        logger.info(f"Connection created at {address}")
        return indexer

    @classmethod
    def init_key_path(cls, key_path: str):
        """
        Initializes the key path for the index.

        Args:
            key_path (``str``): Path to the key directory.
        """
        cls._default_key_path = key_path
        return key_path

    @classmethod
    def create_index(cls, index_config: IndexConfig, indexer: Optional[Indexer] = None) -> "Index":
        """
        Creates a new index.

        Parameters
        ----------
        index_config : IndexConfig
            Configuration for the index.
        indexer : Indexer, optional
            Indexer object for managing connections.

        Returns
        -------
        Index
            The created index.

        Examples
        --------
        >>> from es2.index import IndexConfig, Index
        >>> from es2.api import Indexer
        >>> index_config = IndexConfig(
        ...   key_path="./keys",
        ...   key_id="example_key",
        ...   preset="ip",
        ...   query_encryption="plain",
        ...   index_encryption="cipher",
        ...   index_type="flat",
        ...   index_name="test_index",
        ...   dim=128
        ... )
        >>> indexer = Indexer.connect(address="localhost:50050")
        >>> index = Index.create_index(indexer=indexer, index_config=index_config)
        """
        active_indexer = indexer or cls._default_indexer
        if not active_indexer:
            raise ValueError("Indexer not connected. Please call Index.connect() first.")

        if not index_config.index_name or not index_config.dim:
            raise ValueError("Index name and dimension must be set.")

        if cls._default_key_path != index_config.key_path:
            raise ValueError(
                f"Key path {index_config.key_path} does not match the default key path {cls._default_key_path}. "
                "Please reinitialize. es2.init()"
            )
        key_list = active_indexer.get_key_list()
        if not key_list or index_config.key_id not in key_list:
            raise ValueError(f"Key ID '{index_config.key_id}' not found in Server. Please register key first.")
        active_indexer.create_index(
            index_name=index_config.index_name,
            key_id=index_config.key_id,
            dim=index_config.dim,
            search_type=index_config.search_type,
            index_encryption=index_config.index_encryption,
            query_encryption=index_config.query_encryption,
        )
        return cls(index_config.index_name, index_config)

    def insert(self, data: Union[List[List[float]], List[np.ndarray], List[CipherBlock]], metadata: List[any]):
        """
        Inserts data into the index.

        Parameters
        ----------
        data : list of floats or np.ndarray or CipherBlock
            Data to be inserted. It can be plaintext (list of lists or numpy arrays) or ciphertext (CipherBlock).
            Currently, only a list of ``CipherBlock`` is supported for encrypted data.
        metadata : str
            Metadata for the data.

        Returns
        -------
        Index
            The index object after insertion.

        Examples
        --------
        >>> data = [[0.001, 0.02, ..., 0.127]]
        >>> metadata = ["example_metadata"]
        >>> index.insert(data=data, metadata=metadata)
        """
        if isinstance(data[0], CipherBlock):
            if self.index_config.index_encryption not in ["cipher", "hybrid"]:
                raise ValueError("Index encryption must be enabled to insert CipherBlock data.")
        elif isinstance(data[0], (list, np.ndarray)):
            data = [np.array(item) for item in data]
            if not isinstance(data[0], np.ndarray):
                raise ValueError("Data must be a list of lists or numpy arrays.")
            if data[0].shape[0] != self.index_config.dim:
                raise ValueError(
                    f"Data dimension {data[0].shape[0]} does not match index dimension {self.index_config.dim}."
                )
        else:
            raise ValueError("Data must be a list of lists, numpy arrays, or CipherBlock.")

        self._insert_bulk(data, metadata=metadata)
        logger.debug("Data insertion completed successfully.")
        return self

    def _prepare_metadata_for_chunk(self, metadata_chunk: List[any], num_item_list: List[int]) -> List[List[any]]:
        """Partitions a chunk of metadata according to the num_item_list."""
        if not metadata_chunk:
            return []
        offsets = list(accumulate(num_item_list, initial=0))
        return [metadata_chunk[s:e] for s, e in zip(offsets, offsets[1:])]

    def _insert_chunk(self, data_chunk: CipherBlock, metadata: List[any] = None):
        """Inserts a single data chunk (CipherBlock) and its metadata into the indexer."""
        input_metadata = self._prepare_metadata_for_chunk(metadata, data_chunk.num_item_list)

        self.indexer.insert_data_bulk(
            self.index_config.index_name, data_chunk.data, data_chunk.num_item_list, input_metadata
        )
        self.num_entities += data_chunk.num_vectors

    def _insert_bulk(self, data: List[any], metadata: List[any] = None):
        """
        Bulk inserts data into the index.
        If the data is not encrypted, it will be encrypted before insertion.
        """
        # Case 1: Data is not encrypted (raw data)
        if not isinstance(data[0], CipherBlock):
            if self.index_config.index_encryption not in ["cipher", "hybrid"]:
                raise ValueError("Received unencrypted data, but index encryption is disabled.")

            num_items = len(data)
            logger.debug(f"Bulk encrypting {num_items} entities for index '{self.index_config.index_name}'.")
            for i in tqdm(range(0, num_items, ENCRYPTION_BATCH_SIZE), desc="Encrypt and Insert"):
                raw_data_chunk = data[i : i + ENCRYPTION_BATCH_SIZE]

                # Encrypt the data and convert it into a CipherBlock object
                encrypted_chunk = self.cipher.encrypt_multiple(raw_data_chunk, encode_type="item")

                metadata_chunk = metadata[i : i + ENCRYPTION_BATCH_SIZE] if metadata else None
                self._insert_chunk(encrypted_chunk, metadata_chunk)

        # Case 2: Data is already a list of CipherBlock objects
        else:
            num_total_vectors = sum(chunk.num_vectors for chunk in data)
            if metadata and num_total_vectors != len(metadata):
                raise ValueError("Metadata length does not match the total number of entities.")

            metadata_offset = 0
            for data_chunk in tqdm(data, desc="Insert CipherBlock Bulk"):
                if metadata:
                    num_chunk_entities = data_chunk.num_vectors
                    metadata_chunk = metadata[metadata_offset : metadata_offset + num_chunk_entities]
                    metadata_offset += num_chunk_entities
                else:
                    metadata_chunk = None

                self._insert_chunk(data_chunk, metadata_chunk)

        logger.debug("Data insertion completed successfully.")
        return self

    def search(
        self,
        query: Union[List[float], np.ndarray, List[List[float]], List[np.ndarray], List[CipherBlock]],
        top_k: int,
        output_fields: List[str] = None,
    ):
        """
        Searches the index.

        Parameters
        ----------
        query : list of float or np.ndarray
            Query vector.
        top_k : int, optional
            Number of top results to return (default 3).
        output_fields : list of str, optional
            Fields to include in the output.

        Returns
        -------
        list of dict
            Search results.

        Examples
        --------
        >>> query = [0.001, 0.02, ..., 0.127]
        >>> results = index.search(query=query, top_k=3, output_fields=["metadata"])
        >>> print(results)
        """
        result_ctxt_list = self.scoring(query)
        result_list = [self.cipher.decrypt_score(result_ctxt) for result_ctxt in result_ctxt_list]
        output_result_list = [self.get_topk_metadata_results(result, top_k, output_fields) for result in result_list]
        return output_result_list

    def scoring(
        self, query: Union[List[float], np.ndarray, CipherBlock, List[List[float]], List[np.ndarray], List[CipherBlock]]
    ):
        """
        Computes the scores for a query against the index.
        Args:
            query (list): Query vector.

        Returns:
            list of dict: Scores for the query.

        Raises:
            ValueError: If the index is not connected.

        Examples
        --------
        >>> query = [0.001, 0.02, 0.03, ..., 0.127]
        >>> result_ctxt = index.scoring(query=query)
        >>> print(result_ctxt)
        """
        if (
            # Plain Query
            (isinstance(query, list) and isinstance(query[0], float))
            or isinstance(query, np.ndarray)
            # Cipher Query
            or isinstance(query, CipherBlock)
        ):
            query = [query]  # If single query, make it form of multi query

        # Check whether plain query has proper dimension or not
        if isinstance(query, list) and (
            (isinstance(query[0], list) and isinstance(query[0][0], float)) or isinstance(query[0], np.ndarray)
        ):
            for i in query:
                i = np.array(i)
                if i.shape[0] != self.index_config.dim:
                    raise ValueError(
                        f"Query dimension {i.shape[0]} does not match index dimension {self.index_config.dim}."
                    )

        # Now, all query is form of multi query
        if self.index_config.query_encryption in ["cipher"]:  # CC
            # Encrypt multiple queries for each, if query was plaintext
            if (
                isinstance(query, List) and query and isinstance(query[0], List) and isinstance(query[0][0], float)
            ) or (isinstance(query, List) and isinstance(query[0], np.ndarray)):
                encrypted_query = [self.cipher.encrypt(i, encode_type="query") for i in query]
            else:
                encrypted_query = query
            # Do search with encrypted queries
            result_ctxt = self.indexer.encrypted_search(self.index_config.index_name, encrypted_query)
        else:  # PC
            # Do search with plain queries
            result_ctxt = self.indexer.search(self.index_config.index_name, query)
        return [CipherBlock(result) for result in result_ctxt]  # Return is always a list of CipherBlock

    def get_topk_metadata_results(self, result, top_k: int, output_fields: List[str] = None):
        """
        Get top-k metadata results from the search ciphertext result.

        Args:
            result (CipherBlock): The result context containing encrypted scores.
            top_k (int): Number of top results to return.
            output_fields (list of str, optional): Fields to include in the output.

        Returns:
            list of dict: List of dictionaries containing the top-k results with metadata.

        Raises:
            ValueError: If the indexer is not connected or if the result is empty.

        Examples
        --------
        >>> decrypted_scores = index.decrypt_score(result_ctxt, sec_key_path="./keys/SecKey.bin")
        >>> top_k_results = index.get_topk_metadata_results(result_ctxt, top_k=3, output_fields=["metadata"])
        >>> print(top_k_results)
        """
        topk_result, topk_indices = topk(result, top_k)
        metadata_result = self.indexer.get_metadata(self.index_config.index_name, topk_indices, fields=output_fields)
        output_result = []
        for i in range(len(topk_indices)):
            output_json = {
                "id": metadata_result[i].id,
                "score": topk_result[i][1],
                "metadata": metadata_result[i].infos,
            }
            output_result.append(output_json)
        return output_result

    def decrypt_score(self, result_ctxt: CipherBlock, sec_key_path: Optional[str] = None):
        """
        Decrypts the scores from the result context.

        Args:
            result_ctxt (CipherBlock): The result context containing encrypted scores.

        Returns:
            list of float: Decrypted scores.

        Examples
        --------
        >>> result_ctxt = index.scoring(query=query)
        >>> decrypted_scores = index.decrypt_score(result_ctxt, sec_key_path="./keys/SecKey.bin")
        >>> print(decrypted_scores)
        """
        if self.index_config.index_encryption not in ["cipher", "hybrid"]:
            raise ValueError("Index encryption is not enabled. Cannot decrypt scores.")
        return self.cipher.decrypt_score(result_ctxt, sec_key_path=sec_key_path)

    def drop(self):
        """
        Drops the index.

        Returns
        -------
        Index
            The index object after dropping it.

        Examples
        --------
        >>> index.drop()
        """
        if not self.is_connected:
            raise ValueError("Indexer not connected. Please call Index.connect() first.")
        self.indexer.delete_index(self.index_config.index_name)
        self.indexer = None
        self.index_config = None
        self.num_entities = 0
        return self

    @property
    def is_connected(self) -> bool:
        """
        Checks if the indexer is connected.

        Returns:
            ``bool``: True if the indexer is connected, False otherwise.
        """
        return self.index_config.index_name in self.indexer.get_index_list() if self.indexer else False

    def __repr__(self):
        return (
            "Index(\n"
            f"  {repr(self.index_config)},\n"
            f"  num_entities={self.num_entities},\n"
            f"  cipher={self.cipher if self.cipher else None}\n"
            ")"
        )
