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

from typing import List, Optional, Union

import evi
from evi import SingleCiphertext

from proto.es2_comm_type_pb2 import CiphertextScore


class CipherBlock:
    """
    CipherBlock class for handling ciphertexts.

    Ciphertexts can be either an encrypted vector or an encrypted similarity scores.
    """

    def __init__(self, data: Union[List[SingleCiphertext], CiphertextScore], enc_type: Optional[str] = None):
        self._is_score = None
        self.data = data
        self.enc_type = enc_type

    @property
    def data(self):
        return self._data

    @property
    def enc_type(self):
        return self._enc_type

    @property
    def is_score(self):
        return self._is_score

    @enc_type.setter
    def enc_type(self, value: Optional[str]):
        if value and value not in ["multiple", "single"]:
            raise ValueError("Invalid enc_type. Must be 'multiple' or 'single'.")
        self._enc_type = value

    @property
    def num_vectors(self):
        if not self.is_score:
            sum = 0
            for vec in self.data:
                sum += vec[0].n
            return sum
        else:
            raise ValueError("Invalid data type for num_vectors.")

    @property
    def num_item_list(self):
        if not self.is_score:
            item_list = []
            for vec in self.data:
                item_list.append(vec[0].n)
            return item_list
        else:
            raise ValueError("Invalid data type for num_item_list.")

    @property
    def num_ciphertexts(self):
        if not self.is_score:
            return len(self.data)
        else:
            raise ValueError("Invalid data type for num_ciphertexts.")

    @data.setter
    def data(self, value: Union[List[SingleCiphertext], List[List[SingleCiphertext]], CiphertextScore]):
        if not value:
            raise ValueError("Data list cannot be empty.")
        if isinstance(value, CiphertextScore):
            self._is_score = True
            self._data = value
            return self
        elif isinstance(value, list) and all(isinstance(v, SingleCiphertext) for v in value):
            self._is_score = False
            self.enc_type = "single"
            self._data = [value]
            return self
        elif isinstance(value, list) and all(
            isinstance(v, list) and all(isinstance(item, SingleCiphertext) for item in v) for v in value
        ):
            self._is_score = False
            self.enc_type = "multiple"
            self._data = value
            return self
        else:
            raise ValueError("Data must be a list of SingleCiphertext or CiphertextScore.")

    def serialize(self) -> bytes:
        """
        Serializes the CipherBlock to bytes.

        Returns:
            bytes: Serialized bytes of the CipherBlock.
        """
        if self.is_score is True:
            raise ValueError("CipherBlock data must be set before serialization.")
        return evi.serialize_query_to(self.data[0])
