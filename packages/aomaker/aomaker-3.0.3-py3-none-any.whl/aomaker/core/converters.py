# --coding:utf-8--
from __future__ import annotations
from typing import TypeVar, TYPE_CHECKING, Optional, Type, Any, get_args, Union, Dict, get_origin, ForwardRef
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from uuid import UUID
import keyword
import sys

import cattrs
from attrs import has, define, field
from cattrs import Converter as CattrsConverter

if TYPE_CHECKING:
    from .api_object import BaseAPIObject
from .base_model import ContentType, EndpointConfig, HTTPMethod, ParametersT, PreparedRequest, RequestBodyT, \
    MultipartFormDataRequest
from .request_builder import JSONRequestBuilder, FormURLEncodedRequestBuilder, MultipartFormDataRequestBuilder, \
    RequestBuilder, TextPlainRequestBuilder

REQUEST_BUILDERS = {
    ContentType.JSON: JSONRequestBuilder,
    ContentType.FORM: FormURLEncodedRequestBuilder,
    ContentType.MULTIPART: MultipartFormDataRequestBuilder,
    ContentType.TEXT: TextPlainRequestBuilder
}

T = TypeVar('T')

cattrs_converter = CattrsConverter()

# ===== Python关键字alias自动处理 =====

def _get_keyword_alias_fields(cls):
    """检测attrs类中需要重命名的字段（包括Python关键字和非法字符字段名）"""
    if not has(cls):
        return {}
    
    field_aliases = {}
    for attr in cls.__attrs_attrs__:
        # 策略1：检查字段是否有alias且alias是Python关键字
        if hasattr(attr, 'alias') and attr.alias and keyword.iskeyword(attr.alias):
            field_aliases[attr.name] = attr.alias
        # 策略2：检查字段名是否以_结尾，且去掉_后是Python关键字
        elif attr.name.endswith('_') and keyword.iskeyword(attr.name[:-1]):
            field_aliases[attr.name] = attr.name[:-1]
        # 策略3：检查metadata中是否有original_name（用于处理连字符等非法字符）
        elif hasattr(attr, 'metadata') and attr.metadata and 'original_name' in attr.metadata:
            field_aliases[attr.name] = attr.metadata['original_name']
    return field_aliases

def _auto_configure_field_alias_renaming(cls):
    """自动为使用字段别名的attrs类配置cattrs重命名规则（包括Python关键字和非法字符字段名）"""
    field_aliases = _get_keyword_alias_fields(cls)
    
    if not field_aliases:
        return  # 没有字段别名，无需配置
    
    # 准备cattrs.override参数
    overrides = {}
    for field_name, alias in field_aliases.items():
        overrides[field_name] = cattrs.override(rename=alias)
    
    # 配置unstructure（对象 -> 字典）
    cattrs_converter.register_unstructure_hook(
        cls,
        cattrs.gen.make_dict_unstructure_fn(
            cls,
            cattrs_converter,
            **overrides
        )
    )
    
    # 配置structure（字典 -> 对象）
    cattrs_converter.register_structure_hook(
        cls,
        cattrs.gen.make_dict_structure_fn(
            cls,
            cattrs_converter,
            **overrides
        )
    )

def _ensure_field_alias_configured(cls):
    """确保指定类型的字段别名重命名已配置（包括Python关键字和非法字符字段名）"""
    if cls is None:
        return
    
    # 如果是attrs类且还没有配置过重命名规则
    if has(cls) and not hasattr(cls, '_aomaker_field_alias_configured'):
        _auto_configure_field_alias_renaming(cls)
        # 标记已配置，避免重复配置
        cls._aomaker_field_alias_configured = True


# ===== 结构化钩子（将原始数据转换为对象）=====

# datetime 结构化钩子
def datetime_structure_hook(value, _type):
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    elif isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value)
    else:
        raise ValueError(f"无法将 {value} 转换为 datetime")


# date 结构化钩子
def date_structure_hook(value, _type):
    if isinstance(value, str):
        return date.fromisoformat(value)
    else:
        raise ValueError(f"无法将 {value} 转换为 date")


# time 结构化钩子
def time_structure_hook(value, _type):
    if isinstance(value, str):
        return time.fromisoformat(value)
    else:
        raise ValueError(f"无法将 {value} 转换为 time")
    
    
