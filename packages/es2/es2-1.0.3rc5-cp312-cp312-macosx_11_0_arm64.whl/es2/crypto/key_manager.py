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

import json
from pathlib import Path
from typing import List, Optional, Union

import evi

from es2.crypto.context import Context
from es2.crypto.parameter import ContextParameter, KeyParameter

from ..utils.utils import is_empty_dir

# *********************************************************************
# * Key Generation Module for ES2 workflow (CCMM)
# * Plans for now:
#     1. Make pybind11 wrapper of HEaaN-FR (DONE)
#     2. Keygen class just need to call pybind11 wrapped code + a (WIP)
# *********************************************************************


###################################
# KeyGenerator Class
###################################


def convert_string_to_seal_mode(sMode):
    if sMode.upper() == "NONE":
        return evi.SealMode.NONE
    elif sMode.upper() == "AES_KEK":
        return evi.SealMode.AES_KEK
    else:
        raise ValueError(f"Unknown SealMode: {sMode}. Supported modes are: NONE, AES_KEK.")


###################################
# KeyGenerator Class
###################################


class KeyGenerator:
    """
    Key Generator with the given parameters.

    Parameters
    ------------
    key_path : str
        The path where keys will be stored.
    dim_list : list, optional
        List of dimensions for the context. Defaults to powers of 2 from 32 to 4096.
    preset : str, optional
        The parameter preset to use for the context. Defaults to "ip".
    seal_mode : str, optional
        The seal mode for the keys. Defaults to "none".
    eval_mode : str, optional
        The evaluation mode for the context. Defaults to "RMP".

    Example
    --------
    >>> keygen = KeyGenerator("./keys")
    >>> keygen.generate_keys()
    """

    def __init__(
        self,
        key_path,
        dim_list: Optional[Union[int, List[int]]] = None,
        preset: Optional[str] = "ip",
        seal_mode: Optional[str] = "none",
        eval_mode: Optional[str] = "RMP",
    ):
        if dim_list is None:
            dim_list = [2**i for i in range(5, 13)]
        if isinstance(dim_list, int):
            dim_list = [dim_list]
        context_list = [Context(preset, d, eval_mode)._context for d in dim_list]
        self.sInfo = evi.SealInfo(convert_string_to_seal_mode(seal_mode))
        key_param = KeyParameter(key_path=key_path, seal_mode=seal_mode)
        self._key_generator = evi.MultiKeyGenerator(context_list, key_path, self.sInfo)
        self._context_param = ContextParameter(preset, eval_mode=eval_mode)
        self._key_param = key_param
        self._dim_list = dim_list
        self.key_path = key_path

    @classmethod
    def _create_from_parameter(cls, context_param: ContextParameter, key_param: KeyParameter):
        """
        Initializes the KeyGenerator with the given context and key parameters.

        Args:
            context_param (ContextParameter): The context parameters for the key generation.
            key_param (KeyParameter): The key parameters for the key generation.
        """
        return cls(
            key_param.key_dir,
            preset=context_param.preset_name,
            eval_mode=context_param.eval_mode,
            seal_mode=key_param.seal_mode_name,
        )

        # *********************************************************************
        # Call HEaaN-FR keygen code which is member of ES2.KeyGenerator
        # With this, key file will be autoimatically saved to key_path
        # *********************************************************************

    def generate_keys(self):
        """
        Generate all keys including encryption, evaluation, and secret keys.

        Parameters
        ----------
        None

        Returns
        -------
        KeyGenerator: The KeyGenerator instance with generated keys.
        """

        # Ensure the key path exists, create directories if necessary
        key_path = Path(self.key_path).expanduser().resolve()
        key_path.mkdir(parents=True, exist_ok=True)

        # Check if the directory is empty
        if not is_empty_dir(self.key_path):
            raise ValueError(f"Key path '{self.key_path}' is not empty. Key generation canceled.")

        # Generate keys
        self._key_generator.generate_keys()

        # Create metadata JSON
        metadata = {
            "preset": self._context_param.preset_name,
            "eval_mode": self._context_param.eval_mode_name,
            "seal_mode": self._key_param.seal_mode_name,
            "dim_list": self._dim_list,
        }
        metadata_path = Path(self._key_param.key_dir) / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)

        return self

    # def generate_secret_key(self):
    # 	# This function generates secret key only
    # 	# When if user generated secret key, return it
    # 	return self.key_generator.generateSecKey()

    # def generate_public_keys(self):
    # 	# This function generates public keys only
    # 	# This function cannot be called before secret key has been generated
    # 	self.key_generator.generatePublicKey(self.key_dir + "SecKey.bin")
    # 	# TODO) Public key generation with secret key that has loaded to memory space
    # 	# Like, self.key_generator.generate_pub_key(ES2.FRSecKey)
