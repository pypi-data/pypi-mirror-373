import inspect
from dataclasses import dataclass
from functools import cached_property
from typing import get_type_hints, TypeVar

from pydantic import TypeAdapter

from .logging_configuration import TRACE_ID


T = TypeVar("T")
ArgName = str
ArgDefault = any
ArgMetadata = tuple[ArgName, type, ArgDefault]
ArgsMetadata = list[ArgMetadata]
empty = inspect.Parameter.empty


@dataclass
class FuncMetadata:
    name: str
    args_metadata: ArgsMetadata
    args_type: type
    result_type: type

    @cached_property
    def args_adapter(self) -> TypeAdapter:
        return TypeAdapter(self.args_type)

    @cached_property
    def result_adapter(self) -> TypeAdapter:
        return TypeAdapter(self.result_type)


Methods = dict[str, callable]
Metadatas = dict[str, FuncMetadata]


def _parse_param(param) -> ArgMetadata | None:
    name = param.name
    param_type = param.annotation
    if param_type == empty:
        raise ValueError(f"Not found type for parameter `{name}`")
    # todo validate param_type: allow only builtins and pydantic
    default = param.default
    if default != empty and not isinstance(default, param_type):
        raise ValueError(f"For argument `{name}` type {param_type} is not aligned with default value: {default}")
    return (name, param_type, default)


def prettify_arg_metadata(arg_metadata: ArgMetadata):
    an, at, ad = arg_metadata
    atp = getattr(at, '__name__', at)
    if ad is empty:
        return f'{an}: {atp}'
    if ad == '':
        ad = "''"
    return f'{an}: {atp}={ad}'


def prettify_args_metatadata(args_metadata: ArgsMetadata):
    return ", ".join(prettify_arg_metadata(am) for am in args_metadata)


def _parse_args(func: callable) -> ArgsMetadata:
    signature = inspect.signature(func)
    parameters_all = list(signature.parameters.values())
    if parameters_all[0].name != "self":
        raise ValueError(f"Method with first `self` parameter expected, found: {parameters_all}")
    parameters = parameters_all[1:]
    args_metadata_0 = [_parse_param(param) for param in parameters]
    args_metadata = [am for am in args_metadata_0 if am]

    for param in parameters:
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            continue
        am_pretty = prettify_args_metatadata(args_metadata)
        signature = f"(self, *, {am_pretty})"
        msg_parts = [
            f"Keyword-Only parameters expected, found positional: `{param}`.",
            f"Probably enough to fix signature to `{signature}`.",
            "See https://peps.python.org/pep-3102/ for additional info",
        ]
        msg = " ".join(msg_parts)
        raise ValueError(msg)

    return args_metadata


def _bind_arg(arg_metadata: ArgMetadata, kwargs: dict):
    name, arg_type, default = arg_metadata
    if name in kwargs:
        arg_val = kwargs[name]
        if not isinstance(arg_val, arg_type):
            raise ValueError(f"Argument `{name}`: expected type `{arg_type}`, found: {type(arg_val)}")
    elif default is not empty:
        arg_val = default
    else:
        raise ValueError(f"Argument `{name}`: not found")
    return arg_val


def bind_args(args_metadata: ArgsMetadata, kwargs: dict) -> tuple:
    excess_args = set(kwargs) - set(am[0] for am in args_metadata)
    if excess_args:
        raise ValueError(f"Unexpected excess arguments passed: {excess_args}")
    args = tuple(_bind_arg(am, kwargs) for am in args_metadata)
    return args


def filter_trace_id(args_metadata: ArgsMetadata) -> ArgsMetadata:
    if not args_metadata:
        return args_metadata
    am_last = args_metadata[-1]
    if am_last == TRACE_ID:
        # todo check default arg
        args_metadata.pop()
        return args_metadata
    for am in args_metadata[:-1]:
        if am[0] == TRACE_ID:
            am_pretty = prettify_args_metatadata(args_metadata)
            raise ValueError(f"Bad signature [{am_pretty}]: unexpected trace_id on non-last position")
    return args_metadata


def _extract_func_metadata(func: callable) -> FuncMetadata | None:
    """
    Extract a func's type hints and return Pydantic adapters for the argument and return value.
    """
    func_name = func.__name__
    if func_name.startswith("_"):
        return None

    type_hints = get_type_hints(func)
    args_metadata = _parse_args(func)
    args_metadata = filter_trace_id(args_metadata)
    args_type = tuple[*(am[1] for am in args_metadata)]
    result_type = type_hints.get("return")
    if not result_type:
        raise ValueError(f"return type annotation for func `{func_name}` should present but not found!")
    func_metadata = FuncMetadata(
        name=func_name,
        args_metadata=args_metadata,
        args_type=args_type,
        result_type=result_type,
    )
    return func_metadata


def _extract_method_metadata(method: callable) -> FuncMetadata | None:
    func = method.__func__
    return _extract_func_metadata(func)


def extract_interface_metadatas(interface) -> Metadatas:
    metadatas = {}
    for name, func in inspect.getmembers(interface, predicate=inspect.isfunction):
        func_metadata = _extract_func_metadata(func)
        if func_metadata is None:
            raise ValueError(f"Failed to parse interface func: {func.__name__}")
        metadatas[name] = func_metadata
    return metadatas


def _extract_obj_methods_metadatas(obj) -> tuple[Methods, Metadatas]:
    methods, metadatas = {}, {}
    for name, method in inspect.getmembers(obj, predicate=inspect.ismethod):
        # also can see only on func from the base interface class
        func = method.__func__
        func_metadata = _extract_func_metadata(func)
        if func_metadata:
            methods[name] = method
            metadatas[name] = func_metadata
    return methods, metadatas


def _get_interface(obj):
    bases = obj.__class__.__bases__
    if len(bases) != 1:
        raise ValueError(f"Expected one base class, found: {bases}")
    interface = bases[0]
    return interface


def _get_full_class_name(cls):
    return cls.__module__ + "." + cls.__qualname__


def extract_and_validate_obj_methods_metadatas(obj):
    methods, metadatas = _extract_obj_methods_metadatas(obj)
    interface = _get_interface(obj)
    metadatas_i = extract_interface_metadatas(interface)
    if metadatas != metadatas_i:
        s_pref = f"service `{_get_full_class_name(type(obj))}`"
        i_pref = f"interface `{_get_full_class_name(interface)}`"
        sz = max(len(s_pref), len(i_pref))
        s_pref = s_pref.ljust(sz)
        i_pref = i_pref.ljust(sz)
        raise ValueError(f"Signatures mismatch between:\n{s_pref} :: {metadatas}\nand\n{i_pref} :: {metadatas_i}")
    return methods, metadatas
