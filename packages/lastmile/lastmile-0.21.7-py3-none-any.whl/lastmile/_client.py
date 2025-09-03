# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._compat import cached_property
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import LastmileError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import datasets, projects, evaluation, experiments, fine_tune_jobs, label_dataset_jobs
    from .resources.datasets import DatasetsResource, AsyncDatasetsResource
    from .resources.projects import ProjectsResource, AsyncProjectsResource
    from .resources.evaluation import EvaluationResource, AsyncEvaluationResource
    from .resources.experiments import ExperimentsResource, AsyncExperimentsResource
    from .resources.fine_tune_jobs import FineTuneJobsResource, AsyncFineTuneJobsResource
    from .resources.label_dataset_jobs import LabelDatasetJobsResource, AsyncLabelDatasetJobsResource

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Lastmile",
    "AsyncLastmile",
    "Client",
    "AsyncClient",
]


class Lastmile(SyncAPIClient):
    # client options
    bearer_token: str

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Lastmile client instance.

        This automatically infers the `bearer_token` argument from the `LASTMILE_API_TOKEN` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = os.environ.get("LASTMILE_API_TOKEN")
        if bearer_token is None:
            raise LastmileError(
                "The bearer_token client option must be set either by passing bearer_token to the client or by setting the LASTMILE_API_TOKEN environment variable"
            )
        self.bearer_token = bearer_token

        if base_url is None:
            base_url = os.environ.get("LASTMILE_BASE_URL")
        if base_url is None:
            base_url = f"https://lastmileai.dev"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

    @cached_property
    def projects(self) -> ProjectsResource:
        from .resources.projects import ProjectsResource

        return ProjectsResource(self)

    @cached_property
    def experiments(self) -> ExperimentsResource:
        from .resources.experiments import ExperimentsResource

        return ExperimentsResource(self)

    @cached_property
    def datasets(self) -> DatasetsResource:
        from .resources.datasets import DatasetsResource

        return DatasetsResource(self)

    @cached_property
    def evaluation(self) -> EvaluationResource:
        from .resources.evaluation import EvaluationResource

        return EvaluationResource(self)

    @cached_property
    def fine_tune_jobs(self) -> FineTuneJobsResource:
        from .resources.fine_tune_jobs import FineTuneJobsResource

        return FineTuneJobsResource(self)

    @cached_property
    def label_dataset_jobs(self) -> LabelDatasetJobsResource:
        from .resources.label_dataset_jobs import LabelDatasetJobsResource

        return LabelDatasetJobsResource(self)

    @cached_property
    def with_raw_response(self) -> LastmileWithRawResponse:
        return LastmileWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LastmileWithStreamedResponse:
        return LastmileWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        return {"Authorization": f"Bearer {bearer_token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncLastmile(AsyncAPIClient):
    # client options
    bearer_token: str

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncLastmile client instance.

        This automatically infers the `bearer_token` argument from the `LASTMILE_API_TOKEN` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = os.environ.get("LASTMILE_API_TOKEN")
        if bearer_token is None:
            raise LastmileError(
                "The bearer_token client option must be set either by passing bearer_token to the client or by setting the LASTMILE_API_TOKEN environment variable"
            )
        self.bearer_token = bearer_token

        if base_url is None:
            base_url = os.environ.get("LASTMILE_BASE_URL")
        if base_url is None:
            base_url = f"https://lastmileai.dev"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

    @cached_property
    def projects(self) -> AsyncProjectsResource:
        from .resources.projects import AsyncProjectsResource

        return AsyncProjectsResource(self)

    @cached_property
    def experiments(self) -> AsyncExperimentsResource:
        from .resources.experiments import AsyncExperimentsResource

        return AsyncExperimentsResource(self)

    @cached_property
    def datasets(self) -> AsyncDatasetsResource:
        from .resources.datasets import AsyncDatasetsResource

        return AsyncDatasetsResource(self)

    @cached_property
    def evaluation(self) -> AsyncEvaluationResource:
        from .resources.evaluation import AsyncEvaluationResource

        return AsyncEvaluationResource(self)

    @cached_property
    def fine_tune_jobs(self) -> AsyncFineTuneJobsResource:
        from .resources.fine_tune_jobs import AsyncFineTuneJobsResource

        return AsyncFineTuneJobsResource(self)

    @cached_property
    def label_dataset_jobs(self) -> AsyncLabelDatasetJobsResource:
        from .resources.label_dataset_jobs import AsyncLabelDatasetJobsResource

        return AsyncLabelDatasetJobsResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncLastmileWithRawResponse:
        return AsyncLastmileWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLastmileWithStreamedResponse:
        return AsyncLastmileWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        return {"Authorization": f"Bearer {bearer_token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class LastmileWithRawResponse:
    _client: Lastmile

    def __init__(self, client: Lastmile) -> None:
        self._client = client

    @cached_property
    def projects(self) -> projects.ProjectsResourceWithRawResponse:
        from .resources.projects import ProjectsResourceWithRawResponse

        return ProjectsResourceWithRawResponse(self._client.projects)

    @cached_property
    def experiments(self) -> experiments.ExperimentsResourceWithRawResponse:
        from .resources.experiments import ExperimentsResourceWithRawResponse

        return ExperimentsResourceWithRawResponse(self._client.experiments)

    @cached_property
    def datasets(self) -> datasets.DatasetsResourceWithRawResponse:
        from .resources.datasets import DatasetsResourceWithRawResponse

        return DatasetsResourceWithRawResponse(self._client.datasets)

    @cached_property
    def evaluation(self) -> evaluation.EvaluationResourceWithRawResponse:
        from .resources.evaluation import EvaluationResourceWithRawResponse

        return EvaluationResourceWithRawResponse(self._client.evaluation)

    @cached_property
    def fine_tune_jobs(self) -> fine_tune_jobs.FineTuneJobsResourceWithRawResponse:
        from .resources.fine_tune_jobs import FineTuneJobsResourceWithRawResponse

        return FineTuneJobsResourceWithRawResponse(self._client.fine_tune_jobs)

    @cached_property
    def label_dataset_jobs(self) -> label_dataset_jobs.LabelDatasetJobsResourceWithRawResponse:
        from .resources.label_dataset_jobs import LabelDatasetJobsResourceWithRawResponse

        return LabelDatasetJobsResourceWithRawResponse(self._client.label_dataset_jobs)


class AsyncLastmileWithRawResponse:
    _client: AsyncLastmile

    def __init__(self, client: AsyncLastmile) -> None:
        self._client = client

    @cached_property
    def projects(self) -> projects.AsyncProjectsResourceWithRawResponse:
        from .resources.projects import AsyncProjectsResourceWithRawResponse

        return AsyncProjectsResourceWithRawResponse(self._client.projects)

    @cached_property
    def experiments(self) -> experiments.AsyncExperimentsResourceWithRawResponse:
        from .resources.experiments import AsyncExperimentsResourceWithRawResponse

        return AsyncExperimentsResourceWithRawResponse(self._client.experiments)

    @cached_property
    def datasets(self) -> datasets.AsyncDatasetsResourceWithRawResponse:
        from .resources.datasets import AsyncDatasetsResourceWithRawResponse

        return AsyncDatasetsResourceWithRawResponse(self._client.datasets)

    @cached_property
    def evaluation(self) -> evaluation.AsyncEvaluationResourceWithRawResponse:
        from .resources.evaluation import AsyncEvaluationResourceWithRawResponse

        return AsyncEvaluationResourceWithRawResponse(self._client.evaluation)

    @cached_property
    def fine_tune_jobs(self) -> fine_tune_jobs.AsyncFineTuneJobsResourceWithRawResponse:
        from .resources.fine_tune_jobs import AsyncFineTuneJobsResourceWithRawResponse

        return AsyncFineTuneJobsResourceWithRawResponse(self._client.fine_tune_jobs)

    @cached_property
    def label_dataset_jobs(self) -> label_dataset_jobs.AsyncLabelDatasetJobsResourceWithRawResponse:
        from .resources.label_dataset_jobs import AsyncLabelDatasetJobsResourceWithRawResponse

        return AsyncLabelDatasetJobsResourceWithRawResponse(self._client.label_dataset_jobs)


class LastmileWithStreamedResponse:
    _client: Lastmile

    def __init__(self, client: Lastmile) -> None:
        self._client = client

    @cached_property
    def projects(self) -> projects.ProjectsResourceWithStreamingResponse:
        from .resources.projects import ProjectsResourceWithStreamingResponse

        return ProjectsResourceWithStreamingResponse(self._client.projects)

    @cached_property
    def experiments(self) -> experiments.ExperimentsResourceWithStreamingResponse:
        from .resources.experiments import ExperimentsResourceWithStreamingResponse

        return ExperimentsResourceWithStreamingResponse(self._client.experiments)

    @cached_property
    def datasets(self) -> datasets.DatasetsResourceWithStreamingResponse:
        from .resources.datasets import DatasetsResourceWithStreamingResponse

        return DatasetsResourceWithStreamingResponse(self._client.datasets)

    @cached_property
    def evaluation(self) -> evaluation.EvaluationResourceWithStreamingResponse:
        from .resources.evaluation import EvaluationResourceWithStreamingResponse

        return EvaluationResourceWithStreamingResponse(self._client.evaluation)

    @cached_property
    def fine_tune_jobs(self) -> fine_tune_jobs.FineTuneJobsResourceWithStreamingResponse:
        from .resources.fine_tune_jobs import FineTuneJobsResourceWithStreamingResponse

        return FineTuneJobsResourceWithStreamingResponse(self._client.fine_tune_jobs)

    @cached_property
    def label_dataset_jobs(self) -> label_dataset_jobs.LabelDatasetJobsResourceWithStreamingResponse:
        from .resources.label_dataset_jobs import LabelDatasetJobsResourceWithStreamingResponse

        return LabelDatasetJobsResourceWithStreamingResponse(self._client.label_dataset_jobs)


class AsyncLastmileWithStreamedResponse:
    _client: AsyncLastmile

    def __init__(self, client: AsyncLastmile) -> None:
        self._client = client

    @cached_property
    def projects(self) -> projects.AsyncProjectsResourceWithStreamingResponse:
        from .resources.projects import AsyncProjectsResourceWithStreamingResponse

        return AsyncProjectsResourceWithStreamingResponse(self._client.projects)

    @cached_property
    def experiments(self) -> experiments.AsyncExperimentsResourceWithStreamingResponse:
        from .resources.experiments import AsyncExperimentsResourceWithStreamingResponse

        return AsyncExperimentsResourceWithStreamingResponse(self._client.experiments)

    @cached_property
    def datasets(self) -> datasets.AsyncDatasetsResourceWithStreamingResponse:
        from .resources.datasets import AsyncDatasetsResourceWithStreamingResponse

        return AsyncDatasetsResourceWithStreamingResponse(self._client.datasets)

    @cached_property
    def evaluation(self) -> evaluation.AsyncEvaluationResourceWithStreamingResponse:
        from .resources.evaluation import AsyncEvaluationResourceWithStreamingResponse

        return AsyncEvaluationResourceWithStreamingResponse(self._client.evaluation)

    @cached_property
    def fine_tune_jobs(self) -> fine_tune_jobs.AsyncFineTuneJobsResourceWithStreamingResponse:
        from .resources.fine_tune_jobs import AsyncFineTuneJobsResourceWithStreamingResponse

        return AsyncFineTuneJobsResourceWithStreamingResponse(self._client.fine_tune_jobs)

    @cached_property
    def label_dataset_jobs(self) -> label_dataset_jobs.AsyncLabelDatasetJobsResourceWithStreamingResponse:
        from .resources.label_dataset_jobs import AsyncLabelDatasetJobsResourceWithStreamingResponse

        return AsyncLabelDatasetJobsResourceWithStreamingResponse(self._client.label_dataset_jobs)


Client = Lastmile

AsyncClient = AsyncLastmile
