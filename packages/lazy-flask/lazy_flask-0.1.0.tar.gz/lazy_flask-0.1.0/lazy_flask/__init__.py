# coding=utf-8
import json
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import (Any, Callable, Dict, List, Optional, Union, ClassVar)
from flask import Flask, request as flask_request, Response as FlaskResponse


class MiddlewareType(Enum):
    Request = 'Request'
    Response = 'Response'


@dataclass
class Middleware:
    func: Callable[[Any], Any]
    tag: Optional[str] = None
    weight: int = 0
    m_type: MiddlewareType = MiddlewareType.Request


@dataclass
class ModuleFunction:
    func: Callable
    tags: Optional[List[str]] = None


class Module:

    def __init__(self, name: str):
        self.name = name
        self._middleware: Dict[Optional[str], List[Middleware]] = {None: []}
        self._functions: Dict[str, ModuleFunction] = {}
        self._functions_registered = False

    def register_middleware(self, middleware: Middleware) -> None:
        if self._functions_registered:
            raise RuntimeError("Cannot add middleware after function registration")

        key = middleware.tag or None
        self._middleware.setdefault(key, []).append(middleware)
        self._middleware[key].sort(key=lambda m: -m.weight)

    def request(self, request: 'APIRequest') -> None:
        if request.function not in self._functions:
            raise KeyError(f"Function {request.function} not found")

            # Collect relevant middleware
        relevant_middleware = self._middleware[None].copy()
        function_tags = self._functions[request.function].tags or []
        for tag in function_tags:
            relevant_middleware.extend(self._middleware.get(tag, []))

        # Process request middleware
        current_request = request
        for mw in sorted(relevant_middleware,
                         key=lambda m: m.weight, reverse=True):
            if mw.m_type == MiddlewareType.Request:
                if result := mw.func(current_request):
                    current_request = result

        # Execute function
        func = self._functions[request.function].func
        response_data = func(**current_request.args)

        # Process response middleware
        current_response = response_data
        for mw in sorted(relevant_middleware,
                         key=lambda m: m.weight, reverse=True):
            if mw.m_type == MiddlewareType.Response:
                if result := mw.func(current_response):
                    current_response = result

        request.response = current_response

    def function(self, name: str, tags: Optional[List[str]] = None):

        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            self._functions_registered = True
            self._functions[name] = ModuleFunction(wrapper, tags)
            return wrapper

        return decorator


class APIRequest:

    def __init__(self, data: Dict[str, Any]):
        self._validate(data)
        self.module_name = data['module']
        self.function = data['function']
        self.args = data.get('args', {})
        self.response: Optional[APIResponse] = None

    @staticmethod
    def _validate(data: Dict[str, Any]):
        """Validate request structure"""
        required = {'module', 'function'}
        if not required.issubset(data.keys()):
            raise ValueError("Invalid request structure")


@dataclass
class APIError(Exception):
    code: int = 0
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message}


@dataclass
class APIResponse:
    data: Union[Dict, List] = field(default_factory=dict)
    error: APIError = field(default_factory=APIError)

    @property
    def formatted(self) -> Dict[str, Any]:
        return {
            "data": self.data,
            "error": self.error.to_dict()
        }


class EnhancedJSONEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o, APIError):
            return o.to_dict()
        if isinstance(o, (APIResponse, Module, Middleware)):
            return vars(o)
        return super().default(o)


class App(Flask):
    _instance: ClassVar[Optional['App']] = None
    _initialized: bool = False

    def __init__(self, name: str = 'lazy_flask', endpoint: str = '/query'):
        if not self._initialized:
            super().__init__(name)
            self.modules: Dict[str, Module] = {}
            self.add_url_rule(endpoint, 'api', self.handle_request, methods=['POST'])
            self.json_encoder = EnhancedJSONEncoder
            self._initialized = True

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register_module(self, module: Module) -> None:
        if module.name in self.modules:
            raise ValueError(f"Module {module.name} already registered")
        self.modules[module.name] = module

    def handle_request(self) -> FlaskResponse:
        try:
            request_data = flask_request.get_json()
            request = APIRequest(request_data)

            if request.module_name not in self.modules:
                raise KeyError(f"Module {request.module_name} not found")

            module = self.modules[request.module_name]
            module.request(request)

            return FlaskResponse(
                response=json.dumps(request.response.formatted, cls=self.json_encoder),
                status=200,
                mimetype='application/json'
            )
        except APIError as e:
            return FlaskResponse(
                response=json.dumps(APIResponse(error=e).formatted),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            error = APIError(code=500, message=str(e))
            return FlaskResponse(
                response=json.dumps(APIResponse(error=error).formatted),
                status=500,
                mimetype='application/json'
            )
