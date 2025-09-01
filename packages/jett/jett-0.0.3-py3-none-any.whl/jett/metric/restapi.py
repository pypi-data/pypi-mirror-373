import base64
import json
import logging
from typing import Annotated, Literal, Union
from urllib import parse

from pydantic import BaseModel, Field, SecretStr
from pydantic.functional_validators import model_validator
from requests import Request, Session
from requests.adapters import HTTPAdapter, Retry

from ..__types import DictData
from ..models import MetricData
from .__abc import BaseMetric

logger = logging.getLogger("jett")


class BasicAuth(BaseModel):
    """Basic Authenticate."""

    type: Literal["basic"]
    username: str
    password: SecretStr

    def apply(self, request: Request) -> Request:
        """Apply Basic Authentication."""
        # ARCHIVE:
        # from requests.auth import HTTPBasicAuth
        #
        # request.auth = HTTPBasicAuth(self.username, self.password)
        encoded = base64.b64encode(
            bytes(
                f"{self.username}:{self.password.get_secret_value()}", "utf-8"
            )
        )
        request.headers.update({"Authorization": f"Basic {encoded.decode()}"})
        return request


RestAPIAuth = Annotated[
    Union[BasicAuth,],
    Field(discriminator="type"),
]


class RestAPI(BaseMetric):
    """Metric RestAPI model."""

    type: Literal["restapi"]
    base_url: str
    path: str
    method: Literal["POST", "GET", "PUT", "PATCH"]
    header: dict[str, str | int] = Field(default_factory=dict)
    authentication: RestAPIAuth | None = None
    retry: int = 0
    retry_on_status: list[int] = Field(default_factory=list)
    timeout: int = 30

    @model_validator(mode="after")
    def __post_validate(self):
        """Validate URL."""
        parse_result = parse.urlparse(f"{self.base_url}{self.path}")
        if (
            parse_result.scheme not in ["http", "https"]
            or parse_result.netloc == ""
        ):
            raise ValueError("invalid base_url or path")

        if self.retry > 0 and len(self.retry_on_status) == 0:
            raise ValueError(
                "Please specify response status code for retrying mechanism"
            )
        return self

    def attach_retry(self, session: Session) -> None:
        """Attach Retry mechanism to the Session object."""
        retry_mec = Retry(
            total=self.retry,
            backoff_factor=2,
            status_forcelist=self.retry_on_status,
            allowed_methods=[self.method],
        )
        session.mount("http://", HTTPAdapter(max_retries=retry_mec))
        session.mount("https://", HTTPAdapter(max_retries=retry_mec))

    def emit(self, data: MetricData, convert: DictData, **kwargs) -> None:
        """Emit"""
        with Session() as session:
            url: str = f"{self.base_url}{self.path}"
            request = Request(
                method=self.method,
                url=url,
                data=json.dumps(convert, default=str),
                headers=self.header,
            )

            if self.retry > 0 and len(self.retry_on_status) > 0:
                self.attach_retry(session)

            if self.authentication:
                self.authentication.apply(request)

            logger.info("📩 Metric - RestAPI")
            logger.info(
                f"Pushing metric to: {self.method} {url}, with payload:\n"
                f"{json.dumps(convert, default=str, indent=1)}"
            )
            response = session.send(request.prepare(), timeout=self.timeout)
            response.raise_for_status()
            logger.info(
                f"Response status code of pushing metric to: "
                f"{self.method} {url}, is {response.status_code}",
            )
