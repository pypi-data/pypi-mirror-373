import asyncio
import signal
from asyncio import CancelledError
from contextlib import asynccontextmanager
from types import FrameType
from typing import Any, Callable, Coroutine, Type

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine
from typing_extensions import TypeVar

from planar.ai import Agent
from planar.config import Environment, PlanarConfig, load_environment_aware_config
from planar.db import DatabaseManager
from planar.files.storage.base import Storage
from planar.files.storage.config import create_from_config
from planar.files.storage.context import set_storage
from planar.logging import get_logger
from planar.modeling.orm import PlanarBaseEntity
from planar.object_registry import ObjectRegistry
from planar.routers import (
    create_files_router,
    create_human_task_routes,
    create_info_router,
    create_workflow_router,
)
from planar.routers.agents_router import create_agent_router
from planar.routers.entity_router import create_entities_router
from planar.routers.object_config_router import create_object_config_router
from planar.routers.rule import create_rule_router
from planar.rules.decorator import RULE_REGISTRY
from planar.security.auth_middleware import AuthMiddleware
from planar.security.authorization import PolicyService, policy_service_context
from planar.session import config_var, session_context
from planar.sse.proxy import SSEProxy
from planar.workflows import (
    WorkflowNotification,
    WorkflowNotificationCallback,
    WorkflowOrchestrator,
    WorkflowWrapper,
    orchestrator_context,
    workflow_notification_context,
)
from planar.workflows.tracing import LoggingTracer, Tracer, tracer_context

T = TypeVar("T", bound=BaseModel)
U = TypeVar("U", bound=BaseModel)

logger = get_logger(__name__)

PLANAR_BASE_PATH = "/planar"


