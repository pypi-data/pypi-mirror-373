"""Tesseract Module for LogicLayer.

This module contains an implementation of the :class:`LogicLayerModule` class,
for use with a :class:`LogicLayer` instance.
"""

import dataclasses
import traceback
from pathlib import Path
from typing import Optional, Union

import logiclayer as ll
from fastapi import Depends, Header, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import ValidationError
from typing import Annotated

import tesseract_olap as olap
from tesseract_olap.backend import JoinStep
from tesseract_olap.common import AnyDict, Prim
from tesseract_olap.exceptions import TesseractError
from tesseract_olap.exceptions.query import NotAuthorized
from tesseract_olap.query import (
    DataMultiQuery,
    DataMultiRequest,
    DataQuery,
    DataRequest,
    MembersQuery,
    MembersRequest,
)
from tesseract_olap.schema import TesseractCube, TesseractSchema
from tesseract_olap.server import OlapServer

from .debug import debug_response
from .dependencies import auth_token, dataquery_params, membersquery_params
from .response import MembersResponseModel, ResponseFormat, data_response


class TesseractModule(ll.LogicLayerModule):
    """Tesseract OLAP server module for LogicLayer.

    It must be initialized with a :class:`logiclayer.OlapServer` instance, but
    can also be created directly with the schema path and the connection string
    using the helper method `TesseractModule.new(connection, schema)`.
    """

    server: OlapServer
    session_kwargs: dict[str, Prim]

    def __init__(
        self,
        server: OlapServer,
        *,
        chunk_limit: int = 50000,
        query_limit: int = 0,
        **kwargs,
    ):
        self.server = server
        self.session_kwargs = {
            "chunk_limit": max(0, chunk_limit),
            "query_limit": max(0, query_limit),
        }
        super().__init__(**kwargs)

    @classmethod
    def new(cls, connection: str, schema: Union[str, Path], cache: str = "", **kwargs):
        """Short method to create a new :class:`TesseractModule` instance.

        Uses the strings with the path to the schema file (or the schema content itself),
        and with the connection string to the backend.
        """
        server = OlapServer(backend=connection, schema=schema, cache=cache)
        return cls(server, **kwargs)

    @ll.healthcheck
    def healthcheck(self) -> bool:
        """Perform a healthcheck against the backend."""
        return self.server.ping()

    @ll.route("GET", "/")
    def module_status(self) -> ll.ModuleStatus:
        """Retrieve operational information about this instance of TesseractModule."""
        return ll.ModuleStatus(
            module=olap.__title__,
            version=olap.__version__,
            debug=self.debug,
            status="ok" if self.server.ping() else "error",
        )

    @ll.route("GET", "/cubes")
    def get_schema(
        self,
        locale: Optional[str] = None,
        show_all: Annotated[bool, Query(description="Show all elements including non-visible ones. When false (default), show only visible elements. When true, show all elements.")] = False,
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> TesseractSchema:
        """Return the public schema with all the available cubes."""
        roles = self.auth.get_roles(token)
        return TesseractSchema.from_entity(
            self.server.schema,
            roles=roles,
            locale=locale,
            show_all=show_all
        )

    @ll.route("GET", "/cubes/{cube_name}")
    def get_cube(
        self,
        cube_name: str,
        locale: Optional[str] = None,
        show_all: Annotated[bool, Query(description="Show all elements including non-visible ones. When false (default), show only visible elements. When true, show all elements.")] = False,
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> TesseractCube:
        """Return the public schema for the single specified cube."""
        roles = self.auth.get_roles(token)
        cube = self.server.schema.get_cube(cube_name)
        if not cube.is_authorized(roles):
            raise NotAuthorized(f"Cube({cube.name})", roles)
        locale = self.server.schema.default_locale if locale is None else locale
        return TesseractCube.from_entity(cube, locale=locale, show_all=show_all)

    @ll.route("GET", "/data", deprecated=True, response_class=RedirectResponse)
    def query_data_redirect(self, request: Request) -> str:
        """Redirect the request to the canonical endpoint in jsonrecords format."""
        return f"{request.url.path}.jsonrecords?{request.url.query}"

    @ll.route("GET", "/data.{extension}")
    def query_data(
        self,
        extension: ResponseFormat,
        params: DataRequest = Depends(dataquery_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ):
        """Execute a request for data from the backend server."""
        params.roles = self.auth.get_roles(token)
        query = DataQuery.from_request(self.server.schema, params)
        with self.server.session(**self.session_kwargs) as session:
            result = session.fetch_dataframe(query)
        return data_response(query, result, extension)

    @ll.route("POST", "/multiquery.{extension}")
    def multiquery_data(
        self,
        extension: ResponseFormat,
        params: DataMultiRequest,
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ):
        """Execute a request for joining data from the server."""
        # Add role data to all params, overwrite possible user injections
        roles = self.auth.get_roles(token)
        for request in params.requests:
            request.roles = roles

        query = DataMultiQuery.from_requests(
            self.server.schema,
            params.requests,
            params.joins,
        )

        with self.server.session(**self.session_kwargs) as session:
            result = session.fetch_dataframe(query.initial)
            step = JoinStep.new(result)

            for query_right, join_params in query.join_with:
                result = session.fetch_dataframe(query_right)
                join_params.suffix = f"_{query_right.cube.name}"
                step = step.join_with(result, join_params)

        result = step.get_result(params.pagination)
        return data_response(query, result, extension)

    @ll.route(
        "GET",
        "/members.{extension}",
        deprecated=True,
        response_class=RedirectResponse,
    )
    def get_members_redirect(self, request: Request, extension: str):
        """Redirect the request to the canonical endpoint without extension."""
        path = request.url.path.replace(f"members.{extension}", "members")
        return f"{path}?{request.url.query}"

    @ll.route("GET", "/members", summary="Get level members")
    def get_members(
        self,
        params: MembersRequest = Depends(membersquery_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> MembersResponseModel:
        """Retrieve detailed information about a level and its members."""
        params.roles = self.auth.get_roles(token)
        query = MembersQuery.from_request(self.server.schema, params)
        with self.server.session(**self.session_kwargs) as session:
            result = session.fetch_records(query)
        return MembersResponseModel.from_result(query, result)

    @ll.route("PUT", "/debug/flush", debug=True, include_in_schema=False)
    def debug_flush(self, token: Optional[ll.AuthToken] = Depends(auth_token)) -> Response:
        """Clear the DataQuery cache."""
        roles = self.auth.get_roles(token)
        if "sysadmin" not in roles:
            raise NotAuthorized("debug.flush_cache", roles)

        self.server.clear_cache()
        return Response("OK", status_code=202)

    @ll.route("GET", "/debug/schema", debug=True, include_in_schema=False)
    def debug_schema(self, token: Optional[ll.AuthToken] = Depends(auth_token)) -> AnyDict:
        """Return the true internal schema, used to validate the requests."""
        roles = self.auth.get_roles(token)
        if "sysadmin" not in roles:
            raise NotAuthorized("debug.schema_tree", roles)

        return dataclasses.asdict(self.server.raw_schema)

    @ll.route("GET", "/debug/query", debug=True, include_in_schema=False)
    def debug_sql(
        self,
        accept: str = Header(alias="Accept"),
        params: DataRequest = Depends(dataquery_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> Response:
        """Return the generated SQL query for the same parameters of a data request."""
        roles = self.auth.get_roles(token)
        if "sysadmin" not in roles:
            raise NotAuthorized("debug.query_sql", roles)

        params.roles = roles
        query = self.server.build_query(params)
        debug = self.server.debug_query(query)

        return debug_response(accept, request=params, query=query, debug=debug)

    @ll.exception_handler(ValidationError)
    async def exc_validationerror(self, _: Request, exc: ValidationError) -> Response:
        """Handle errors derived from pydantic validation.

        fastapi.RequestValidationError is supposed to be a subclass of pydantic.ValidationError.
        There are [ongoing discussions](https://github.com/fastapi/fastapi/issues/10424) on how
        should be implemented, but in the meanwhile we are gonna need both exception handlers.
        """
        message = "Parameter type validation failed. Please check the following values:\n"

        for error in exc.errors(include_url=False):
            param = "".join(f"[{i}]" if isinstance(i, int) else f".{i}" for i in error["loc"])
            detail = error["msg"].removeprefix("Value error, ")
            message += f"  Parameter {param[1:]!r}: {detail} (user input: {error['input']!r})\n"

        return JSONResponse({"error": True, "detail": message.rstrip()}, status_code=400)

    @ll.exception_handler(RequestValidationError)
    async def exc_requestvalidationerror(self, _: Request, exc: RequestValidationError) -> Response:
        """Reformat errors derived from data model validations.

        fastapi.RequestValidationError is supposed to be a subclass of pydantic.ValidationError.
        There are [ongoing discussions](https://github.com/fastapi/fastapi/issues/10424) on how
        should be implemented, but in the meanwhile we are gonna need both exception handlers.
        """
        message = "Parameter type validation failed. Please check the following values:\n"

        for error in exc.errors():
            param = "".join(f"[{i}]" if isinstance(i, int) else f".{i}" for i in error["loc"])
            detail = error["msg"].removeprefix("Value error, ")
            message += f"  Parameter {param[1:]!r}: {detail} (user input: {error['input']!r})\n"

        return JSONResponse({"error": True, "detail": message.rstrip()}, status_code=400)

    @ll.exception_handler(TesseractError)
    async def exc_tesseracterror(self, _: Request, exc: TesseractError) -> Response:
        """Handle errors derived from the tesseract_olap package."""
        content: AnyDict = {"error": True, "detail": "Backend error"}

        # In debug mode give extra information
        if self.debug:
            content.update(
                debug_mode=True,
                type=type(exc).__name__,
                detail=exc.message,
                traceback=traceback.format_exception(None, exc, exc.__traceback__),
            )

        if isinstance(exc, NotAuthorized):
            roles = tuple(exc.roles)
            # TODO: `visitor` is a hardcoded value, must be explained in docs
            if len(roles) == 0 or "visitor" in roles:
                exc.code = 401
                wall = "The requested resource needs authorization."
            else:
                exc.code = 403
                wall = "You don't have authorization to access this resource."
            content["detail"] = exc.message if self.debug else wall

        # Error code 4xx means the user can and should fix the request
        elif 399 < exc.code < 500:
            content["detail"] = exc.message

        return JSONResponse(content, status_code=exc.code)
