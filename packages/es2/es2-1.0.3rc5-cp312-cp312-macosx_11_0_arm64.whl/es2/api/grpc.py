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

import secrets
from typing import List, Tuple, Union

import evi

from es2.api.connection import Connection
from es2.utils.logging_config import logger
from proto import es2_comm_type_pb2 as es2_type_pb
from proto.public.v1 import es2_msa_api_pb2_grpc as es2_grpc
from proto.public.v1 import es2_msa_message_pb2 as es2_msg_pb2

###################################
# Indexer Class
###################################


class Indexer:
    """
    High-level client for managing encrypted index and performing vector search operations on the ES2 server.

    This API provides:

    - Connection to the ES2 server (local or remote)
    - Key and context setup for homomorphic encryption at server side
    - Index creation, deletion, and management (encrypted/plain(TBD))
    - Batch or incremental vector insertion (encrypted/plain)
    - Encrypted similarity search
    - Both synchronous and asynchronous search operations

    Notes
    -----
    Instances should be created via the static `connect()` methods.

    Example
    --------

    >>> indexer = Indexer.connect("localhost:50050", access_token="your_access_token")
    >>> if indexer.is_connected():
    >>>     print("Connected to ES2 service.")
    >>> else:
    >>>     print("Failed to connect to ES2 service.")

    """

    def __init__(self, connection: Connection, access_token: str = None):
        self.connection = connection
        self.stub = es2_grpc.ES2PublicServiceStub(connection.get_channel())
        self.access_token = access_token
        self.grpc_metadata = []
        if self.access_token:
            self.grpc_metadata.append(("authorization", f"Bearer {self.access_token}"))

    ###################################
    # Connection Management
    ###################################

    @classmethod
    def connect(cls, address: str, access_token: str = None) -> "Indexer":
        """
        Establishes a connection to the ES2 service.

        Parameters
        ----------
        address : str
            The address of the ES2 service endpoint (e.g., "localhost:50051").
        access_token : str, optional
            Access token for authentication (default: None).

        Parameters
        ----------
        None

        Returns
        -------
        Indexer
            An instance of the Indexer class connected to the specified address.
        """
        secure = True if access_token else False
        conn = Connection(address, secure=secure)
        if not conn.is_connected():
            raise RuntimeError(f"Failed to connect to {address}")
        return cls(conn, access_token)

    def is_connected(self):
        """
        Checks if the ES2 connection is active.

        Returns
        -------
        bool
            True if the connection is active, False otherwise.
        """
        return self.connection.is_connected()

    def disconnect(self):
        """
        Closes the ES2 connection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.connection.close()

    ###################################
    # Key Management
    ###################################

    def register_key(
        self, key_id: str, key_path: str, key_type: str = "EvalKey", preset: str = "IP", eval_mode: str = "RMP"
    ):
        """
        Registers a public key from the specified file path to ES2 server.

        Parameters
        ----------
        key_id : str
            The unique identifier for the key.
        key_path : str
            The file path to the key to be registered.
        preset : str
            The preset to use for the key. Default is "IP".
        eval_mode : str
            The evaluation mode to use for the key. Default is "RMP".

        Returns
        -------
        None
        """

        def register_key_request_generator():
            try:
                with open(key_path, "rb") as key_file:
                    while True:
                        chunk = key_file.read(1 * 1024 * 1024)  # 1MB씩 읽기
                        if not chunk:
                            break
                        request = es2_msg_pb2.RegisterKeysRequest()
                        request.header.type = es2_type_pb.MessageType.RegisterKeys

                        request.key_info.key_id = key_id
                        request.key_info.type = key_type
                        request.key_info.preset = preset
                        request.key_info.eval_mode = eval_mode
                        # TODO: request.key_info.sha256sum = ""

                        request.key.value = chunk
                        request.key.size = len(chunk)
                        yield request

            except Exception as e:
                logger.error(f"Error reading key file '{key_path}': {e}")
                return

        response = self.stub.RegisterKeys(
            register_key_request_generator(),
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to register key with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Key '{key_id}' registered successfully.")

    def get_key_list(self):
        """
        Get a list of all registered key IDs.

        Returns
        -------
        Optional[List[str]]
            A list of registered key IDs, or None if the request failed.
        """
        request = es2_msg_pb2.GetKeyListRequest()

        request.header.type = es2_type_pb.MessageType.GetKeyList

        response = self.stub.GetKeyList(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to list keys with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info("Get key list successfully.")
            key_list = list(response.key_id)
            if len(key_list) == 0:
                logger.info("No keys registered in the ES2 server.")
            return key_list

    def get_key_info(self, key_id: str):
        """
        Retrieves key information about a specific key from ES2 server.

        Parameters
        ----------
        key_id : str
            The unique identifier for the key.

        Returns
        -------
        Optional[dict]
            A dictionary containing key information (key_id, key_type, dim, url), or None if the request failed.
        """
        request = es2_msg_pb2.GetKeyInfoRequest()

        request.header.type = es2_type_pb.MessageType.GetKeyInfo
        request.key_id = key_id

        response = self.stub.GetKeyInfo(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to get key info with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Key info for '{key_id}' received successfully.")

            return {
                "key_id": key_id,
                "key_type": response.key_info.type,
                "preset": response.key_info.preset,
                "eval_mode": response.key_info.eval_mode,
                "sha256sum": response.key_info.sha256sum,
            }

    def delete_key(self, key_id: str):
        """
        Deletes a registered key by its ID from ES2 server.

        Parameters
        ----------
        key_id : str
            The unique identifier for the key to be deleted.

        Returns
        -------
        None
        """
        request = es2_msg_pb2.DeleteKeyRequest()
        request.header.type = es2_type_pb.MessageType.DeleteKey
        request.key_id = key_id

        response = self.stub.DeleteKey(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to delete key with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Key '{key_id}' deleted successfully.")

    ###################################
    # Index Management
    ###################################

    def create_index(
        self,
        index_name: str,
        key_id: str,
        dim: int,
        search_type: str = "ip",
        index_encryption: str = "cipher",
        query_encryption: str = "plain",
    ):
        """
        Creates a new index into ES2 server.

        Index includes the following information:
        - Encrypted Vectors to store
        - Metadata for each vector

        Parameters
        ----------
        index_name : str
            The name of the index to be created.
        key_id : str
            The unique identifier for the key associated with the index.
        dim : int
            Vector dimension to be stored in the index.
        search_type : Union[str, es2_type_pb.SearchType], optional
            The type of search to be performed on the index (default: "ip").
        index_encryption : str, optional
            The type of index to be created (default: "cipher"). Options are "plain" or "cipher".
        query_encryption : str, optional
            The type of query to be performed on the index (default: "plain"). Options are "plain" or "cipher".

        Returns
        -------
        None
        """
        request = es2_msg_pb2.CreateIndexRequest()
        request.header.type = es2_type_pb.MessageType.CreateIndex

        if isinstance(search_type, str):
            if search_type.lower() == "iponly" or search_type.lower() == "ip":
                search_type = es2_type_pb.SearchType.IPOnly
            elif search_type.lower() == "ipandqf" or search_type.lower() == "qf":
                search_type = es2_type_pb.SearchType.IPAndQF
            else:
                logger.debug(f"Invalid search type: {search_type}. Defaulting to IPOnly.")
                search_type = es2_type_pb.SearchType.IPOnly

        elif isinstance(search_type, int):
            if search_type not in [es2_type_pb.SearchType.IPOnly, es2_type_pb.SearchType.IPAndQF]:
                logger.debug(f"Invalid search type: {search_type}. Defaulting to IPOnly.")
                search_type = es2_type_pb.SearchType.IPOnly
            else:
                search_type = search_type
        else:
            raise ValueError(f"Invalid type for search_type: {type(search_type)}.")

        if isinstance(index_encryption, str) and index_encryption.lower() in ["plain", "cipher", "hybrid"]:
            index_encryption = index_encryption.lower()
        else:
            raise ValueError(f"Invalid index_encryption: {index_encryption}. Expected 'plain' or 'cipher'.")

        request.index_info.index_name = index_name
        request.index_info.dim = dim
        request.index_info.search_type = search_type
        request.index_info.key_id = key_id
        request.index_info.index_encryption = index_encryption
        request.index_info.query_encryption = query_encryption

        response = self.stub.CreateIndex(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(f"Failed to create index with error code {response.header.return_code}: {response.header}")
        else:
            logger.info(f"Index '{index_name}' created successfully.")
            return {
                "index_name": index_name,
                "dim": dim,
                "search_type": search_type,
                "key_id": key_id,
                "index_encryption": index_encryption,
                "query_encryption": query_encryption,
            }

    def get_index_list(self):
        """
        Get a list of all index names in ES2 server.

        Parameters
        ----------
        None

        Returns
        -------
        Optional[List[str]]
            A list of index names, or None if the request failed.
        """
        request = es2_msg_pb2.GetIndexListRequest()
        request.header.type = es2_type_pb.MessageType.GetIndexList

        response = self.stub.GetIndexList(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to get index list with error code {response.header.return_code}: "
                f"{response.header.error_message}"
            )
        else:
            logger.info("Get Index list received successfully.")
            return list(response.index_names)

    def get_index_info(self, index_name: str):
        """
        Retrieves information about a specific index from ES2 server.

        Parameters
        ----------
        index_name : str
            The name of the index to retrieve information for.

        Returns
        -------
        Optional[dict]
            A dictionary containing index information (index_name, dim, row_count, search_type, key_id, created_time),
                or None if the request failed.
        """
        request = es2_msg_pb2.GetIndexInfoRequest()
        request.header.type = es2_type_pb.MessageType.GetIndexInfo
        request.index_name = index_name

        response = self.stub.GetIndexInfo(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to get index info with error code "
                f"{response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Index info for '{index_name}' received successfully.")
            return {
                "index_name": index_name,
                "dim": response.index_info.dim,
                "row_count": response.index_info.row_count,
                "search_type": es2_type_pb.SearchType.Name(response.index_info.search_type),
                "key_id": response.index_info.key_id,
                "index_encryption": response.index_info.index_encryption,
                "query_encryption": response.index_info.query_encryption,
                "created_time": response.index_info.created_time,
            }

    def delete_index(self, index_name: str):
        """
        Deletes a specified index from ES2 server.

        Parameters
        ----------
        index_name : str
            The name of the index to be deleted.

        Returns
        -------
        None
        """
        request = es2_msg_pb2.DeleteIndexRequest()
        request.header.type = es2_type_pb.MessageType.DeleteIndex
        request.index_name = index_name

        response = self.stub.DeleteIndex(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to delete index with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Index '{index_name}' deleted successfully.")

    ###################################
    # Data Management
    ###################################

    def insert_data(self, index_name: str, enc_vec: List[List[evi.SingleCiphertext]], metadata: List[str] = []):
        """
        Inserts encrypted data and their metadata into an index from ES2 server.

        Parameters
        ----------
        index_name : str
            The name of the index where data will be inserted.
        enc_vec : List[List[evi.SingleCiphertext]]
            A list of encrypted vectors to be inserted.
        metadata : List[str], optional
            A list of metadata strings associated with the data. The default is an empty list.

        Returns
        -------
        None
        """

        def insert_data_request_generator():
            for vec_idx, vec in enumerate(enc_vec):
                data = evi.serialize_query_to(vec)
                chunk_size = 1024 * 1024 * 1  # 1MB
                for offset in range(0, len(data), chunk_size):
                    request = es2_msg_pb2.InsertDataRequest()
                    request.header.type = es2_type_pb.MessageType.InsertData
                    request.index_name = index_name
                    chunk = data[offset : offset + chunk_size]
                    packed_vector = request.packed_vectors.add()
                    packed_vector.vector.cipher_vector.id = str(vec_idx)
                    packed_vector.vector.cipher_vector.data = chunk
                    packed_vector.num_vector = 1
                    if metadata and offset == 0:
                        packed_vector.metadata.append(metadata[vec_idx] if vec_idx < len(metadata) else "")
                    yield request

        response = self.stub.InsertData(
            insert_data_request_generator(),
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to insert data with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Data inserted successfully into index '{index_name}'.")

    def insert_data_bulk(
        self,
        index_name: str,
        enc_vec: List[List[evi.SingleCiphertext]],
        numitems: List[int],
        metadata: List[List[str]] = [],
    ):
        """
        Inserts encrypted data and their metadata into an index from ES2 server.

        Parameters
        ----------
        index_name : str
            The name of the index where data will be inserted.
        enc_vec : List[List[evi.SingleCiphertext]]
            A list of encrypted vectors to be inserted.
        metadata : List[str], optional
            A list of metadata strings associated with the data. The default is an empty list.

        Returns
        -------
        None
        """

        def insert_data_request_generator():
            for vec_idx, vec in enumerate(enc_vec):
                data = evi.serialize_query_to(vec)
                chunk_size = 1024 * 1024 * 1  # 1MB
                for offset in range(0, len(data), chunk_size):
                    request = es2_msg_pb2.InsertDataRequest()
                    request.header.type = es2_type_pb.MessageType.InsertData
                    request.index_name = index_name
                    chunk = data[offset : offset + chunk_size]
                    packed_vector = request.packed_vectors.add()
                    packed_vector.vector.cipher_vector.id = str(vec_idx)
                    packed_vector.vector.cipher_vector.data = chunk
                    packed_vector.num_vector = numitems[vec_idx] if vec_idx < len(numitems) else 1
                    if metadata and offset == 0:
                        for idx in range(packed_vector.num_vector):
                            packed_vector.metadata.append(
                                metadata[vec_idx][idx]
                                if vec_idx < len(metadata) and idx < len(metadata[vec_idx])
                                else ""
                            )
                    yield request

        # print("time to batch insert")
        response = self.stub.BatchInsertData(
            insert_data_request_generator(),
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to insert data with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Data inserted successfully into index '{index_name}'.")

    ###################################
    # Search APIs
    ###################################

    def search(self, index_name: str, query: List[List[float]]):
        """
        Performs encrypted similarity search on the specified index from ES2 server.
        ES2 server performs secure homomorphic encryption operations with the registered evaluation key.

        Parameters
        ----------
        index_name : str
            The name of the index to search.
        query : List[List[float]]
            A list of query vectors to search for.

        Returns
        -------
        List[evi.CiphertextLv0]
            A list of search results, or None if the request failed.
        """
        # PC Search gRPC call
        request = es2_msg_pb2.SearchRequest()
        request.header.type = es2_type_pb.MessageType.Search
        request.index_name = index_name

        for q in query:
            dt = es2_type_pb.DataType()
            dt.plain_vector.id = f"id-{secrets.token_hex(5)}"
            dt.plain_vector.data.extend(q)
            dt.plain_vector.dim = len(q)
            request.query_vector.append(dt)

        query_ids = [dt.plain_vector.id for dt in request.query_vector]

        response_stream = self.stub.Search(
            request,
            metadata=self.grpc_metadata,
        )

        results = {k: [] for k in query_ids}
        for response in response_stream:
            if response.header.return_code != es2_type_pb.ReturnCode.Success:
                raise ValueError(
                    f"Failed to search with error code {response.header.return_code}: {response.header.error_message}"
                )
            output = list(response.ctxt_score)[0]
            results[output.id].append(list(output.ctxt_score)[0])

        outputs = [es2_type_pb.CiphertextScore(id=query_id, ctxt_score=results[query_id]) for query_id in query_ids]

        return outputs

    def encrypted_search(self, index_name: str, enc_query: List[List[evi.SingleCiphertext]]):
        """
        Performs encrypted similarity search on the specified index from ES2 server.
        ES2 server performs secure homomorphic encryption operations with the registered evaluation key.

        Parameters
        ----------
        index_name : str
            The name of the index to search.
        query : List[CipherBlock]
            A list of encrypted query vectors to search for.

        Returns
        -------
        List[evi.CiphertextLv0]
            A list of search results, or None if the request failed.
        """
        # CC Search gRPC call
        request = es2_msg_pb2.SearchRequest()
        request.header.type = es2_type_pb.MessageType.EncryptedSearch
        request.index_name = index_name

        for vec in enc_query:
            dt = es2_type_pb.DataType()
            dt.cipher_vector.id = f"id-{secrets.token_hex(5)}"
            dt.cipher_vector.data = vec.serialize()
            request.query_vector.append(dt)

        query_ids = [dt.cipher_vector.id for dt in request.query_vector]

        response_stream = self.stub.Search(
            request,
            metadata=self.grpc_metadata,
        )

        results = {k: [] for k in query_ids}
        for response in response_stream:
            if response.header.return_code != es2_type_pb.ReturnCode.Success:
                raise ValueError(
                    f"Failed to search with error code {response.header.return_code}: {response.header.error_message}"
                )
            output = list(response.ctxt_score)[0]
            results[output.id].append(list(output.ctxt_score)[0])

        outputs = [es2_type_pb.CiphertextScore(id=query_id, ctxt_score=results[query_id]) for query_id in query_ids]

        return outputs

    ###################################
    # Query APIs
    ###################################

    def get_metadata(self, index_name: str, idx: Union[List, Tuple], fields: list[str] = []):
        """
        Retrieves metadata for specified indices and output fields in an index from ES2 server.

        Parameters
        ----------
        index_name : str
            The name of the index from which to retrieve metadata.
        idx : Union[List, Tuple]
            A list of Position objects specifying the shard and row indices for metadata retrieval.
        fields : List[str]
            A list of field names to retrieve from the metadata.
            The default is an empty list, which does not retrieve metadata.

        Returns
        -------
        Optional[List]
            A list of metadata entries for the specified positions and fields, or None if the request failed.
        """
        request = es2_msg_pb2.GetMetadataRequest()
        request.header.type = es2_type_pb.MessageType.GetMetadata
        request.index_name = index_name

        if isinstance(idx, list) or isinstance(idx, tuple):
            if isinstance(idx[0], dict):
                for position in idx:
                    pos = request.idx.add()
                    pos.shard_idx = position["shard_idx"]
                    pos.row_idx = position["row_idx"]

            elif isinstance(idx[0], list) or isinstance(idx[0], tuple):
                for position in idx:
                    pos = request.idx.add()
                    pos.shard_idx = position[0]
                    pos.row_idx = position[1]

        else:
            raise ValueError(f"Ambiguous format for idx: {type(idx)}.\nExpected 'List[Position]' or 'List[List[int]]'.")

        for field in fields:
            request.output_fields.append(field)

        response = self.stub.GetMetadata(
            request,
            metadata=self.grpc_metadata,
        )

        if response.header.return_code != es2_type_pb.ReturnCode.Success:
            raise ValueError(
                f"Failed to get metadata with error code {response.header.return_code}: {response.header.error_message}"
            )
        else:
            logger.info(f"Metadata for index '{index_name}' received successfully.")
            return list(response.metadata)
