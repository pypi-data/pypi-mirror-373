from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import jmespath
import asyncio
from pydantic.json import pydantic_encoder
import json

from inspect import signature, Signature, Parameter
from functools import wraps


def pieql(param_name: str = "__schema"):

    def decorator(func):
        sig = signature(func)
        params = list(sig.parameters.values())

        has_request = True
        if "request" not in sig.parameters:
            params.append(Parameter("request",
                                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                                    annotation=Request))
            has_request = False
        wrapper_sig = Signature(params)

        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            if has_request:
                kwargs["request"] = request

            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

            schema = request.query_params.get(param_name)
            if not schema:
                return result

            if not isinstance(result, JSONResponse):
                return result

            data = json.loads(result.body)

            try:
                filtered = jmespath.search(schema, data)
            except Exception as e:
                return JSONResponse({"error": f"Invalid PieQL query: {schema}: {e}"}, status_code=400)

            return filtered

        wrapper.__signature__ = wrapper_sig
        return wrapper

    return decorator


QLType = Any
