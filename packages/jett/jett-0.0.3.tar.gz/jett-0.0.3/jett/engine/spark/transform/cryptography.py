from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Literal

from pydantic import SecretStr

if TYPE_CHECKING:
    from pyspark.sql import Column, DataFrame, SparkSession

    PairCol = tuple[Column, str]

from ....__types import DictData
from .__abc import BaseSparkTransform


class GCMDecrypt(BaseSparkTransform):
    """GCM Decrypt Transform model."""

    op: Literal["gcm_decrypt"]
    name: str
    source: str
    secret_key: SecretStr
    encode_mode: Literal["base64"] = "base64"
    block_size: int = 16

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> PairCol:
        """Decryption with GCM mode.

        Args:
            df (Any): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.
        """
        from Crypto.Cipher import AES
        from Crypto.Hash import HMAC, SHA256
        from pyspark.errors import PythonException
        from pyspark.sql.functions import col, udf
        from pyspark.sql.types import StringType

        def __decrypt_gcm(
            cipher_test: str,
            secret_key: str,
            bs: int,
            encode: Literal["base64"],
        ) -> str:  # pragma: no cover
            """Create Wrapped function that will use for making PySpark UDF
            function via Python API.

            Warning: Fixing the case of SPARK-5063.

            Returns: str
            """
            secret_key = secret_key.encode()
            nonce = HMAC.new(secret_key, msg=b"", digestmod=SHA256).digest()
            cipher = AES.new(secret_key, AES.MODE_GCM, nonce, mac_len=bs)

            if encode == "base64":
                decode_func = base64.b64decode
            else:
                raise PythonException(f"not support encode mode: {encode}")

            try:
                decoded_data = decode_func(cipher_test)
                base64_text = decoded_data[:-bs]
                mac_tag = decoded_data[-bs:]
                decrypted_text = cipher.decrypt_and_verify(
                    base64_text, mac_tag
                ).decode("utf8")

            except Exception as e:
                raise PythonException(
                    f"decryption error, encrypted value: {cipher_test}, "
                    f"error message: {e}"
                ) from e

            return decrypted_text

        secret: str = self.secret_key.get_secret_value()
        block_size: int = self.block_size
        encode_mode: Literal["base64"] = self.encode_mode
        decrypt_udf = udf(
            lambda text: __decrypt_gcm(
                cipher_test=text,
                secret_key=secret,
                bs=block_size,
                encode=encode_mode,
            ),
            StringType(),
        )
        return decrypt_udf(col(self.source)), self.name
