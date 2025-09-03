from typing import List, Optional

from anyscale._private.models.model_base import ResultIterator
from anyscale._private.sdk import sdk_command
from anyscale.client.openapi_client.models.job_queue_sort_directive import (
    JobQueueSortDirective,
)
from anyscale.client.openapi_client.models.session_state import SessionState
from anyscale.job_queue._private.job_queue_sdk import PrivateJobQueueSDK
from anyscale.job_queue.models import JobQueueStatus


_JOB_QUEUE_SDK_SINGLETON_KEY = "job_queue_sdk"


_LIST_EXAMPLE = """
import anyscale

# Example: List the first 50 job queues
for jq in anyscale.job_queue.list(max_items=50):
    print(jq.id, jq.name, jq.state)
"""

_LIST_ARG_DOCSTRINGS = {
    "job_queue_id": "If provided, fetches only the job queue with this ID.",
    "name": "Filter by job queue name.",
    "creator_id": "Filter by the user ID of the creator.",
    "cloud": "Filter by cloud name.",
    "project": "Filter by project name.",
    "cluster_status": "Filter by the state of the associated cluster.",
    "page_size": "Number of items per API request page.",
    "max_items": "Maximum total number of items to return.",
    "sorting_directives": "List of directives to sort the results.",
}

_STATUS_EXAMPLE = """
import anyscale

status = anyscale.job_queue.status(job_queue_id=\"jobq_abc123\")
print(status)
"""

_STATUS_ARG_DOCSTRINGS = {
    "job_queue_id": "The unique ID of the job queue.",
}

_UPDATE_EXAMPLE = """
import anyscale

updated_jq = anyscale.job_queue.update(job_queue_id=\"jobq_abc123\", max_concurrency=5)
print(updated_jq)
"""

_UPDATE_ARG_DOCSTRINGS = {
    "job_queue_id": "ID of the job queue to update.",
    "job_queue_name": "Name of the job queue to update (alternative to ID).",
    "max_concurrency": "New maximum concurrency value.",
    "idle_timeout_s": "New idle timeout in seconds.",
}


@sdk_command(
    _JOB_QUEUE_SDK_SINGLETON_KEY,
    PrivateJobQueueSDK,
    doc_py_example=_LIST_EXAMPLE,
    arg_docstrings=_LIST_ARG_DOCSTRINGS,
)
def list(  # noqa: A001
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
    _private_sdk: Optional[PrivateJobQueueSDK] = None,
) -> ResultIterator[JobQueueStatus]:
    """List job queues or fetch a single job queue by ID."""
    return _private_sdk.list(  # type: ignore
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


@sdk_command(
    _JOB_QUEUE_SDK_SINGLETON_KEY,
    PrivateJobQueueSDK,
    doc_py_example=_STATUS_EXAMPLE,
    arg_docstrings=_STATUS_ARG_DOCSTRINGS,
)
def status(
    job_queue_id: str, _private_sdk: Optional[PrivateJobQueueSDK] = None
) -> JobQueueStatus:
    """Get the status and details for a specific job queue."""
    return _private_sdk.status(  # type: ignore
        job_queue_id=job_queue_id
    )


@sdk_command(
    _JOB_QUEUE_SDK_SINGLETON_KEY,
    PrivateJobQueueSDK,
    doc_py_example=_UPDATE_EXAMPLE,
    arg_docstrings=_UPDATE_ARG_DOCSTRINGS,
)
def update(
    *,
    job_queue_id: Optional[str] = None,
    job_queue_name: Optional[str] = None,
    max_concurrency: Optional[int] = None,
    idle_timeout_s: Optional[int] = None,
    _private_sdk: Optional[PrivateJobQueueSDK] = None,
) -> JobQueueStatus:
    """Update a job queue."""
    return _private_sdk.update(  # type: ignore
        job_queue_id=job_queue_id,
        job_queue_name=job_queue_name,
        max_concurrency=max_concurrency,
        idle_timeout_s=idle_timeout_s,
    )
