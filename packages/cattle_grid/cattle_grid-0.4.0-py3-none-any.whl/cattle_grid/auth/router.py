import logging

from typing import Annotated

from fastapi import HTTPException, Request, Response, APIRouter, Header
from fastapi.responses import PlainTextResponse
from starlette.datastructures import MutableHeaders

from pydantic import BaseModel, Field

from bovine.utils import webfinger_response
from bovine.types.jrd import JrdData

from cattle_grid.activity_pub.server.router import ActivityResponse
from .util import check_block
from .http_util import should_serve, ContentType

from .dependencies import (
    AuthConfig as AuthConfigDependency,
    ActorObject,
    SignatureCheckWithCache,
)

logger = logging.getLogger(__name__)


class ReverseProxyHeaders(BaseModel):
    """Headers set by the reverse proxy"""

    x_original_method: str = Field("get", description="""The original used method""")
    x_original_uri: str | None = Field(None, description="""The original request uri""")
    x_original_host: str | None = Field(None, description="""The original used host""")
    x_forwarded_proto: str = Field("http", description="""The protocol being used""")


auth_router = APIRouter(tags=["auth"])
"""The authentication router"""


@auth_router.get("/.well-known/webfinger")
async def webfinger(resource: str, config: AuthConfigDependency) -> JrdData:
    """If resource is the actor corresponding to the actor fetching
    public keys, returns the corresponding Jrd. Otherwise returns
    not found"""
    logger.info(config)
    if resource != config.actor_acct_id:
        raise HTTPException(404)
    return webfinger_response(config.actor_acct_id, config.actor_id)


@auth_router.get(
    "/cattle_grid_actor",
    response_class=ActivityResponse,
)
async def handle_get_actor(actor_object: ActorObject):
    """Returns the actor profile of the
    fetch actor used to retrieve public keys, e.g.

    ```json
    {
        "type": "Service",
        "id": "https://your-domain.example/cattle_grid_actor",
        ...
    }
    ```
    """
    return actor_object


@auth_router.get(
    "/auth",
    responses={
        200: {"description": "Request is valid", "content": {"text/plain": ""}},
        401: {"description": "The signature was invalid"},
        403: {"description": "Request was blocked"},
    },
    response_class=PlainTextResponse,
)
async def verify_signature(
    request: Request,
    response: Response,
    config: AuthConfigDependency,
    signature_checker: SignatureCheckWithCache,
    reverse_proxy_headers: Annotated[ReverseProxyHeaders, Header()],
) -> str:
    """Takes the request and checks signature. If signature check
    fails a 401 is returned. If the domain the public key belongs
    to is blocked, a 403 is returned.

    If the request is valid. The controller corresponding to
    the signature is set in the response header `X-CATTLE-GRID-REQUESTER`.

    The header `X-CATTLE-GRID-SHOULD-SERVE` is set to `html`
    if one should redirect to the HTML resource. It is set to `other` if the resource to serve cannot be determined.
    This is only used for unsigned requests.

    Note: More headers than the ones listed below can be used
    to verify a signature.
    """
    headers = MutableHeaders(request.headers)

    logger.debug(headers)

    servable_content_types = should_serve(headers.get("accept"))

    if "signature" not in headers:
        if ContentType.html in servable_content_types:
            response.headers["x-cattle-grid-should-serve"] = "html"
            return ""
        elif ContentType.other in servable_content_types:
            response.headers["x-cattle-grid-should-serve"] = "other"
            return ""
        elif config.require_signature_for_activity_pub:
            raise HTTPException(401)
        else:
            return ""

    if reverse_proxy_headers.x_original_host:
        headers["Host"] = reverse_proxy_headers.x_original_host

    url = f"{reverse_proxy_headers.x_forwarded_proto}://{reverse_proxy_headers.x_original_host}{reverse_proxy_headers.x_original_uri}"

    logger.debug("Treating request as to url %s", url)

    controller = await signature_checker.validate_signature(
        reverse_proxy_headers.x_original_method.lower(),
        url,
        dict(headers.items()),
        None,
    )

    logger.debug("Got controller %s", controller)

    if controller:
        if check_block(config.domain_blocks, controller):
            logger.info("Blocked a request by %s", controller)
            raise HTTPException(403)
        response.headers["x-cattle-grid-requester"] = controller

        logger.debug("Got requester %s", controller)

        return ""

    logger.info(
        "invalid signature for request to %s => access denied",
        request.headers.get("X-Original-Uri", ""),
    )

    raise HTTPException(401)