def _register_union_structure_hooks():
    """注册Union类型的structure hook来处理复杂的Union类型"""

    def _resolve_forward_ref(arg):
        """将 ForwardRef 解析为真实类型；解析失败返回 None"""
        if not isinstance(arg, ForwardRef):
            return arg
        name = getattr(arg, "__forward_arg__", None)
        modname = getattr(arg, "__forward_module__", None)
        namespaces = []
        if modname and modname in sys.modules:
            namespaces.append(sys.modules[modname].__dict__)
        if "__main__" in sys.modules:
            namespaces.append(sys.modules["__main__"].__dict__)
        namespaces.append(globals())
        for ns in namespaces:
            try:
                return eval(name, ns, ns)
            except Exception:
                continue
        return

    def _resolve_container_param_type(tp):
        """解析容器类型参数中的 ForwardRef，并尽量重建参数化类型"""
        resolved = _resolve_forward_ref(tp) or tp
        origin = get_origin(resolved)
        if origin is None:
            return resolved
        args = get_args(resolved)
        if not args:
            return resolved
        # 解析内部 ForwardRef
        new_args = tuple(_resolve_forward_ref(a) or a for a in args)
        try:
            # PEP 585: 内置容器类型可用下标构造（list[int]、dict[str, int]）
            if len(new_args) == 1:
                return origin[new_args[0]]
            return origin[new_args]
        except Exception:
            # 无法重建参数化类型则返回已解析的 resolved
            return resolved

    def structure_union_hook(obj, union_type):
        """智能处理Union类型的转换"""
        union_args = get_args(union_type)
        if not union_args:
            return obj

        # 优先：当 obj 是 dict 时，先尝试转换为最具体的 attrs 类
        if isinstance(obj, dict):
            # 1) dict -> attrs 类（优先）
            for arg_type in union_args:
                resolved = _resolve_forward_ref(arg_type) or arg_type
                target = get_origin(resolved) or resolved  # 兼容 typing 泛型（如 Dict[str, Any]）
                if (hasattr(target, '__attrs_attrs__') and
                        target not in (dict, Dict)):
                    try:
                        return cattrs_converter.structure(obj, target)
                    except Exception:
                        continue
            # 2) dict -> 参数化映射类型（例如 Dict[str, T]），用于深度结构化 value
            for arg_type in union_args:
                candidate = _resolve_container_param_type(arg_type)
                origin = get_origin(candidate) or candidate
                if origin in (dict, Dict):
                    try:
                        return cattrs_converter.structure(obj, candidate)
                    except Exception:
                        continue
            return obj

        # 容器类型优先做深度结构化（避免被 isinstance 短路）
        # list / tuple / set -> 参数化容器类型（例如 List[T]、Tuple[T,...]、Set[T]）
        if isinstance(obj, (list, tuple, set)):
            for arg_type in union_args:
                candidate = _resolve_container_param_type(arg_type)
                origin = get_origin(candidate) or candidate
                if origin in (list, tuple, set):
                    try:
                        return cattrs_converter.structure(obj, candidate)
                    except Exception:
                        continue

        # 兜底：如果对象已经是 Union 中某个类型，直接返回
        for arg_type in union_args:
            resolved = _resolve_forward_ref(arg_type) or arg_type
            target = get_origin(resolved) or resolved
            if target is Any or target in (dict, Dict):
                continue
            try:
                if isinstance(obj, target):
                    # 若为参数化容器，则让 cattrs 进一步深度结构化
                    if get_args(resolved):
                        try:
                            return cattrs_converter.structure(obj, resolved)
                        except Exception:
                            return obj
                    return obj
            except TypeError:
                # 遇到 typing 泛型（如 typing.Dict[...]）不能直接用于 isinstance
                continue

        return obj

    def is_union_type(tp):
        """检查是否是Union类型"""
        return get_origin(tp) is Union

    cattrs_converter.register_structure_hook_func(
        is_union_type,
        structure_union_hook
    )

# 注册结构化钩子
cattrs_converter.register_structure_hook(datetime, datetime_structure_hook)
cattrs_converter.register_structure_hook(date, date_structure_hook)
cattrs_converter.register_structure_hook(time, time_structure_hook)
cattrs_converter.register_structure_hook(UUID, lambda value, _: UUID(value))
cattrs_converter.register_structure_hook(Decimal, lambda value, _: Decimal(str(value)))
cattrs_converter.register_structure_hook(Enum, lambda value, cls: cls(value))
_register_union_structure_hooks()
# ===== 反结构化钩子（将对象转换为可序列化数据）=====

# 注册反结构化钩子
cattrs_converter.register_unstructure_hook(
    datetime,
    lambda dt: dt.isoformat() if dt else None
)
cattrs_converter.register_unstructure_hook(
    date,
    lambda d: d.isoformat() if d else None
)
cattrs_converter.register_unstructure_hook(
    time,
    lambda t: t.isoformat() if t else None
)
cattrs_converter.register_unstructure_hook(
    UUID,
    lambda uuid_obj: str(uuid_obj) if uuid_obj else None
)
cattrs_converter.register_unstructure_hook(
    Decimal,
    lambda dec: str(dec) if dec else None
)
cattrs_converter.register_unstructure_hook(
    Enum,
    lambda enum_obj: enum_obj.value if enum_obj else None
)


