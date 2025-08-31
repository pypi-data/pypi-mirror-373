from typing import Any, Dict, List, Union

from lano_valo_py.valo_types.valo_responses import APIResponseModel, BinaryData


class ResponceHelper:
    def data_convertor(self, result: APIResponseModel) -> List[Dict[str, Any]]:
        if result.data is None:
            raise ValueError(f"API response contains no data: {result}")

        if isinstance(result.data, bytes):
            if result.data != b"":
                raise ValueError("Unexpected bytes data in response")
            raise ValueError("Empty bytes data in response")

        result_data: Union[Dict[str, Any], List[Dict[str, Any]]] = result.data

        data: List[Dict[str, Any]] = (
            [result_data] if isinstance(result_data, dict) else result_data
        )

        return data

    def data_binary_convertor(self, result: APIResponseModel) -> BinaryData:
        if result.data is None:
            raise ValueError("API response contains no data")

        if isinstance(result.data, bytes):
            if not result.data:
                raise ValueError("Received empty binary data")
            return BinaryData(result.data)

        if isinstance(result.data, (dict, list)):
            raise TypeError("Failed data, expect binary data")

        raise TypeError(
            f"Cannot convert {type(result.data).__name__} to BinaryData. "
            "Expected bytes, dict, or list."
        )