class PlanarApp:
    def __init__(
        self,
        *,
        config: PlanarConfig | None = None,
        title: str | None = None,
        description: str | None = None,
        on_startup: Callable[[AsyncEngine], Coroutine[Any, Any, None]] | None = None,
        on_workflow_notification: WorkflowNotificationCallback | None = None,
    ):
        # If no config provided, load from environment
        self.config = config or load_environment_aware_config()
        self.config.configure_logging()

        self.tracer: Tracer | None = None
        self.storage: Storage | None = None
        self.sse_proxy = SSEProxy(self.config)
        self.on_startup = on_startup
        self.on_workflow_notification = on_workflow_notification
        self.fastapi = FastAPI(
            title=title or "Planar API",
            description=description or "Planar API",
            lifespan=self._lifespan,
        )
        self.policy_service: PolicyService | None = None

        self.db_manager = DatabaseManager(db_url=self.config.connection_url())

        if self.config.storage:
            self.storage = create_from_config(self.config.storage)

        # Used to track what objects have been registered with the app instance
        self._object_registry = ObjectRegistry()

        setup_file_storage_middleware(self)
        setup_sqlalchemy_session_middleware(self)
        setup_orchestrator_middleware(self)
        setup_workflow_notification_middleware(self)
        setup_tracer_middleware(self)
        setup_auth_middleware(self)
        setup_http_exception_handler(self)
        setup_authorization_policy_service(self)

        self.router_v1 = APIRouter(
            prefix=f"{PLANAR_BASE_PATH}/v1", tags=["Planar API v1"]
        )

        self.router_v1.include_router(
            create_entities_router(self._object_registry),
            prefix="/entities",
        )

        self.router_v1.include_router(
            create_workflow_router(self._object_registry),
            prefix="/workflows",
        )
        self.router_v1.include_router(
            create_rule_router(self._object_registry),
            prefix="/rules",
        )
        self.router_v1.include_router(
            create_agent_router(self._object_registry),
            prefix="/agents",
        )
        self.router_v1.include_router(
            create_object_config_router(self._object_registry),
            prefix="/object-configurations",
        )
        self.router_v1.include_router(
            create_human_task_routes(),
            prefix="/human-tasks",
        )

        self.router_v1.include_router(
            create_info_router(
                title=title or "Planar API", description=description or "Planar API"
            ),
            prefix="",
        )

        if self.sse_proxy.hub_url:
            self.router_v1.include_router(
                self.sse_proxy.router,
                prefix="/sse",
            )

        if self.storage:
            self.router_v1.include_router(
                create_files_router(),
                prefix="/file",
            )

        self.router_v1.add_api_route(
            "/health", lambda: {"status": "ok"}, methods=["GET"]
        )

        self.fastapi.include_router(self.router_v1)

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            # setup cors middleware as late as possible ensuring
            # that it's the first middleware to be called in the middleware stack
            setup_cors_middleware(self)
        try:
            await self.fastapi(scope, receive, send)
        except CancelledError as e:
            logger.info(f"lifespan cancelled: {e}")
            raise e

    def start_sse(self):
        if not self.sse_proxy.hub_url:
            return

        def on_workflow_notification(notification: WorkflowNotification):
            self.sse_proxy.push(
                f"{notification.kind.value}:{notification.workflow_id}",
                notification.data.model_dump(mode="json"),
            )

        if self.on_workflow_notification:
            raise ValueError(
                "on_workflow_notification should not be set when enabling SSE forwarding"
            )

        self.on_workflow_notification = on_workflow_notification
        self.sse_proxy.start()

    async def stop_sse(self):
        if self.sse_proxy.hub_url:
            await self.sse_proxy.stop()

    async def graceful_shutdown(self) -> None:
        """
        Called as soon as the process receives SIGINT/SIGTERM but
        *before* Uvicorn starts waiting for open connections to finish.

        At the moment we only need to stop the SSE proxy so that
        long-lived EventSource connections close quickly, but more
        early-shutdown logic can be added here in future.
        """
        await self.stop_sse()

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        # We manually capture SIGINT/SIGTERM to trigger our own graceful shutdown.
        # This is necessary because long-lived connections, such as from the SSE
        # proxy, can cause uvicorn's default graceful shutdown to hang, preventing
        # the lifespan shutdown logic (after the yield) from ever being reached.
        # Our handler starts the shutdown of these components and then chains to the
        # original uvicorn handler to allow it to proceed with its own shutdown.
        original_handlers = {
            signal.SIGINT: signal.getsignal(signal.SIGINT),
            signal.SIGTERM: signal.getsignal(signal.SIGTERM),
        }

        def terminate_now(signum: int, frame: FrameType | None = None):
            asyncio.create_task(self.graceful_shutdown())
            handler = original_handlers.get(signal.Signals(signum))
            if callable(handler):
                handler(signum, frame)

        signal.signal(signal.SIGINT, terminate_now)
        signal.signal(signal.SIGTERM, terminate_now)

        # Begin the normal lifespan logic
        self.db_manager.connect()
        await self.db_manager.migrate(
            self.config.use_alembic if self.config.use_alembic is not None else True
        )

        self.orchestrator = WorkflowOrchestrator(self.db_manager.get_engine())
        config_tok = config_var.set(self.config)

        self.start_sse()

        if self.tracer is None:
            self.tracer = LoggingTracer()

        if self.storage:
            set_storage(self.storage)

        async with tracer_context(self.tracer):
            self.orchestrator_task = asyncio.create_task(
                self.orchestrator.run(
                    notification_callback=self.on_workflow_notification
                )
            )

        if self.on_startup:
            await self.on_startup(self.db_manager.get_engine())

        yield
        # stop workflow orchestrator
        self.orchestrator_task.cancel()
        try:
            await self.orchestrator_task
        except asyncio.CancelledError:
            pass
        finally:
            # Reset the config in the context
            config_var.reset(config_tok)

        await self.db_manager.disconnect()

        if self.storage:
            await self.storage.close()

        logger.info("stopping sse")
        await self.stop_sse()
        logger.info("lifespan completed")

    def register_agent(self, agent: Agent) -> "PlanarApp":
        self._object_registry.register(agent)
        return self

    def register_rule(
        self, rule_fn: Callable[[T], Coroutine[Any, Any, U]]
    ) -> "PlanarApp":
        rule = RULE_REGISTRY.get(rule_fn.__name__)

        if not rule:
            raise ValueError(f"rule {rule_fn.__name__} not found")

        self._object_registry.register(rule)

        return self

    def register_entity(
        self,
        entity_cls: Type[PlanarBaseEntity],
    ) -> "PlanarApp":
        """
        Register an entity. Uses a fluent interface pattern.

        Args:
            entity_cls: The Planar Entity to create add to the object registry

        Returns:
            self: Returns the app instance for method chaining
        """
        self._object_registry.register(entity_cls)

        return self

    def register_workflow(self, wrapper: WorkflowWrapper) -> "PlanarApp":
        """
        Register routes for starting a workflow and checking its status.

        Args:
            wrapper: The ``WorkflowWrapper`` containing the workflow definition.

        Returns:
            self: Returns the service instance for method chaining
        """
        self._object_registry.register(wrapper)
        return self

    def register_router(
        self,
        router: APIRouter,
        prefix: str | None = None,
        **kwargs,
    ):
        """
        Register a custom router. Uses a fluent interface pattern.
        Args:
            router: APIRouter instance to register
            path_prefix: The URL path prefix for all routes (e.g. '/suppliers')
        Returns:
            self: Returns the app instance for method chaining
        """
        # If router doesn't have tags, create one based on the first word in the route path
        if not getattr(router, "tags", None):
            # Try to derive tags from prefix if available
            if kwargs.get("tags", None) is None and prefix:
                # Extract the first segment of the path (without slashes) as the tag
                tag = prefix.strip("/").split("/")[0].title()

                if tag:
                    kwargs["tags"] = [tag]
            else:
                logger.warning(
                    "router being registered without tags. consider adding tags for better api documentation."
                )

        self.fastapi.include_router(router, prefix=prefix or "", **kwargs)

        return self

    @property
    def middleware(self):
        return self.fastapi.middleware

    async def run_standalone(self, func, *args, **kwargs):
        """
        Run a function in the context of a Planar application.

        This sets up all the necessary context variables and lifecycle components
        (database, orchestrator, etc.) and then runs the provided async function.

        Args:
            func: An async function to run
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function call
        """
        # Use the same lifespan context manager as the FastAPI app
        async with self._lifespan(self.fastapi):
            # Set up session and orchestrator contexts using the same context managers
            # that are used by the HTTP middlewares
            async with session_context(self.db_manager.get_engine()):
                async with orchestrator_context(self.orchestrator):
                    async with policy_service_context(self.policy_service):
                        # Run the function with all context properly set up
                        return await func(*args, **kwargs)


