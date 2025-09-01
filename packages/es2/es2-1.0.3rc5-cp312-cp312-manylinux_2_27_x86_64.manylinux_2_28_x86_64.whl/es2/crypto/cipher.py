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
Cipher Module

This module provides encryption and decryption functionalities for vectors and scores using the ES2 framework.

Classes:
    Cipher: Handles encryption and decryption operations.

Example:
    # Initialize with key paths
    cipher = Cipher(dim=512, enc_key_path="./temp/keys/EncKey.bin", sec_key_path="./temp/keys/SecKey.bin")
    vec = [0.0] * 512
    enc_vec = cipher.encrypt(vec, "item")
    dec_vec = cipher.decrypt(enc_vec)

    # Or specify key paths at method call
    cipher = Cipher(dim=512)
    enc_vec = cipher.encrypt(vec, enc_key_path="./temp/keys/EncKey.bin")
    dec_vec = cipher.decrypt(enc_vec, sec_key_path="./temp/keys/SecKey.bin")
"""

from typing import TYPE_CHECKING, Optional

import numpy as np

from es2.crypto.block import CipherBlock
from es2.crypto.decryptor import Decryptor
from es2.crypto.encryptor import Encryptor
from es2.crypto.parameter import ContextParameter

if TYPE_CHECKING:
    from es2.index import IndexConfig


class Cipher:
    """
    Cipher class for handling encryption and decryption operations.
    """

    def __init__(
        self,
        enc_key_path: Optional[str] = None,
        sec_key_path: Optional[str] = None,
        preset: Optional[str] = None,
        dim: Optional[int] = None,
        eval_mode: Optional[str] = None,
    ):
        if dim is None or not (dim >= 32 and dim <= 4096):
            raise ValueError("Dimension (dim) must be specified for Cipher initialization.")
        self._context_param = ContextParameter(preset=preset, dim=dim, eval_mode=eval_mode)
        if enc_key_path is not None:
            self._encryptor = Encryptor._create_from_context_parameter(self._context_param, enc_key_path)
        else:
            self._encryptor = None
        if sec_key_path is not None:
            self._decryptor = Decryptor._create_from_context_parameter(self._context_param, sec_key_path)
        else:
            self._decryptor = None
        self._sec_key_path = sec_key_path

    @classmethod
    def _create_from_index_config(cls, index_config: "IndexConfig"):
        """
        Initializes the Cipher class from an IndexConfig.

        Args:
            index_config (IndexConfig): The configuration for the index, including preset and key paths.
        """
        return cls(
            enc_key_path=index_config.enc_key_path,
            sec_key_path=index_config.sec_key_path,
            preset=index_config.preset,
            dim=index_config.dim,
            eval_mode=index_config.eval_mode,
        )

    def encrypt(self, vector, encode_type, enc_key_path: Optional[str] = None):
        """
        Encrypts a vector.

        Args:
            vector (Union[list, np.ndarray]): The vector to be encrypted.
            encode_type (str): The encoding type for encryption.
            enc_key_path (str, optional): The path to the encryption key file.
                If not provided, uses the key path set at initialization.

        Returns:
            CipherBlock : Encrypted vector.

        Examples:
            >>> cipher = Cipher(dim=512, enc_key_path="./temp/keys/EncKey.bin")
            >>> vec = [0.0] * 512
            >>> enc_vec = cipher.encrypt(vec, "item")

            >>> cipher = Cipher(dim=512)
            >>> vec = [0.0] * 512
            >>> enc_vec = cipher.encrypt(vec, enc_key_path="./temp/keys/EncKey.bin")
        """
        if isinstance(vector, list):
            vector = np.array(vector)
        if vector.shape[0] != self._context_param.dim:
            raise ValueError(
                f"Vector dimension {vector.shape[0]} does not match context dimension {self._context_param.dim}."
            )
        if enc_key_path:
            self._encryptor = Encryptor._create_from_context_parameter(self._context_param, enc_key_path)

        enc_res = self.encryptor.encrypt(vector, encode_type)
        return CipherBlock(data=enc_res, enc_type="single")

    def encrypt_multiple(self, vectors, encode_type, enc_key_path: Optional[str] = None, metadata=[]):
        """
        Encrypts a vector.

        Args:
            vector: The vector to be encrypted.
            encode_type: The encoding type for encryption.
            enc_key_path: Optional; The path to the encryption key file.
            If not provided, uses the key path set at initialization.

        Returns:
            Encrypted vector.

        Examples:
            >>> cipher = Cipher(dim=512, enc_key_path="./temp/keys/EncKey.bin")
            >>> vec = [0.0] * 512
            >>> enc_vec = cipher.encrypt(vec, "item")

            >>> cipher = Cipher(dim=512)
            >>> vec = [0.0] * 512
            >>> enc_vec = cipher.encrypt(vec, enc_key_path="./temp/keys/EncKey.bin")
        """
        if enc_key_path:
            self._encryptor = Encryptor._create_from_context_parameter(self._context_param, enc_key_path)

        enc_res = []
        enc_metadata = []
        enc_res = self.encryptor.encrypt_multiple(vectors, encode_type)
        meta_data_idx = 0
        for i in range(0, len(enc_res)):
            output = enc_res[i][0].n
            enc_metadata.append(metadata[meta_data_idx : meta_data_idx + output])
            meta_data_idx += output
        return CipherBlock(data=[enc_ctxt for enc_ctxt in enc_res], enc_type="multiple")

    def decrypt(self, encrypted_vector, sec_key_path: Optional[str] = None, idx: int = 0):
        """
        Decrypts an encrypted vector.

        Args:
            encrypted_vector (CipherBlock): The vector to be decrypted.
            sec_key_path (str, optional): The path to the secret key file for decryption.
                If not provided, uses the default path.

        Returns:
            ``list`` : Decrypted vector.

        Examples:
            >>> cipher = Cipher(dim=512, enc_key_path="./temp/keys/EncKey.bin")
            >>> enc_vec = cipher.encrypt([0.0] * 512, "item")
            >>> dec_vec = cipher.decrypt(enc_vec, sec_key_path="./temp/keys/SecKey.bin")
        """
        if not isinstance(encrypted_vector, CipherBlock):
            raise ValueError("The encrypted vector must be an instance of CipherBlock.")
        if encrypted_vector.is_score:
            raise ValueError("The encrypted vector must not be a score. use decrypt_score().")
        if sec_key_path is None:
            sec_key_path = self.sec_key_path
        if self._decryptor is None:
            self._decryptor = Decryptor._create_from_context_parameter(self._context_param)
        if encrypted_vector.enc_type == "single":
            return self.decryptor.decrypt(encrypted_vector.data[0], sec_key_path=sec_key_path)
        else:
            if idx < 0 or idx >= encrypted_vector.num_vectors:
                raise IndexError("Index out of range for the encrypted vector.")
            total = 0
            for i, count in enumerate(encrypted_vector.num_item_list):
                if idx < total + count:
                    block_idx = i
                    dec_idx = idx - total
                    break
                total += count
            return self.decryptor.decrypt_with_idx(encrypted_vector.data[block_idx], dec_idx, sec_key_path=sec_key_path)

    def decrypt_score(self, encrypted_score, sec_key_path: Optional[str] = None):
        """
        Decrypts an encrypted score.

        Args:
            encrypted_score (CipherBlock): The score to be decrypted.
            sec_key_path (str, optional): The path to the secret key file for decryption.
                If not provided, uses the default path set in Cipher initialization.

        Returns:
            ``list`` : Decrypted score.

        Examples:
            >>> result_ctxt = index.search(...)
            >>> dec_score = cipher.decrypt_score(result_ctxt, sec_key_path="./temp/keys/SecKey.bin")
        """
        if not isinstance(encrypted_score, CipherBlock):
            raise ValueError("The encrypted score must be an instance of CipherBlock.")
        if not encrypted_score._is_score:
            raise ValueError("The encrypted score must be a CipherBlock with is_score set to True.")
        if sec_key_path is None:
            sec_key_path = self.sec_key_path
        if self._decryptor is None:
            self._decryptor = Decryptor._create_from_context_parameter(self._context_param)

        return [
            self.decryptor.decrypt_score(score, sec_key_path=sec_key_path) for score in encrypted_score.data.ctxt_score
        ]

    @property
    def encryptor(self):
        """
        Returns the encryptor object.

        Returns:
            Encryptor: The encryptor object for encryption operations.
        """
        if self._encryptor is None:
            raise ValueError("Encryptor is not initialized. Ensure the encryption key path is set.")
        return self._encryptor

    @property
    def decryptor(self):
        """
        Returns the decryptor object.

        Returns:
            Decryptor: The decryptor object for decryption operations.
        """
        if self._decryptor is None:
            raise ValueError("Decryptor is not initialized. Ensure the secret key path is set.")
        return self._decryptor

    @property
    def sec_key_path(self):
        """
        Returns the path to the secret key file.

        Returns:
            ``str``: The path to the secret key file used for decryption.
        """
        if self._sec_key_path is None:
            raise ValueError("Secret key path is not set. Ensure the secret key file exists.")
        return self._sec_key_path
