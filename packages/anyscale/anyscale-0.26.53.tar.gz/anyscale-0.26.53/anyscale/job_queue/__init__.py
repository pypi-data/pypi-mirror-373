from typing import List, Optional

from anyscale._private.anyscale_client import AnyscaleClient
from anyscale._private.models.model_base import ResultIterator
from anyscale._private.sdk import sdk_command, sdk_docs
from anyscale._private.sdk.base_sdk import Timer
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models.job_queue_sort_directive import (
    JobQueueSortDirective,
)
from anyscale.client.openapi_client.models.session_state import SessionState
from anyscale.job_queue._private.job_queue_sdk import PrivateJobQueueSDK
from anyscale.job_queue.commands import (
    _JOB_QUEUE_SDK_SINGLETON_KEY,
    _LIST_ARG_DOCSTRINGS,
    _LIST_EXAMPLE,
    _STATUS_ARG_DOCSTRINGS,
    _STATUS_EXAMPLE,
    _UPDATE_ARG_DOCSTRINGS,
    _UPDATE_EXAMPLE,
    list,
    status,
    update,
)
from anyscale.job_queue.models import JobQueueSortField, JobQueueState, JobQueueStatus


class JobQueueSDK:
    """Public SDK for interacting with Anyscale Job Queues."""

    def __init__(
        self,
        *,
        client: Optional[AnyscaleClient] = None,
        logger: Optional[BlockLogger] = None,
        timer: Optional[Timer] = None,
    ):
        self._private_sdk = PrivateJobQueueSDK(
            client=client, logger=logger, timer=timer
        )

    @sdk_docs(doc_py_example=_LIST_EXAMPLE, arg_docstrings=_LIST_ARG_DOCSTRINGS)
    def list(  # noqa: F811
        self,
        *,
        job_queue_id: Optional[str] = None,
        name: Optional[str] = None,
        creator_id: Optional[str] = None,
        cloud: Optional[str] = None,
        project: Optional[str] = None,
        cluster_status: Optional[SessionState] = None,
        page_size: Optional[int] = None,
        max_items: Optional[int] = None,
        sorting_directives: Optional[List[JobQueueSortDirective]] = None,
    ) -> ResultIterator[JobQueueStatus]:
        """List job queues or fetch a single job queue by ID."""
        return self._private_sdk.list(
            job_queue_id=job_queue_id,
            name=name,
            creator_id=creator_id,
            cloud=cloud,
            project=project,
            cluster_status=cluster_status,
            page_size=page_size,
            max_items=max_items,
            sorting_directives=sorting_directives,
        )

    @sdk_docs(doc_py_example=_STATUS_EXAMPLE, arg_docstrings=_STATUS_ARG_DOCSTRINGS)
    def status(self, job_queue_id: str) -> JobQueueStatus:  # noqa: F811
        """Get the status and details for a specific job queue."""
        return self._private_sdk.status(job_queue_id=job_queue_id)

    @sdk_docs(doc_py_example=_UPDATE_EXAMPLE, arg_docstrings=_UPDATE_ARG_DOCSTRINGS)
    def update(  # noqa: F811
        self,
        *,
        job_queue_id: Optional[str] = None,
        job_queue_name: Optional[str] = None,
        max_concurrency: Optional[int] = None,
        idle_timeout_s: Optional[int] = None,
    ) -> JobQueueStatus:
        """Update a job queue."""
        return self._private_sdk.update(
            job_queue_id=job_queue_id,
            job_queue_name=job_queue_name,
            max_concurrency=max_concurrency,
            idle_timeout_s=idle_timeout_s,
        )