def setup_file_storage_middleware(app: PlanarApp):
    @app.middleware("http")
    async def file_storage_middleware(request: Request, call_next):
        if app.storage:
            set_storage(app.storage)
        return await call_next(request)

    return file_storage_middleware


def setup_sqlalchemy_session_middleware(app: PlanarApp):
    @app.middleware("http")
    async def session_middleware(request: Request, call_next):
        async with session_context(app.db_manager.get_engine()):
            response = await call_next(request)
        return response

    return session_middleware


def setup_orchestrator_middleware(app: PlanarApp):
    @app.middleware("http")
    async def orchestrator_middleware(request: Request, call_next):
        config_tok = config_var.set(app.config)

        async with orchestrator_context(app.orchestrator):
            response = await call_next(request)

        config_var.reset(config_tok)

        return response

    return orchestrator_middleware


def setup_workflow_notification_middleware(app: PlanarApp):
    # This middleware is used for handling endpoints that start workflows
    @app.middleware("http")
    async def workflow_notification_middleware(request: Request, call_next):
        if not app.on_workflow_notification:
            return await call_next(request)
        async with workflow_notification_context(app.on_workflow_notification):
            return await call_next(request)

    return workflow_notification_middleware


def setup_tracer_middleware(app: PlanarApp):
    @app.middleware("http")
    async def tracer_middleware(request: Request, call_next):
        if app.tracer:
            async with tracer_context(app.tracer):
                return await call_next(request)
        return await call_next(request)

    return tracer_middleware


def setup_http_exception_handler(app: PlanarApp):
    """
    This middleware is used to handle HTTP exceptions and return a JSON response
    with the appropriate status code and detail.

    This is useful for handling HTTP exceptions that are raised by the middleware
    stack. Middleware that uses app.middleware() to register itself already handles
    HTTP exceptions by default. The class based middleware (ie. JWTMiddleware and
    CORSMiddleware) do not handle HTTP exceptions by default.
    """

    @app.middleware("http")
    async def http_exception_handler(request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail} if e.detail else {},
                headers=e.headers,
            )


def setup_cors_middleware(app: PlanarApp):
    opts = {
        "allow_headers": app.config.security.cors.allow_headers,
        "allow_methods": app.config.security.cors.allow_methods,
        "allow_credentials": app.config.security.cors.allow_credentials,
    }

    if isinstance(app.config.security.cors.allow_origins, str):
        opts["allow_origin_regex"] = app.config.security.cors.allow_origins
    else:
        opts["allow_origins"] = app.config.security.cors.allow_origins

    app.fastapi.add_middleware(
        CORSMiddleware,
        **opts,
    )


def setup_auth_middleware(app: PlanarApp):
    if (
        app.config.security
        and app.config.security.jwt
        and app.config.security.jwt.client_id
        and app.config.security.jwt.org_id
    ):
        client_id = app.config.security.jwt.client_id
        org_id = app.config.security.jwt.org_id
        additional_exclusion_paths = app.config.security.jwt.additional_exclusion_paths
        app.fastapi.add_middleware(
            AuthMiddleware,  # type: ignore
            client_id,
            org_id,
            additional_exclusion_paths,
            service_token=app.config.security.service_token.token
            if app.config.security.service_token
            and app.config.security.service_token.token
            else None,
        )
        logger.info(
            "Auth middleware enabled",
            client_id=client_id,
            org_id=org_id,
            additional_exclusion_paths=additional_exclusion_paths,
        )
    elif app.config.environment == Environment.PROD:
        raise ValueError(
            "Auth middleware is required in production. Please set the JWT config and optionally service token config."
        )
    else:
        logger.warning("Auth middleware disabled")


def setup_authorization_policy_service(app: PlanarApp):
    if (
        app.config.security
        and app.config.security.authz
        and app.config.security.authz.enabled
    ):
        app.policy_service = PolicyService(
            policy_file_path=app.config.security.authz.policy_file
            if app.config.security.authz.policy_file
            else None
        )
        logger.info(
            f"Authorization policy service enabled with policy file: {app.policy_service.policy_file_path}"
        )
    else:
        app.policy_service = None
        logger.warning("Authz service disabled")

    # Set up middleware to manage authorization service context
    @app.middleware("http")
    async def authz_service_middleware(request: Request, call_next):
        async with policy_service_context(app.policy_service):
            response = await call_next(request)
        return response
