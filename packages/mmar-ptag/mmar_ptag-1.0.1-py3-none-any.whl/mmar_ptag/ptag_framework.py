"""PTAG ~ 'Pydantic Type Adapter GRPC'"""

import types
from contextlib import contextmanager
from contextvars import ContextVar
from typing import TypeVar

from grpc import ServicerContext, StatusCode, insecure_channel
from loguru import logger

from .ptag_pb2 import PTAGResponse, PTAGRequest
from .ptag_pb2_grpc import PTAGServiceServicer, add_PTAGServiceServicer_to_server, PTAGServiceStub
from .utils_inspect import (
    FuncMetadata,
    extract_and_validate_obj_methods_metadatas,
    extract_interface_metadatas,
    bind_args,
)
from .logging_configuration import TRACE_ID, TRACE_ID_DEFAULT
from google.protobuf.message import Message


T = TypeVar("T")
TRACE_ID_VAR: ContextVar[str] = ContextVar(TRACE_ID, default=None)


@contextmanager
def contextualize(context: ServicerContext):
    metadata = dict(context.invocation_metadata())
    trace_id = metadata.get(TRACE_ID, TRACE_ID_DEFAULT)
    token = TRACE_ID_VAR.set(trace_id)
    try:
        with logger.contextualize(trace_id=trace_id):
            yield
    finally:
        TRACE_ID_VAR.reset(token)


class WrappedPTAGService(PTAGServiceServicer):
    def __init__(self, service_object):
        self.methods, self.metadatas = extract_and_validate_obj_methods_metadatas(service_object)

    def Invoke(self, request: Message, context: ServicerContext):
        method_name = request.FunctionName
        method = self.methods.get(method_name)
        method_metadata = self.metadatas.get(method_name)

        if method_metadata is None:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details(f"Method {method_name} not found")
            return PTAGResponse()

        args_adapter = method_metadata.args_adapter
        result_adapter = method_metadata.result_adapter

        # [args_bytes] -(args_adapter.validate)-> [args] -(method)-> [result] -(result_adapter.dump)-> [result_bytes]
        try:
            input_obj = args_adapter.validate_json(request.Payload)
            input_names = (am[0] for am in method_metadata.args_metadata)
            input_kwargs = dict(zip(input_names, input_obj))
            with contextualize(context):
                output_obj = method(**input_kwargs)
            payload = result_adapter.dump_json(output_obj)
            return PTAGResponse(FunctionName=method_name, Payload=payload)
        except Exception as e:
            logger.exception(f"Failed to process request: {e}")
            context.set_code(StatusCode.INTERNAL)
            context.set_details(str(e))
            return PTAGResponse()


def make_proxy(grpc_stub, func_metadata: FuncMetadata):
    mm = func_metadata

    # only **kwargs supported
    # [args] -(args_adapter.dump)-> [args_bytes] -(send)-> [result_bytes] -(return_adapter.validate)-> [result]
    def proxy(self, *args, **kwargs):
        if args:
            raise ValueError(f"Func `{mm.name}`: only kwargs supported, but args found: `{args}`")
        trace_id = kwargs.pop(TRACE_ID, None) or TRACE_ID_VAR.get()
        metadata = [(TRACE_ID, trace_id)] if trace_id else []

        args = bind_args(mm.args_metadata, kwargs)
        args_bytes = mm.args_adapter.dump_json(args)
        request = PTAGRequest(FunctionName=mm.name, Payload=args_bytes)
        response = grpc_stub.Invoke(request, metadata=metadata)
        result_bytes = response.Payload
        result = mm.result_adapter.validate_json(result_bytes)
        return result

    return proxy


class ClientProxy:
    def __init__(self, service_interface, grpc_stub):
        metadatas = extract_interface_metadatas(service_interface)

        for mm in metadatas.values():
            proxy = make_proxy(grpc_stub, mm)
            bound_func = types.MethodType(proxy, self)
            setattr(self, mm.name, bound_func)


def ptag_attach(server, service_object):
    """
    Attach a service object implementing the interface to a gRPC server.
    """
    service = WrappedPTAGService(service_object)
    add_PTAGServiceServicer_to_server(service, server)


def ptag_client(service_interface: T, address: str) -> T:
    """
    Create a dynamic client for the given interface at the provided gRPC address.
    """
    channel = insecure_channel(address)
    stub = PTAGServiceStub(channel)
    return ClientProxy(service_interface, stub)