def multipart_unstructure_hook(req: MultipartFormDataRequest) -> dict:
    return {
        "method": req.method,
        "url": req.url,
        "headers": cattrs_converter.unstructure(req.headers),
        "params": cattrs_converter.unstructure(req.params),
        "data": cattrs_converter.unstructure(req.data),
        "files": req.files,  # 不让 cattrs 误判为 Mapping，直接透传
    }

cattrs_converter.register_unstructure_hook(MultipartFormDataRequest, multipart_unstructure_hook)


@define
class RequestConverter:
    api_object: BaseAPIObject = field(default=None)
    _converter: CattrsConverter = field(default=cattrs_converter)

    def convert(self) -> dict:
        request_data = self.prepare()
        builder = self.get_request_builder()
        req = builder.build_request(request_data)
        unstructured_req = self._serialize_data(req)
        return unstructured_req

    def unstructure(self, data: Any) -> Any:
        """结构化数据 -> 原始数据"""
        if data is not None:
            _ensure_field_alias_configured(type(data))

            if isinstance(data, (list, tuple, set)):
                for item in data:
                    if has(item):
                        _ensure_field_alias_configured(type(item))
            elif isinstance(data, dict):
                for v in data.values():
                    if has(v):
                        _ensure_field_alias_configured(type(v))
        return self._converter.unstructure(data)

    def structure(self, data: Any, type_: Type[T]) -> Any:
        """原始数据 -> 结构化数据"""
        _ensure_field_alias_configured(type_)
        return self._converter.structure(data, type_)

    def get_request_builder(self) -> RequestBuilder:
        builder_class = REQUEST_BUILDERS.get(self.content_type)
        if not builder_class:
            raise ValueError(f"Unsupported content type: {self.content_type}")
        return builder_class()

    @property
    def base_url(self) -> str:
        return self.api_object.base_url

    @property
    def content_type(self) -> ContentType:
        return self.api_object.content_type

    @property
    def endpoint_config(self) -> EndpointConfig:
        return self.api_object.endpoint_config

    @property
    def route(self) -> str:
        route = self._replace_route_params(self.endpoint_config.route).lstrip("/")
        return route

    def post_prepare(self, prepared_data: PreparedRequest) -> PreparedRequest:
        """子类可重写此方法对最终请求数据进行调整"""
        return prepared_data

    def prepare(self) -> PreparedRequest:
        params = self.prepare_params()
        request_body = self.prepare_request_body()
        
        if params is not None:
            _ensure_field_alias_configured(type(params))
        if request_body is not None:
            _ensure_field_alias_configured(type(request_body))
            
        request_data = {
            "method": self.endpoint_config.method.value,
            "url": self.prepare_url(),
            "headers": self.prepare_headers(),
            "params": params,  # 结构化对象
            "request_body": request_body,  # 结构化对象
            "files": self.prepare_files() if self.content_type == ContentType.MULTIPART else None,
        }

        unstructured_request_data = self._serialize_data(request_data)
        prepared_request_data = PreparedRequest(**unstructured_request_data)
        return self.post_prepare(prepared_request_data)

    def prepare_url(self) -> str:
        base_url = self.base_url
        return f"{base_url}/{self.route}"

    def prepare_method(self) -> HTTPMethod:
        method = self.endpoint_config.method.value
        return method

    def prepare_headers(self) -> dict:
        return self.api_object.headers or {}

    def prepare_params(self) -> Optional[ParametersT]:
        return self.api_object.query_params

    def prepare_request_body(self) -> Optional[RequestBodyT]:
        return self.api_object.request_body

    def prepare_files(self) -> dict:
        if hasattr(self.api_object, 'files') and self.api_object.files:
            return self.api_object.files
        return {}

    def _replace_route_params(self, route: str) -> str:
        # 路由参数替换
        for path_param in (self.endpoint_config.route_params or []):
            if hasattr(self.api_object.path_params, path_param):
                value = getattr(self.api_object.path_params, path_param)
                route = route.replace(f"{{{path_param}}}", str(value))
            else:
                raise ValueError(f"Missing required route parameter: {path_param}")
        return route

    def _serialize_data(self, data):
        """统一解构 + 清理空值"""
        unstructured = self.unstructure(data)
        return self._remove_nones(unstructured)

    def _remove_nones(self, obj):
        if isinstance(obj, dict):
            return {k: self._remove_nones(v) for k, v in obj.items() if v is not None}
        elif isinstance(obj, list):
            return [self._remove_nones(v) for v in obj if v is not None]
        elif has(obj):  # Check if it's an attrs class
            return self._remove_nones(self.unstructure(obj))
        else:
            return obj
