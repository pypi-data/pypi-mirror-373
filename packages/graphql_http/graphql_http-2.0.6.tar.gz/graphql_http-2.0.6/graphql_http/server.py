import copy
import json
import os
from json import JSONDecodeError
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type, Union
from logging import getLogger

import jwt
import uvicorn

from graphql import GraphQLError, ExecutionResult
from graphql.execution.execute import ExecutionContext
from graphql.type.schema import GraphQLSchema
from jwt import InvalidTokenError, PyJWKClient
from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.middleware import Middleware as StarletteMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from starlette.routing import Route
from starlette.testclient import TestClient

from graphql_http.helpers import (
    HttpQueryError,
    encode_execution_results,
    json_encode,
    load_json_body,
    run_http_query,
)

# Optional import for GraphQL API integration
try:
    from graphql_api.context import GraphQLContext
except ImportError:
    GraphQLContext = None  # type: ignore

logger = getLogger(__name__)
# Constants
GRAPHIQL_DIR = os.path.join(os.path.dirname(__file__), "graphiql")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000


class GraphQLHTTP:
    """GraphQL HTTP server for serving GraphQL schemas over HTTP.

    This class provides a complete HTTP server for GraphQL APIs with support for:
    - GraphiQL interface for development
    - JWT authentication with JWKS
    - CORS configuration
    - Health check endpoints
    - Custom middleware and context
    - Error handling and formatting
    """
    @classmethod
    def from_api(cls, api, root_value: Any = None, **kwargs) -> "GraphQLHTTP":
        try:
            from graphql_api import GraphQLAPI
            from graphql_api.context import GraphQLContext

        except ImportError:
            raise ImportError("GraphQLAPI is not installed.")

        graphql_api: GraphQLAPI = api

        executor = graphql_api.executor(root_value=root_value)

        schema: GraphQLSchema = executor.schema
        meta = executor.meta
        root_value = executor.root_value

        middleware = executor.middleware
        context = GraphQLContext(schema=schema, meta=meta, executor=executor)

        return GraphQLHTTP(
            schema=schema,
            root_value=root_value,
            middleware=middleware,
            context_value=context,
            execution_context_class=executor.execution_context_class,
            **kwargs,
        )

    def __init__(
        self,
        schema: GraphQLSchema,
        root_value: Any = None,
        middleware: Optional[List[Callable[[Callable, Any], Any]]] = None,
        context_value: Any = None,
        serve_graphiql: bool = True,
        graphiql_default_query: Optional[str] = None,
        allow_cors: bool = False,
        health_path: Optional[str] = None,
        execution_context_class: Optional[Type[ExecutionContext]] = None,
        auth_jwks_uri: Optional[str] = None,
        auth_issuer: Optional[str] = None,
        auth_audience: Optional[str] = None,
        auth_enabled: bool = False,
        auth_bypass_during_introspection: bool = True,
    ) -> None:
        """Initialize GraphQL HTTP server.

        Args:
            schema: GraphQL schema to serve
            root_value: Root value passed to resolvers
            middleware: List of middleware functions for field resolution
            context_value: Context value passed to resolvers
            serve_graphiql: Whether to serve GraphiQL interface
            graphiql_default_query: Default query for GraphiQL interface
            allow_cors: Whether to enable CORS middleware
            health_path: Path for health check endpoint (e.g., '/health')
            execution_context_class: Custom execution context class
            auth_jwks_uri: JWKS URI for JWT token validation
            auth_issuer: Expected JWT issuer
            auth_audience: Expected JWT audience
            auth_enabled: Whether to enable JWT authentication
            auth_bypass_during_introspection: Whether auth is required for introspection only queries

        Raises:
            ValueError: If invalid configuration is provided
            ImportError: If required dependencies are missing
        """
        self._validate_config(
            schema=schema,
            auth_enabled=auth_enabled,
            auth_jwks_uri=auth_jwks_uri,
            auth_issuer=auth_issuer,
            auth_audience=auth_audience,
            health_path=health_path,
        )
        if middleware is None:
            middleware = []

        self.schema = schema
        self.root_value = root_value
        self.middleware = middleware
        self.context_value = context_value
        self.serve_graphiql = serve_graphiql
        self.graphiql_default_query = graphiql_default_query
        self.allow_cors = allow_cors
        self.health_path = health_path
        self.execution_context_class = execution_context_class
        self.auth_jwks_uri = auth_jwks_uri
        self.auth_issuer = auth_issuer
        self.auth_audience = auth_audience
        self.auth_enabled = auth_enabled
        self.auth_bypass_during_introspection = auth_bypass_during_introspection

        if auth_jwks_uri:
            self.jwks_client = PyJWKClient(auth_jwks_uri)
        else:
            self.jwks_client = None

        routes = [
            Route("/graphql", self.dispatch,
                  methods=["GET", "POST", "OPTIONS"]),
            Route("/", self.dispatch, methods=["GET", "POST", "OPTIONS"]),
        ]
        if self.health_path:
            routes.insert(
                0, Route(self.health_path, self.health_check, methods=["GET"])
            )

        middleware_stack: List[StarletteMiddleware] = []
        self._setup_cors_middleware(middleware_stack)

        self.app = Starlette(routes=routes, middleware=middleware_stack)

    def _validate_config(
        self,
        schema: GraphQLSchema,
        auth_enabled: bool,
        auth_jwks_uri: Optional[str],
        auth_issuer: Optional[str],
        auth_audience: Optional[str],
        health_path: Optional[str],
    ) -> None:
        """Validate server configuration.

        Args:
            schema: GraphQL schema to validate
            auth_enabled: Whether authentication is enabled
            auth_jwks_uri: JWKS URI for JWT validation
            auth_issuer: JWT issuer
            auth_audience: JWT audience
            health_path: Health check path

        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(schema, GraphQLSchema):
            raise ValueError(f"Expected GraphQLSchema, got {type(schema)}")

        if auth_enabled:
            if not auth_jwks_uri:
                raise ValueError(
                    "auth_jwks_uri is required when auth_enabled=True")
            if not auth_issuer:
                raise ValueError(
                    "auth_issuer is required when auth_enabled=True")
            if not auth_audience:
                raise ValueError(
                    "auth_audience is required when auth_enabled=True")

        if health_path is not None:
            if not isinstance(health_path, str):
                raise ValueError("health_path must be a string")
            if not health_path.startswith('/'):
                raise ValueError("health_path must start with '/'")

    def _setup_cors_middleware(
        self, middleware_stack: List[StarletteMiddleware]
    ) -> None:
        """Setup CORS middleware if enabled.

        Args:
            middleware_stack: List to append CORS middleware to
        """
        if not self.allow_cors:
            return

        allow_headers_list = ["Content-Type"]
        if self.auth_enabled:
            allow_headers_list.append("Authorization")

        allow_origin_regex = None
        allow_credentials = False
        allow_origins = ()

        if self.auth_enabled:
            allow_origin_regex = r"https?://.*"  # Allows any http/https
            allow_credentials = True
        else:
            allow_origins = ["*"]

        middleware_stack.append(StarletteMiddleware(
            CORSMiddleware,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=allow_headers_list,
            allow_origin_regex=allow_origin_regex,
            allow_credentials=allow_credentials,
            allow_origins=allow_origins
        ))

    def _handle_health_check(self, request: Request) -> Optional[Response]:
        """Handle health check requests.

        Args:
            request: HTTP request

        Returns:
            Response if this is a health check request, None otherwise
        """
        if self.health_path and request.url.path == self.health_path:
            return Response("OK")
        return None

    def _handle_graphiql(self, request: Request) -> Optional[Response]:
        """Handle GraphiQL interface requests.

        Args:
            request: HTTP request

        Returns:
            HTMLResponse with GraphiQL if appropriate, None otherwise
        """
        if request.method.lower() != "get" or not self.should_serve_graphiql(request):
            return None

        graphiql_path = os.path.join(GRAPHIQL_DIR, "index.html")

        default_query = ''
        if self.graphiql_default_query:
            if isinstance(self.graphiql_default_query, str):
                default_query = json.dumps(self.graphiql_default_query)
                if default_query.startswith('"'):
                    default_query = default_query[1:-1]

        with open(graphiql_path, "r") as f:
            html_content = f.read()
        html_content = html_content.replace("DEFAULT_QUERY", default_query)

        return HTMLResponse(html_content)

    def _handle_options(self, request: Request) -> Optional[Response]:
        """Handle CORS preflight OPTIONS requests.

        Args:
            request: HTTP request

        Returns:
            Response for OPTIONS request, None if not OPTIONS
        """
        if request.method.lower() != "options":
            return None

        response_headers = {}
        if self.allow_cors:
            allow_h = ["Content-Type"]
            if self.auth_enabled:
                allow_h.append("Authorization")

            response_headers = {
                "Access-Control-Allow-Headers": ", ".join(allow_h),
                "Access-Control-Allow-Methods": "GET, POST",
            }

            origin = request.headers.get(
                "Origin") or request.headers.get("origin")
            if self.auth_enabled:
                # When auth is enabled, be more restrictive
                response_headers["Access-Control-Allow-Credentials"] = "true"
                if origin:
                    response_headers["Access-Control-Allow-Origin"] = origin
            else:
                # When auth is disabled, allow all origins
                response_headers["Access-Control-Allow-Origin"] = "*"

        return PlainTextResponse("OK", headers=response_headers)

    def _check_introspection_only(self, data: Union[Dict, List]) -> bool:
        """Check if request contains only introspection queries using GraphQL's built-in validation.

        This approach uses GraphQL's execution preparation to determine if a query
        is introspection-only by checking what fields would actually be resolved.

        Args:
            data: Request data (dict for single query, list for batched queries)

        Returns:
            True if all queries are introspection-only
        """
        try:
            from graphql import parse, validate
            from graphql.type.introspection import is_introspection_type
            # Try to import execution context functions, fall back gracefully if not available
            try:
                from graphql.execution import build_execution_context
                from graphql.execution.collect_fields import collect_fields
                has_execution_context = True
            except ImportError:
                has_execution_context = False
        except ImportError:
            # Fallback to AST-based check if advanced GraphQL features not available
            return self._check_introspection_only_ast(data)

        # Handle batched queries
        if isinstance(data, list):
            return all(self._check_introspection_only(item) for item in data)

        if not isinstance(data, dict) or 'query' not in data:
            return False

        query_str = data.get('query', '')
        if not query_str or not isinstance(query_str, str):
            return False

        # Pre-validation security checks
        query_stripped = query_str.strip()
        if not query_stripped:
            return False

        # Basic syntax validation - ensure query looks structurally sound
        if query_stripped.count('{') != query_stripped.count('}'):
            return False
        if query_stripped.count('(') != query_stripped.count(')'):
            return False

        try:
            # Parse and validate the query - this will catch syntax errors
            document = parse(query_str)
            validation_errors = validate(self.schema, document)

            # If query has validation errors, it's not a valid introspection query
            if validation_errors:
                return False

            # If execution context is not available, fall back to AST method
            if not has_execution_context:
                return self._check_introspection_only_ast(data)

            # Additional security checks before execution analysis
            # Check if document contains only query operations (no mutations/subscriptions)
            for definition in document.definitions:
                if hasattr(definition, 'operation'):
                    # Only allow query operations for introspection bypass
                    if definition.operation != 'query':
                        return False

            # Build execution context to analyze what fields would be resolved
            try:
                context_value = {}
                variable_values = data.get('variables') or {}
                operation_name = data.get('operationName')

                exe_context = build_execution_context(
                    self.schema,
                    document,
                    context_value=context_value,
                    variable_values=variable_values,
                    operation_name=operation_name
                )

                # If execution context building fails, be conservative
                if isinstance(exe_context, list):  # List of GraphQLError
                    return False

                # Get the operation
                operation = exe_context.operation
                if not operation or not operation.selection_set:
                    return False

                # Collect the fields that would be executed
                fields = collect_fields(
                    exe_context,
                    exe_context.schema.query_type,
                    operation.selection_set,
                    set(),
                    set()
                )

                # Strict validation: only allow official introspection fields
                official_introspection_fields = {'__schema', '__type', '__typename'}

                for field_name in fields.keys():
                    # Must start with __ (introspection convention)
                    if not field_name.startswith('__'):
                        return False

                    # Must be an official introspection field
                    if field_name not in official_introspection_fields:
                        return False

                # Double-check by examining the field types being accessed
                query_type = self.schema.query_type
                for field_name in fields.keys():
                    field_def = query_type.fields.get(field_name)
                    if field_def:
                        field_type = field_def.type
                        # Unwrap non-null and list types to get the base type
                        while hasattr(field_type, 'of_type'):
                            field_type = field_type.of_type

                        # Check if the field type is an introspection type
                        if not is_introspection_type(field_type):
                            return False
                    else:
                        # Field doesn't exist in schema - should not happen with validation
                        return False

                return True

            except Exception:
                # If execution context fails, fall back to AST method
                return self._check_introspection_only_ast(data)

        except Exception:
            # If parsing fails, it's not a valid query - BLOCK IT
            # Parse errors indicate malformed GraphQL which should never bypass auth
            return False

    def _check_introspection_only_ast(self, data: Union[Dict, List]) -> bool:
        """AST-based fallback for introspection detection.

        This is the previous implementation as a fallback when execution context
        analysis is not available.
        """
        try:
            from graphql import parse, FieldNode, visit, Visitor
        except ImportError:
            # Final fallback to string-based check
            return self._check_introspection_only_fallback(data)

        # Handle batched queries
        if isinstance(data, list):
            return all(self._check_introspection_only_ast(item) for item in data)

        if not isinstance(data, dict) or 'query' not in data:
            return False

        query_str = data.get('query', '')
        if not query_str or not isinstance(query_str, str):
            return False

        try:
            # Parse the GraphQL query into an AST
            document = parse(query_str)

            # Extract only root-level field names from the query
            root_field_names = set()

            class RootFieldCollector(Visitor):
                def __init__(self):
                    super().__init__()
                    self.depth = 0
                    self.in_operation = False

                def enter_operation_definition(self, node, *_):
                    # We're now inside an operation (query/mutation/subscription)
                    self.in_operation = True

                def leave_operation_definition(self, node, *_):
                    # Leaving the operation
                    self.in_operation = False

                def enter_fragment_definition(self, node, *_):
                    # Skip fragment definitions - they're not part of the actual query execution
                    return False

                def enter_selection_set(self, node, *_):
                    if self.in_operation:
                        self.depth += 1

                def leave_selection_set(self, node, *_):
                    if self.in_operation:
                        self.depth -= 1

                def enter_field(self, node: FieldNode, *_):
                    # Only collect fields at depth 1 within actual operations
                    if self.in_operation and self.depth == 1 and hasattr(node, 'name') and hasattr(node.name, 'value'):
                        root_field_names.add(node.name.value)

            visit(document, RootFieldCollector())

            # Check if all root fields are introspection fields
            introspection_fields = {'__schema', '__type', '__typename'}

            # If no fields found, it's not a valid query
            if not root_field_names:
                return False

            # All root fields must be introspection fields
            return root_field_names.issubset(introspection_fields)

        except Exception:
            # If AST parsing fails, it's not a valid query - BLOCK IT
            return False

    def _check_introspection_only_fallback(self, data: Union[Dict, List]) -> bool:
        """Fallback string-based introspection check for when GraphQL parsing fails.

        Args:
            data: Request data

        Returns:
            True if request appears to be introspection-only (conservative check)
        """
        # Handle batched queries
        if isinstance(data, list):
            return all(self._check_introspection_only_fallback(item) for item in data)

        if not isinstance(data, dict) or 'query' not in data:
            return False

        query_str = data.get('query', '')
        if not query_str or not isinstance(query_str, str):
            return False

        query_lower = query_str.lower()

        # Check for introspection fields
        introspection_fields = ['__schema', '__type', '__typename']
        has_introspection = any(field in query_lower for field in introspection_fields)

        if not has_introspection:
            return False

        # Conservative approach: check for common non-introspection patterns
        # Remove comments and strings to avoid false positives
        import re
        clean_query = re.sub(r'#.*', '', query_str)  # Remove comments
        clean_query = re.sub(r'"[^"]*"', '', clean_query)  # Remove string literals
        clean_query = re.sub(r"'[^']*'", '', clean_query)  # Remove string literals
        clean_query = clean_query.lower()

        # Look for non-introspection field patterns in clean query
        # Use word boundaries to avoid matching substrings
        suspicious_patterns = [
            r'\b(query|mutation|subscription)\s+\w+',  # Named operations
            r'\{[^}]*[a-z_][a-z0-9_]*\s*[({]',  # Regular field selections
        ]

        # If we find suspicious patterns, be conservative and require auth
        for pattern in suspicious_patterns:
            if re.search(pattern, clean_query):
                # Double-check it's not just introspection
                remaining = clean_query
                for intro_field in introspection_fields:
                    remaining = remaining.replace(intro_field, '')

                # If there's still substantial content, likely has regular fields
                if len(re.findall(r'\w+', remaining)) > 3:  # Threshold for field names
                    return False

        return True

    def _authenticate_request(self, request: Request) -> Optional[Response]:
        """Authenticate JWT token from request.

        Args:
            request: HTTP request

        Returns:
            Error response if authentication fails, None if successful
        """
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise InvalidTokenError(
                    "Unauthorized: Authorization header is missing or not Bearer"
                )

            if not self.jwks_client:
                return self.error_response(
                    ValueError("JWKS client not configured"), status=500
                )

            token = auth_header.replace("Bearer ", "")
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            jwt.decode(
                token,
                audience=self.auth_audience,
                issuer=self.auth_issuer,
                key=signing_key.key,
                algorithms=["RS256"],
                verify=True,
            )
            return None  # Success
        except InvalidTokenError as e:
            return self.error_response(e, status=401)
        except Exception as e:
            # For other exceptions (like JWKS key retrieval failures),
            # preserve the message
            return self.error_response(e, status=401)

    def _prepare_context(self, request: Request) -> Any:
        """Prepare context value for GraphQL execution.

        Args:
            request: HTTP request

        Returns:
            Context value for GraphQL execution
        """
        context_value = copy.copy(self.context_value)

        if GraphQLContext and isinstance(context_value, GraphQLContext):
            context_value.meta["http_request"] = request

        return context_value

    @staticmethod
    def format_error(error: GraphQLError) -> Dict[str, Any]:
        error_dict: Dict[str, Any] = error.formatted  # type: ignore
        return error_dict

    encode = staticmethod(json_encode)

    async def dispatch(self, request: Request) -> Response:
        """Handle HTTP requests and route them appropriately.

        Args:
            request: HTTP request

        Returns:
            HTTP response
        """
        try:
            # Parse request data
            request_method = request.method.lower()
            data = await self.parse_body(request=request)

            # Handle health check requests
            health_response = self._handle_health_check(request)
            if health_response:
                return health_response

            # Handle GraphiQL interface
            graphiql_response = self._handle_graphiql(request)
            if graphiql_response:
                return graphiql_response

            # Handle CORS preflight requests
            options_response = self._handle_options(request)
            if options_response:
                return options_response

            # Handle authentication
            allow_only_introspection = False
            if self.auth_enabled:
                auth_error = self._authenticate_request(request)
                if auth_error:
                    if self.auth_bypass_during_introspection and self._check_introspection_only(data):
                        logger.info("Authentication bypassed as introspection only query.")
                    else:
                        return auth_error

            # Prepare context for GraphQL execution
            context_value = self._prepare_context(request)

            query_data: Dict[str, Any] = {}

            for key, value in request.query_params.items():
                query_data[key] = value

            execution_results, all_params = await run_in_threadpool(
                run_http_query,
                self.schema,
                request_method,
                data,
                allow_only_introspection=allow_only_introspection,
                query_data=query_data,
                root_value=self.root_value,
                middleware=self.middleware,
                context_value=context_value,
                execution_context_class=self.execution_context_class,
            )

            results = []
            for execution_result in execution_results:
                if isinstance(execution_result, Awaitable):
                    awaited_execution_result: ExecutionResult = await execution_result
                else:
                    awaited_execution_result = execution_result or ExecutionResult(
                        data=None, errors=[]
                    )

                results.append(awaited_execution_result)

            result, status_code = encode_execution_results(
                results, is_batch=isinstance(data, list), encode=lambda x: x
            )

            return JSONResponse(
                result,
                status_code=status_code,
            )

        except HttpQueryError as e:
            return self.error_response(e, status=getattr(e, "status_code", None))

    async def health_check(self, request: Request) -> Response:
        return PlainTextResponse("OK")

    @staticmethod
    def error_response(e, status=None):
        if status is None:
            if (
                isinstance(e, GraphQLError)
                and e.extensions
                and "statusCode" in e.extensions
            ):
                status = e.extensions["statusCode"]
            elif hasattr(e, "status_code"):
                status = e.status_code  # type: ignore
            else:
                status = 500

        if isinstance(e, HttpQueryError):
            error_message = str(e.message)
        elif isinstance(e, (jwt.exceptions.InvalidTokenError, ValueError, Exception)):
            error_message = str(e)
        else:
            error_message = "Internal Server Error"

        return JSONResponse(
            {"errors": [{"message": error_message}]}, status_code=status
        )

    async def parse_body(self, request: Request):
        content_type = request.headers.get("Content-Type", "")

        if content_type == "application/graphql":
            body_bytes = await request.body()
            return {"query": body_bytes.decode("utf8")}

        elif content_type == "application/json":
            try:
                return await request.json()
            except JSONDecodeError as e:
                raise HttpQueryError(400, f"Unable to parse JSON body: {e}")

        elif (content_type.startswith("application/x-www-form-urlencoded")
              or content_type.startswith("multipart/form-data")):
            form_data = await request.form()
            return {k: v for k, v in form_data.items()}

        body_bytes = await request.body()
        if body_bytes:
            try:
                return load_json_body(body_bytes.decode("utf8"))
            except (HttpQueryError, UnicodeDecodeError):
                return {"query": body_bytes.decode("utf8")}

        return {}

    def should_serve_graphiql(self, request: Request):
        if not self.serve_graphiql or (
            self.health_path and request.url.path == self.health_path
        ):
            return False
        if "raw" in request.query_params:
            return False
        return self.request_wants_html(request)

    def request_wants_html(self, request: Request):
        accept_header = request.headers.get("accept", "").lower()
        # Serve HTML if "text/html" is accepted and "application/json" is not,
        # or if "text/html" is more preferred than "application/json".
        # A simple check: if "text/html" is present and "application/json" is not,
        # or if "text/html" appears before "application/json".
        # For */*, we should not serve HTML by default.
        if "text/html" in accept_header:
            if "application/json" in accept_header:
                # If both are present, serve HTML only if text/html comes first
                # (this is a simplification of q-factor parsing)
                return accept_header.find("text/html") < accept_header.find(
                    "application/json"
                )
            return True  # Only text/html is present
        return False  # text/html is not present, or only */*

    def client(self) -> TestClient:
        """Get a test client for the GraphQL server.

        Returns:
            Starlette TestClient instance for testing
        """
        return TestClient(self.app)

    def run(
        self, host: Optional[str] = None, port: Optional[int] = None, **kwargs
    ) -> None:
        """Run the GraphQL HTTP server.

        Args:
            host: Host to bind to (default: 127.0.0.1)
            port: Port to bind to (default: 5000)
            **kwargs: Additional arguments passed to uvicorn.run()
        """
        hostname = host or DEFAULT_HOST
        port_num = port or DEFAULT_PORT

        print(
            f"GraphQL server running at http://{hostname}:{port_num}/graphql")
        if self.serve_graphiql:
            print(f"GraphiQL interface: http://{hostname}:{port_num}/graphql")
        if self.health_path:
            print(
                f"Health check: http://{hostname}:{port_num}{self.health_path}")

        uvicorn.run(self.app, host=hostname, port=port_num, **kwargs)
