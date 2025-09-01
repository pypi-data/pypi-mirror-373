from typing import Any, Callable, Optional, Union

from starlette.requests import Request
from starlette.responses import JSONResponse

try:
    from json import JSONEncoder as __JSONEncoder, JSONDecoder as __JSONDecoder
    import orjson as json
    from jwt.api_jwt import _jwt_global_obj, PyJWT as __PyJWT
    from jwt.api_jws import _jws_global_obj, PyJWS as __PyJWS
    from jwt import DecodeError as __DecodeError
    import binascii as __binascii
    from jwt.utils import base64url_decode as __base64url_decode

    USE_ORJSON = True


    def __fix_inner_json_calls():
        def _encode_payload(
                self: __PyJWT,
                payload: dict[str, Any],
                headers: dict[str, Any] | None = None,
                json_encoder: type[__JSONEncoder] | None = None,
        ) -> bytes:
            return dumps(payload).encode("utf-8")

        def _decode_payload(self: __PyJWT, decoded: dict[str, Any]) -> Any:
            try:
                payload = loads(decoded["payload"])
            except ValueError as e:
                raise __DecodeError(f"Invalid payload string: {e}") from e
            if not isinstance(payload, dict):
                raise __DecodeError("Invalid payload string: must be a json object")
            return payload

        def _load(self: __PyJWS, jwt: str | bytes) -> tuple[bytes, bytes, dict[str, Any], bytes]:
            if isinstance(jwt, str):
                jwt = jwt.encode("utf-8")

            if not isinstance(jwt, bytes):
                raise __DecodeError(f"Invalid token type. Token must be a {bytes}")

            try:
                signing_input, crypto_segment = jwt.rsplit(b".", 1)
                header_segment, payload_segment = signing_input.split(b".", 1)
            except ValueError as err:
                raise __DecodeError("Not enough segments") from err

            try:
                header_data = __base64url_decode(header_segment)
            except (TypeError, __binascii.Error) as err:
                raise __DecodeError("Invalid header padding") from err

            try:
                header = loads(header_data)
            except ValueError as e:
                raise __DecodeError(f"Invalid header string: {e}") from e

            if not isinstance(header, dict):
                raise __DecodeError("Invalid header string: must be a json object")

            try:
                payload = __base64url_decode(payload_segment)
            except (TypeError, __binascii.Error) as err:
                raise __DecodeError("Invalid payload padding") from err

            try:
                signature = __base64url_decode(crypto_segment)
            except (TypeError, __binascii.Error) as err:
                raise __DecodeError("Invalid crypto padding") from err

            return (payload, signing_input, header, signature)

        _jwt_global_obj._decode_payload = _decode_payload.__get__(_jws_global_obj, __PyJWT)
        _jwt_global_obj._encode_payload = _encode_payload.__get__(_jwt_global_obj, __PyJWT)
        _jws_global_obj._load = _load.__get__(_jws_global_obj, __PyJWS)


    def __fix_request_class():
        async def orjson(self: Request) -> Any:
            if not hasattr(self, "_json"):  # pragma: no branch
                body = await self.body()
                self._json = loads(body)
            return self._json

        Request.json = orjson


    def __fix_json_response_class():
        def render(self: JSONResponse, content: Any) -> bytes:
            return dumps_bytes(content)

        JSONResponse.render = render


    __fix_inner_json_calls()
    __fix_request_class()
    __fix_json_response_class()


    def dumps(obj: Any, default: Optional[Callable[[Any], Any]] = None, sort_keys: bool = False) -> str:
        if sort_keys:
            options = json.OPT_SORT_KEYS
        else:
            options = None
        return json.dumps(obj, default=default, option=options).decode("utf-8")


    def dumps_bytes(obj: Any, default: Optional[Callable[[Any], Any]] = None, sort_keys: bool = False) -> bytes:
        if sort_keys:
            options = json.OPT_SORT_KEYS
        else:
            options = None
        return json.dumps(obj, default=default, option=options)


    def loads(obj: Union[bytes, bytearray, memoryview, str]) -> Any:
        return json.loads(obj)


    class JSONEncoder(__JSONEncoder):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)

        def encode(self, o: Any) -> str:
            return dumps(o, default=self.default, sort_keys=self.sort_keys)


    class JSONDecoder(__JSONDecoder):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)

        def decode(self, s: Union[bytes, bytearray, memoryview, str], _w=None) -> Any:
            return loads(s)


except ImportError:
    from json import JSONEncoder, JSONDecoder
    import json

    USE_ORJSON = False


    def dumps(obj: Any, default: Optional[Callable[[Any], Any]] = None, sort_keys: bool = False) -> str:
        return json.dumps(obj, default=default, ensure_ascii=False, sort_keys=sort_keys,
                          allow_nan=False, indent=None, separators=(',', ':'))


    def loads(obj: Union[bytes, bytearray, str]) -> Any:
        return json.loads(obj)

__all__ = ["USE_ORJSON", "dumps", "loads", "JSONEncoder", "JSONDecoder"]
