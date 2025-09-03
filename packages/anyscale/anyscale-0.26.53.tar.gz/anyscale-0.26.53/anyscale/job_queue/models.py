from dataclasses import dataclass, field
from datetime import datetime
from typing import get_type_hints, Literal, Optional, TYPE_CHECKING, Union

from anyscale._private.models import ModelBase, ModelEnum


class JobQueueState(ModelEnum):
    """Current state of a job queue."""

    ACTIVE = "ACTIVE"
    SEALED = "SEALED"
    # Add other potential states if necessary based on API reality
    UNKNOWN = "UNKNOWN"

    __docstrings__ = {
        ACTIVE: "The job queue is active and accepting jobs.",
        SEALED: "The job queue is sealed and not accepting new jobs. It may still be processing existing jobs.",
        UNKNOWN: "The state of the job queue is unknown or could not be determined.",
    }


class JobQueueSortField(ModelEnum):
    """Fields available for sorting job queues."""

    ID = "ID"
    NAME = "NAME"
    CREATED_AT = "CREATED_AT"
    CREATOR_ID = "CREATOR_ID"
    CREATOR_EMAIL = "CREATOR_EMAIL"
    PROJECT_ID = "PROJECT_ID"
    CLOUD_ID = "CLOUD_ID"
    QUEUE_STATE = "QUEUE_STATE"
    CLUSTER_STATE = "CLUSTER_STATE"

    __docstrings__ = {
        ID: "Sort by Job Queue ID.",
        NAME: "Sort by Job Queue name.",
        CREATED_AT: "Sort by creation timestamp.",
        CREATOR_ID: "Sort by the ID of the creator.",
        CREATOR_EMAIL: "Sort by the email of the creator.",
        PROJECT_ID: "Sort by the Project ID.",
        CLOUD_ID: "Sort by the Cloud ID.",
        QUEUE_STATE: "Sort by the Job Queue's state (ACTIVE, SEALED).",
        CLUSTER_STATE: "Sort by the state of the associated cluster.",
    }


class ExecutionMode(ModelEnum):
    """Execution mode of a job queue."""

    FIFO = "FIFO"
    LIFO = "LIFO"
    PRIORITY = "PRIORITY"
    # Add other execution modes as needed
    UNKNOWN = "UNKNOWN"

    __docstrings__ = {
        FIFO: "FIFO execution mode.",
        LIFO: "LIFO execution mode.",
        PRIORITY: "Priority-based execution mode.",
        UNKNOWN: "Unknown execution mode.",
    }


class ClusterState(ModelEnum):
    """Possible states for a cluster."""

    RUNNING = "RUNNING"
    TERMINATED = "TERMINATED"
    PENDING = "PENDING"
    # Add other states as needed
    UNKNOWN = "UNKNOWN"

    __docstrings__ = {
        RUNNING: "The cluster is running.",
        TERMINATED: "The cluster is terminated.",
        PENDING: "The cluster is pending creation.",
        UNKNOWN: "The state of the cluster is unknown.",
    }


