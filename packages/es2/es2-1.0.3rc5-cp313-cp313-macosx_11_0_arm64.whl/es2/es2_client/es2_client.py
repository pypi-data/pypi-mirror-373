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
ES2 Configuration Module

This module provides the ES2 class and related functions for managing connections, keys, and indexes.

Classes:
    ES2: Main class for managing ES2 operations.

Functions:
    init_connect: Initializes the connection to the ES2 server.
    init_index_config: Initializes the index configuration.
    create_index: Creates a new index.
    init: Initializes the ES2 environment.
"""

from typing import Optional

from es2.api import Indexer
from es2.crypto import KeyGenerator
from es2.crypto.parameter import ContextParameter, KeyParameter
from es2.index import Index, IndexConfig
from es2.utils.logging_config import logger


class ES2:
    """
    Main class for managing ES2 operations.

    Methods:
        init_connect(host, port, address, access_token): Initializes the connection to the ES2 server.
        register_key(key_id, key_path): Registers a key with the ES2 server.
        generate_and_register_key(key_id, key_path, preset): Generates and registers a key.
        init_index_config(key_path, key_id, preset, query_encryption, index_encryption, index_type):
            Initializes the index configuration.
        create_index(index_name, dim, index_encryption, index_type): Creates a new index.
        init(host, port, address, access_token, key_path, key_id, preset, query_encryption, \
            index_encryption, index_type, auto_key_setup):
            Initializes the ES2 environment.
    """

    def __init__(self):
        """
        Initializes the ES2 class.
        """
        self._indexer = None
        self._index_config = None

    @property
    def indexer(self):
        """
        Returns the indexer object.

        Raises:
            ValueError: If the indexer is not initialized.
        """
        if not self._indexer:
            raise ValueError("Indexer is not initialized. Call init_connect first.")
        return self._indexer

    @indexer.setter
    def indexer(self, indexer: Indexer):
        """
        Sets the indexer object.

        Args:
            indexer (Indexer): The indexer object.

        Raises:
            ValueError: If the indexer is not an instance of Indexer.
        """
        if not isinstance(indexer, Indexer):
            raise ValueError("Indexer must be an instance of Indexer.")
        self._indexer = indexer
        return self

    @property
    def index_config(self):
        """
        Returns the index configuration.

        Raises:
            ValueError: If the index configuration is not initialized.
        """
        if not self._index_config:
            raise ValueError("Index config is not initialized. Call init_index_config first.")
        return self._index_config

    @index_config.setter
    def index_config(self, index_config: IndexConfig):
        """
        Sets the index configuration.

        Args:
            index_config (IndexConfig): The index configuration.

        Raises:
            ValueError: If the index configuration is not an instance of IndexConfig.
        """
        if not isinstance(index_config, IndexConfig):
            raise ValueError("Index config must be an instance of IndexConfig.")
        self._index_config = index_config
        return self

    @property
    def is_connected(self):
        """
        Checks if the ES2 client is connected to the server.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.indexer.is_connected()

    def disconnect(self):
        """
        Disconnects the ES2 client from the server.
        """
        if self.indexer:
            self.indexer.disconnect()
            logger.info("Disconnected from ES2 server.")
        else:
            logger.warning("No active connection to disconnect.")

    def register_key(
        self,
        key_id: Optional[str] = None,
    ):
        """
        Registers a key with the ES2 server.

        Args:
            key_id (str): The key ID.
            key_path (str): The path to the key.

        Raises:
            ValueError: If the indexer is not initialized.
        """
        if key_id is None:
            key_id = self.index_config.key_id
        if key_id is not None:
            self.index_config.key_id = key_id
        if self.index_config.key_param.check_key_dir():
            logger.info(
                f"Keys in {self.index_config.key_path} with key_id: {self.index_config.key_id} "
                f"already exists. Checking for registered keys."
            )
            key_list = self.indexer.get_key_list()
            if key_list and self.index_config.key_id in key_list:
                logger.info(f"Key {self.index_config.key_id} already registered in {self.index_config.key_path}.")
                return
            else:
                logger.info(f"Registering key {self.index_config.key_id} from {self.index_config.key_path}.")
                self.indexer.register_key(self.index_config.key_id, self.index_config.eval_key_path)
            return
        else:
            raise ValueError(
                f"Keys in {self.index_config.key_path} with key_id: {self.index_config.key_id} do not exist. "
                "Please generate keys first."
            )

    def get_key_list(self):
        """
        Retrieves the list of registered keys.

        Returns:
            list: A list of registered keys.

        Raises:
            ValueError: If the indexer is not initialized.
        """
        return self.indexer.get_key_list()

    def get_key_info(self, key_id: Optional[str] = None):
        """
        Retrieves the information of the registered keys.

        Returns:
            dict: A dictionary containing key information.

        Raises:
            ValueError: If the indexer is not initialized.
        """
        if key_id is None:
            key_id = self.index_config.key_id
        return self.indexer.get_key_info(key_id)

    def get_index_list(self):
        """
        Retrieves the list of registered index.

        Returns:
            list: A list of registered indexes.

        Raises:
            ValueError: If the indexer is not initialized.
        """
        return self.indexer.get_index_list()

    def generate_key(self, key_id: Optional[str] = None):
        """
        Generates a key using the KeyGenerator.

        Args:
            key_id (str): The key ID.
            key_path (str): The path to the key.
            preset (str): The preset for the key.

        Returns:
            KeyGenerator: The KeyGenerator instance used to generate the key.
        """
        if key_id is not None:
            self.index_config.key_id = key_id
        if self.index_config.key_param.check_key_dir():
            logger.info(f"Keys in {self.index_config.key_path} with key_id: {self.index_config.key_id} already exists.")
            return
        else:
            logger.info(
                f"Generating keys in {self.index_config.key_path} with key_id: {self.index_config.key_id} "
                f"using preset: {self.index_config.context_param}. "
            )
            keygen = KeyGenerator._create_from_parameter(
                context_param=self.index_config.context_param, key_param=self.index_config.key_param
            )
            keygen.generate_keys()
        return

    def generate_and_register_key(
        self,
    ):
        """
        Generates and registers a key.

        Args:
            key_id (str): The key ID.
            key_path (str): The path to the key.
            preset (str): The preset for the key.
        """
        if self.index_config.key_param.check_key_dir():
            logger.info(
                f"Keys in {self.index_config.key_path} with key_id: {self.index_config.key_id} "
                f"already exists. Checking for existing keys."
            )
            key_list = self.indexer.get_key_list()
            if key_list and self.index_config.key_id in key_list:
                logger.info(f"Key {self.index_config.key_id} already registered in {self.index_config.key_path}.")
                return
            else:
                logger.info(f"Registering key {self.index_config.key_id} from {self.index_config.key_path}.")
                self.register_key()
            return

        else:
            logger.info(
                f"Generating keys in {self.index_config.key_path} with key_id: {self.index_config.key_id} "
                f"using preset: {self.index_config.context_param}. "
            )
            self.generate_key()
            self.register_key()

    @property
    def context_param(self) -> "ContextParameter":
        """
        Returns the context parameters.

        Returns:
            ContextParameter: The context parameters.
        """
        return self.index_config.context_param

    @property
    def key_param(self) -> "KeyParameter":
        """
        Returns the key parameters.

        Returns:
            KeyParameter: The key parameters.
        """
        return self.index_config.key_param

    def init_connect(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        address: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        """
        Initializes the connection to the ES2 server.

        Args:
            host (str, optional): The host address.
            port (int, optional): The port number.
            address (str, optional): The full address.
            access_token (str, optional): The access token.

        Returns:
            ES2: The initialized ES2 object.

        Raises:
            ValueError: If neither host and port nor address are provided.

        Examples:
            Initialize ES2 environment:
                >>> es2_client = ES2()
                >>> es2_instance = es2_client.init_connect(
                ...     host="localhost",
                ...     port=50050,
                ...     )
        """
        if host and port:
            address = f"{host}:{port}"
        elif not address:
            raise ValueError("Either host and port or address must be provided.")
        indexer = Index.init_connect(address=address, access_token=access_token)
        self.indexer = indexer
        return self

    def init_index_config(
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
        auto_key_setup: Optional[bool] = True,
    ):
        """
        Initializes the index configuration.

        Args:
            index_name (str, optional): The name of the index.
            dim (int, optional): The dimensionality of the index.
            key_path (str, optional): The path to the key. Defaults to None.
            key_id (str, optional): The key ID. Defaults to None.
            seal_mode (str, optional): The seal mode. Defaults to None.
            preset (str, optional): The preset for the key. Defaults to None.
            eval_mode (str, optional): The evaluation mode. Defaults to None.
            query_encryption (str, optional): The encryption type for query,
            e.g. "plain", "cipher", "hybrid". Defaults to None.
            index_encryption (str, optional): The encryption type for database,
            e.g. "plain", "cipher", "hybrid". Defaults to None.
            index_type (str, optional): The type of index. Defaults to None.

        Examples:
            Initialize ES2 environment:
                >>> es2_client = ES2()
                >>> es2_client.init_index_config(
                ...     key_path="./keys",
                ...     key_id="example_key",
                ...     preset="ip",
                ...     query_encryption="plain",
                ...     index_encryption="cipher",
                ...     index_type="flat"
                ... )
        """
        if Index._default_key_path and Index._default_key_path != key_path:
            raise ValueError(
                f"Key path {key_path} does not match the default key path {Index._default_key_path}. "
                "Please reinitialize. es2.init()"
            )

        self.index_config = IndexConfig(
            index_name=index_name,
            dim=dim,
            key_path=key_path,
            key_id=key_id,
            seal_mode=seal_mode,
            preset=preset,
            eval_mode=eval_mode,
            query_encryption=query_encryption,
            index_encryption=index_encryption,
            index_type=index_type,
        )
        if auto_key_setup:
            if self.index_config.key_id is None:
                raise ValueError("Key ID must be provided to generate a key.")
            self.generate_key()
            self.register_key()

    def init(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        address: Optional[str] = None,
        access_token: Optional[str] = None,
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
        auto_key_setup: Optional[bool] = True,
    ):
        """
        Initializes the ES2 environment (connection, key, and index config).

        Parameters
        ----------
        host : str, optional
            The host address to connect to ES2 server.
        port : int, optional
            The port number to connect to ES2 server.
        address : str, optional
            The full address to connect to ES2 server.
        access_token : str, optional
            The access token to connect to ES2 server.
        index_name : str, optional
            The name of the index.
        dim : int, optional
            The dimensionality of the index.
        key_path : str, optional
            The path to the key directory.
        key_id : str, optional
            The key ID.
        seal_mode : str, optional
            The seal mode.
        preset : str, optional
            The preset for the key.
        eval_mode : str, optional
            The evaluation mode.
        query_encryption : str, optional
            The encryption type for query, e.g. "plain", "cipher", "hybrid". Defaults to ``plain``.
        index_encryption : str, optional
            The encryption type for database, e.g. "plain", "cipher", "hybrid". Defaults to ``cipher``.
        index_type : str, optional
            The type of index. Defaults to ``flat``.
            Currently, only ``flat`` index type is supported.
        auto_key_setup : bool, optional
            Whether to automatically generate and register the key. Defaults to ``True``.

        Returns
        -------
        ES2
            The initialized ES2 object.

        Examples
        --------
            >>> import es2
            >>> es2.init(
            ...     host="localhost",
            ...     port=50050,
            ...     key_path="./keys",
            ...     key_id="example_key",
            ...     auto_key_setup=True
            ... )

            >>> es2.init(
            ...     address="localhost:50050",
            ...     key_path="./keys",
            ...     auto_key_setup=False,
            ... )
        """
        if host is None and port is None and address is None:
            raise ValueError("Either host and port or address must be provided.")
        self.init_connect(host=host, port=port, address=address, access_token=access_token)
        Index.init_key_path(key_path)
        self.init_index_config(
            index_name=index_name,
            dim=dim,
            key_path=key_path,
            key_id=key_id,
            seal_mode=seal_mode,
            preset=preset,
            eval_mode=eval_mode,
            query_encryption=query_encryption,
            index_encryption=index_encryption,
            index_type=index_type,
            auto_key_setup=auto_key_setup,
        )
        return self

    def create_index(
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
        Creates a new index.

        Args:
            index_name (str): The name of the index.
            dim (int): The dimensionality of the index.
            index_encryption (str, optional): The encryption type for database, e.g. "plain", "cipher", "hybrid".
            index_type (str, optional): The type of index.

        Returns:
            Index: The created index.

        Examples:
            Create Index:
                >>> es2_client = ES2()
                >>> es2_client.init(
                ...     host="localhost",
                ...     port=50050,
                ...     key_path="./keys",
                ...     key_id="example_key",
                ...     preset="ip",
                ...     query_encryption="plain",
                ...     index_encryption="cipher",
                ...     index_type="flat"
                ... )
                >>> index = es2_client.create_index(
                ...     index_name="test_index",
                ...     dim=128
                ... )
        """
        index_config = self.index_config.deepcopy(
            index_name=index_name,
            dim=dim,
            key_path=key_path,
            key_id=key_id,
            seal_mode=seal_mode,
            preset=preset,
            eval_mode=eval_mode,
            query_encryption=query_encryption,
            index_encryption=index_encryption,
            index_type=index_type,
        )

        return Index.create_index(
            indexer=self.indexer,
            index_config=index_config,
        )

    def drop_index(self, index_name: str):
        """
        Drops the current index.

        Returns:
            Index: The current index after dropping it.

        Raises:
            ValueError: If the indexer is not connected.
        """
        if not self.indexer or not self.indexer.is_connected():
            raise ValueError("Indexer not connected. Please call Index.init_connect() first.")

        self.indexer.delete_index(index_name)
        return self

    def release_key(self, key_id: str):
        """
        Releases the key with the given key_id.

        Args:
            key_id (str): The ID of the key to release.

        Raises:
            ValueError: If the indexer is not connected.
        """
        if not self.indexer or not self.indexer.is_connected():
            raise ValueError("Indexer not connected. Please call Index.init_connect() first.")

        self.indexer.delete_key(key_id)
        logger.info(f"Key {key_id} released successfully.")
        return self

    @property
    def key_path(self):
        """
        Returns the path to the key directory.

        Returns:
            str: The path to the key directory.
        """
        return self.index_config.key_path

    def reset(self):
        """
        Resets the ES2 by deleting all index and registered key in Server.

        Returns:
            ES2: The reset ES2 object.
        """
        index_list = self.indexer.get_index_list()
        key_list = self.indexer.get_key_list()
        if index_list:
            logger.info(f"Indexes {index_list} will be cleared.")
            for index_name in index_list:
                self.drop_index(index_name)
        if key_list:
            logger.info(f"Keys {key_list} will be released.")
            for key_id in key_list:
                self.release_key(key_id)
        self._indexer = None
        self._index_config = None
        logger.info("ES2 instance has been reset.")
        return self


es2_client = ES2()

"""
Functions:
    init_connect: Initializes the connection to the ES2 server.
    init_index_config: Initializes the index configuration.
    create_index: Creates a new index.
    init: Initializes the ES2 environment.
"""


def init_connect(*args, **kwargs):
    """
    Initialize the connection to the ES2 server.

    Parameters
    ----------
    host : str, optional
        The host address to connect to ES2 server.
    port : int, optional
        The port number to connect to ES2 server.
    address : str, optional
        The full address (overrides host/port) to connect to ES2 server.
    access_token : str, optional
        The access token to connect to ES2 server.

    Returns
    -------
    ES2
        The initialized ES2 object.
    """
    return es2_client.init_connect(*args, **kwargs)


def init_index_config(*args, **kwargs):
    """
    Initialize the index configuration.

    Parameters
    ----------
    index_name : str, optional
        The name of the index.
    dim : int, optional
        The dimensionality of the index.
    key_path : str, optional
        The path to the key directory.
    key_id : str, optional
        The key ID.
    seal_mode : str, optional
        The seal mode.
    preset : str, optional
        The preset for the key.
    eval_mode : str, optional
        The evaluation mode.
    query_encryption : str, optional
        The encryption type for query, e.g. "plain", "cipher", "hybrid".
    index_encryption : str, optional
        The encryption type for database, e.g. "plain", "cipher", "hybrid".
    index_type : str, optional
        The type of index.
    auto_key_setup : bool, optional
        Whether to automatically generate/register the key (default True).

    Returns
    -------
    ES2
        The initialized ES2 object.
    """
    return es2_client.init_index_config(*args, **kwargs)


def create_index(*args, **kwargs):
    """
    Create a new index.

    Parameters
    ----------
    index_name : str, optional
        The name of the index.
    dim : int, optional
        The dimensionality of the index.
    key_path : str, optional
        The path to the key directory.
    key_id : str, optional
        The key ID.
    seal_mode : str, optional
        The seal mode.
    preset : str, optional
        The preset for the key.
    eval_mode : str, optional
        The evaluation mode.
    query_encryption : str, optional
        The encryption type for query, e.g. "plain", "cipher", "hybrid".
    index_encryption : str, optional
        The encryption type for database, e.g. "plain", "cipher", "hybrid".
    index_type : str, optional
        The type of index.

    Returns
    -------
    Index
        The created index object.
    """
    return es2_client.create_index(*args, **kwargs)


def init(*args, **kwargs):
    """
    Initialize the ES2 environment (connection, key, and index config).

    Parameters
    ----------
    host : str, optional
        The host address to connect to ES2 server.
    port : int, optional
        The port number to connect to ES2 server.
    address : str, optional
        The full address to connect to ES2 server.
    access_token : str, optional
        The access token to connect to ES2 server.
    index_name : str, optional
        The name of the index.
    dim : int, optional
        The dimensionality of the index.
    key_path : str, optional
        The path to the key directory.
    key_id : str, optional
        The key ID.
    seal_mode : str, optional
        The seal mode.
    preset : str, optional
        The preset for the key.
    eval_mode : str, optional
        The evaluation mode.
    query_encryption : str, optional
        The encryption type for query, e.g. "plain", "cipher", "hybrid". Defaults to ``plain``.
    index_encryption : str, optional
        The encryption type for database, e.g. "plain", "cipher", "hybrid". Defaults to ``cipher``.
    index_type : str, optional
        The type of index. Defaults to ``flat``.
        Currently, only ``flat`` index type is supported.
    auto_key_setup : bool, optional
        Whether to automatically generate and register the key. Defaults to ``True``.

    Returns
    -------
    ES2
        The initialized ES2 object.

    Examples
    --------
    >>> import es2
    >>> es2.init(
    ...     host="localhost",
    ...     port=50050,
    ...     key_path="./keys",
    ...     key_id="example_key",
    ...     auto_key_setup=True
    ... )

    >>> import es2
    >>> es2.init(
    ...     address="localhost:50050",
    ...     key_path="./keys",
    ...     auto_key_setup=False,
    )
    """
    return es2_client.init(*args, **kwargs)


def drop_index(index_name: str):
    """
    Drop the index with the given name.

    Parameters
    ----------
    index_name : str
        The name of the index to drop.

    Returns
    -------
    ES2
        The ES2 object after dropping the index.
    """
    return es2_client.drop_index(index_name)


def release_key(key_id: str):
    """
    Release the key with the given key_id.

    Parameters
    ----------
    key_id : str
        The ID of the key to release.

    Returns
    -------
    ES2
        The ES2 object after releasing the key.
    """
    return es2_client.release_key(key_id)


def generate_key(key_id: str):
    """
    Generate a key using the KeyGenerator.

    Parameters
    ----------
    key_id : str
        The ID of the key to generate.

    Returns
    -------
    None
    """
    return es2_client.generate_key(key_id)


def register_key(key_id: str):
    """
    Register a key with the ES2 server.

    Parameters
    ----------
    key_id : str
        The ID of the key to register.

    Returns
    -------
    None
    """
    return es2_client.register_key(key_id)


def reset():
    """
    Reset the ES2 by deleting all indexes and registered keys in the server.

    Returns
    -------
    ES2
        The reset ES2 object.
    """
    return es2_client.reset()


def is_connected():
    """
    Check if the ES2 client is connected to the server.

    Returns
    -------
    bool
        True if connected, False otherwise.
    """
    return es2_client.is_connected


def disconnect():
    """
    Disconnect the ES2 client from the server.
    """
    return es2_client.disconnect()


def get_key_list():
    """
    Retrieve the list of registered keys.

    Returns
    -------
    list
        A list of registered keys.
    """
    return es2_client.get_key_list()


def get_key_info(key_id: str):
    """
    Retrieve the information of the registered key.

    Parameters
    ----------
    key_id : str
        The key ID.

    Returns
    -------
    dict
        A dictionary containing key information.
    """
    return es2_client.get_key_info(key_id)


def get_index_list():
    """
    Retrieve the list of registered indexes.

    Returns
    -------
    list
        A list of registered indexes.
    """
    return es2_client.get_index_list()