@dataclass(frozen=True)
class JobQueueStatus(ModelBase):
    """Represents the status and details of a Job Queue."""

    id: str = field(metadata={"docstring": "Unique ID of the job queue."})
    state: Union[JobQueueState, str] = field(
        metadata={"docstring": "Current state of the job queue."}
    )
    name: Optional[str] = field(
        default=None, metadata={"docstring": "Name of the job queue."}
    )
    creator_email: Optional[str] = field(
        default=None,
        metadata={"docstring": "Email of the user who created the job queue."},
    )
    project_id: Optional[str] = field(
        default=None,
        metadata={"docstring": "ID of the project this job queue belongs to."},
    )
    created_at: Optional[datetime] = field(
        default=None,
        metadata={"docstring": "Timestamp when the job queue was created."},
    )
    max_concurrency: Optional[int] = field(
        default=None,
        metadata={"docstring": "Maximum number of jobs allowed to run concurrently."},
    )
    idle_timeout_s: Optional[int] = field(
        default=None,
        metadata={
            "docstring": "Idle timeout in seconds before the queue's cluster may shut down."
        },
    )
    user_provided_id: Optional[str] = field(
        default=None,
        metadata={"docstring": "User provided identifier of the job queue."},
    )
    execution_mode: Optional[Union[ExecutionMode, str]] = field(
        default=None, metadata={"docstring": "The execution mode of the job queue."}
    )
    creator_id: Optional[str] = field(
        default=None,
        metadata={"docstring": "Identifier of user who created the job queue."},
    )
    cloud_id: Optional[str] = field(
        default=None,
        metadata={"docstring": "The cloud ID associated with the job queue."},
    )
    total_jobs: Optional[int] = field(
        default=None, metadata={"docstring": "Total number of jobs in the job queue."},
    )
    successful_jobs: Optional[int] = field(
        default=None,
        metadata={"docstring": "Number of successful jobs in the job queue."},
    )
    failed_jobs: Optional[int] = field(
        default=None, metadata={"docstring": "Number of failed jobs in the job queue."},
    )
    active_jobs: Optional[int] = field(
        default=None, metadata={"docstring": "Number of active jobs in the job queue."},
    )

    def _validate_id(self, id: str) -> str:  # noqa: A002
        if not isinstance(id, str) or not id:
            raise ValueError("'id' must be a non-empty string.")
        return id

    def _validate_name(self, name: Optional[str]) -> Optional[str]:
        if name is not None and not isinstance(name, str):
            raise ValueError("'name' must be a string or None.")
        return name

    def _validate_state(self, state: Union[JobQueueState, str]) -> JobQueueState:
        return JobQueueState.validate(state)

    def _validate_creator_email(self, creator_email: Optional[str]) -> Optional[str]:
        if creator_email is not None and not isinstance(creator_email, str):
            raise ValueError("'creator_email' must be a string or None.")
        return creator_email

    def _validate_project_id(self, project_id: Optional[str]) -> Optional[str]:
        if project_id is not None and not isinstance(project_id, str):
            raise ValueError("'project_id' must be a string or None.")
        return project_id

    def _validate_created_at(
        self, created_at: Optional[datetime]
    ) -> Optional[datetime]:
        if created_at is not None and not isinstance(created_at, datetime):
            raise ValueError("'created_at' must be a datetime object or None.")
        return created_at

    def _validate_max_concurrency(
        self, max_concurrency: Optional[int]
    ) -> Optional[int]:
        if max_concurrency is not None:
            if not isinstance(max_concurrency, int):
                raise ValueError("'max_concurrency' must be an integer or None.")
            if max_concurrency < 0:
                raise ValueError("'max_concurrency' cannot be negative.")
        return max_concurrency

    def _validate_idle_timeout_s(self, idle_timeout_s: Optional[int]) -> Optional[int]:
        if idle_timeout_s is not None:
            if not isinstance(idle_timeout_s, int):
                raise ValueError("'idle_timeout_s' must be an integer or None.")
            if idle_timeout_s < 0:
                raise ValueError("'idle_timeout_s' cannot be negative.")
        return idle_timeout_s

    def _validate_user_provided_id(
        self, user_provided_id: Optional[str]
    ) -> Optional[str]:
        if user_provided_id is not None and not isinstance(user_provided_id, str):
            raise ValueError("'user_provided_id' must be a string or None.")
        return user_provided_id

    def _validate_execution_mode(
        self, execution_mode: Optional[Union[ExecutionMode, str]]
    ) -> Optional[ExecutionMode]:
        if execution_mode is not None:
            return ExecutionMode.validate(execution_mode)
        return None

    def _validate_creator_id(self, creator_id: Optional[str]) -> Optional[str]:
        if creator_id is not None and not isinstance(creator_id, str):
            raise ValueError("'creator_id' must be a string or None.")
        return creator_id

    def _validate_cluster_id(self, cluster_id: Optional[str]) -> Optional[str]:
        if cluster_id is not None and not isinstance(cluster_id, str):
            raise ValueError("'cluster_id' must be a string or None.")
        return cluster_id

    def _validate_current_cluster_state(
        self, current_cluster_state: Optional[Union[ClusterState, str]]
    ) -> Optional[ClusterState]:
        if current_cluster_state is not None:
            return ClusterState.validate(current_cluster_state)
        return None

    def _validate_cloud_id(self, cloud_id: Optional[str]) -> Optional[str]:
        if cloud_id is not None and not isinstance(cloud_id, str):
            raise ValueError("'cloud_id' must be a string or None.")
        return cloud_id

    def _validate_total_jobs(self, total_jobs: Optional[int]) -> Optional[int]:
        if total_jobs is not None:
            if not isinstance(total_jobs, int):
                raise ValueError("'total_jobs' must be an integer or None.")
            if total_jobs < 0:
                raise ValueError("'total_jobs' cannot be negative.")
        return total_jobs

    def _validate_successful_jobs(
        self, successful_jobs: Optional[int]
    ) -> Optional[int]:
        if successful_jobs is not None:
            if not isinstance(successful_jobs, int):
                raise ValueError("'successful_jobs' must be an integer or None.")
            if successful_jobs < 0:
                raise ValueError("'successful_jobs' cannot be negative.")
        return successful_jobs

    def _validate_failed_jobs(self, failed_jobs: Optional[int]) -> Optional[int]:
        if failed_jobs is not None:
            if not isinstance(failed_jobs, int):
                raise ValueError("'failed_jobs' must be an integer or None.")
            if failed_jobs < 0:
                raise ValueError("'failed_jobs' cannot be negative.")
        return failed_jobs

    def _validate_active_jobs(self, active_jobs: Optional[int]) -> Optional[int]:
        if active_jobs is not None:
            if not isinstance(active_jobs, int):
                raise ValueError("'active_jobs' must be an integer or None.")
            if active_jobs < 0:
                raise ValueError("'active_jobs' cannot be negative.")
        return active_jobs


if TYPE_CHECKING:
    JobQueueStatusKeys = Literal[
        "active_jobs",
        "cloud_id",
        "created_at",
        "creator_email",
        "creator_id",
        "execution_mode",
        "failed_jobs",
        "id",
        "idle_timeout_s",
        "max_concurrency",
        "name",
        "project_id",
        "state",
        "successful_jobs",
        "total_jobs",
        "user_provided_id",
    ]
else:
    JobQueueStatusKeys = Literal[tuple(get_type_hints(JobQueueStatus).keys())]
