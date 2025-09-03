from datetime import datetime
from typing import Any, Iterator, Sequence

from pydantic import Field, RootModel, field_validator

from fused._global_api import get_api
from fused.models.base import FusedBaseModel
from fused.models.internal import RunResponse
from fused.models.udf import BaseUdf
from fused.models.udf.base_udf import METADATA_FUSED_DESCRIPTION, METADATA_FUSED_ID


class CronJob(FusedBaseModel):
    """A scheduled run of the UDF"""

    id: str | None = None
    """ID of the cron job"""
    name: str
    """Name of the cron job"""
    description: str | None = None
    execution_environment_id: str | None = None
    """ID of the team that owns the cron job"""
    enabled: bool
    minute: list[int]
    hour: list[int]
    day_of_month: list[int]
    month: list[int]
    day_of_week: list[int]
    udf_id: str = Field(alias="udf")
    """ID of the UDF to run"""
    udf_args: dict[str, Any] | None = None
    """Arguments to pass to the UDF"""
    last_run: datetime | None = None
    """The last time the cron job was run"""

    @field_validator("minute", mode="before")
    @classmethod
    def validate_minute(cls, v):
        if isinstance(v, int):
            v = [v]
        if not isinstance(v, list) or not all(0 <= i <= 59 for i in v):
            raise ValueError("Minute must be between 0 and 59")
        if len(v) > 1:
            raise ValueError("Minute must be a single integer")
        return v

    @field_validator("hour", mode="before")
    @classmethod
    def validate_hour(cls, v):
        if isinstance(v, int):
            v = [v]
        if not isinstance(v, list) or not all(0 <= i < 24 for i in v):
            raise ValueError("Hour must be between 0 and 23")
        return v

    @field_validator("day_of_month", mode="before")
    @classmethod
    def validate_day_of_month(cls, v):
        if isinstance(v, int):
            v = [v]
        if not isinstance(v, list) or not all(1 <= i <= 31 for i in v):
            raise ValueError("Day of month must be between 1 and 31")
        return v

    @field_validator("month", mode="before")
    @classmethod
    def validate_month(cls, v):
        if isinstance(v, int):
            v = [v]
        if not isinstance(v, list) or not all(1 <= i <= 12 for i in v):
            raise ValueError("Month must be between 1 and 12")
        return v

    @field_validator("day_of_week", mode="before")
    @classmethod
    def validate_day_of_week(cls, v):
        if isinstance(v, int):
            v = [v]
        if not isinstance(v, list) or not all(0 <= i <= 6 for i in v):
            raise ValueError("Day of week must be between 0 and 6")
        return v

    @classmethod
    def from_udf(
        cls,
        udf: BaseUdf | str,
        minute: list[int] | int,
        hour: list[int] | int,
        day_of_month: list[int] | int | None = None,
        month: list[int] | int | None = None,
        day_of_week: list[int] | int | None = None,
        udf_args: dict[str, Any] | None = None,
        enabled: bool = True,
        description: str | None = None,
        _create_udf: bool = True,
        **kwargs,
    ) -> "CronJob":
        """Create a cron job from a UDF"""
        from fused._load_udf import load as fused_load

        if not isinstance(udf, BaseUdf):
            udf = fused_load(udf)

        udf_id = udf._get_metadata_safe(METADATA_FUSED_ID)
        if _create_udf and udf_id is None:
            try:
                udf = udf.to_fused()
                udf_id = udf._get_metadata_safe(METADATA_FUSED_ID)
            except Exception as e:
                raise ValueError(
                    "Could not save UDF. Call to_fused() on the UDF."
                ) from e
        elif udf_id is None:
            raise ValueError(
                "UDF has not been saved yet, call to_fused() on the UDF or CronJob.from_udf with _create_udf=True"
            )

        day_of_month = day_of_month if day_of_month is not None else list(range(1, 32))
        month = month if month is not None else list(range(1, 13))
        day_of_week = day_of_week if day_of_week is not None else list(range(7))

        cronjob = cls(
            udf_id=udf_id,
            name=udf.name,
            description=description
            or udf._get_metadata_safe(METADATA_FUSED_DESCRIPTION),
            enabled=enabled,
            minute=minute,
            hour=hour,
            day_of_month=day_of_month,
            month=month,
            day_of_week=day_of_week,
            udf_args=udf_args,
            **kwargs,
        )
        return cronjob.create()

    @classmethod
    def from_id(cls, cronjob_id: str) -> "CronJob":
        """Get a cron job by it's ID"""
        return get_api().get_cronjob(cronjob_id=cronjob_id)

    @classmethod
    def list_team(cls) -> list["CronJob"]:
        """List all cron jobs for the team"""
        return get_api().list_cronjobs()

    @property
    def udf(self) -> BaseUdf:
        """Get the UDF that this cron job will run"""
        from fused._load_udf import load as fused_load

        return fused_load(self.udf_id)

    @property
    def _schedule(self) -> str:
        """Retrieve the schedule as a cron-compatible string."""

        def format_cron_part(
            part: list[int] | int, default: list[int] | None = None
        ) -> str:
            if isinstance(part, int):
                return str(part)
            elif len(part) == 1:
                return part[0]
            elif default is not None and part == default:
                return "*"
            else:
                return ",".join(str(i) for i in part)

        minute_part = format_cron_part(self.minute, list(range(60)))
        hour_part = format_cron_part(self.hour, list(range(24)))
        dom_part = format_cron_part(self.day_of_month, list(range(1, 32)))
        month_part = format_cron_part(self.month, list(range(1, 13)))
        dow_part = format_cron_part(self.day_of_week, list(range(7)))
        return f"{minute_part} {hour_part} {dom_part} {month_part} {dow_part}"

    def delete(self) -> "CronJob":
        """Delete the cron job, unscheduling it."""
        if self.id is None:
            raise ValueError("This cron job has not been saved yet")
        deleted_cronjob = self._api.delete_cronjob(self.id)
        self.id = None
        deleted_cronjob.id = None
        return deleted_cronjob

    def create(self) -> "CronJob":
        """Create the cron job, scheduling it to run."""
        new_cronjob = self._api.create_cronjob(self)
        self.id = new_cronjob.id
        self.execution_environment_id = new_cronjob.execution_environment_id
        return new_cronjob

    def update(self, create: bool = False) -> "CronJob":
        """Update the cron job, changing its schedule or arguments using the values in this object.

        Changes on this object will not take effect until this method is called.

        Args:
            create: If True, create the cron job if it has not been saved yet.
        """
        if self.id is None:
            if create:
                return self.create()
            else:
                raise ValueError(
                    "This cron job has not been saved yet. Call update(create=True) to save it."
                )

        return self._api.update_cronjob(self)

    def refresh_from_api(self) -> "CronJob":
        """Refresh the cron job from the saved version on the server"""
        if self.id is None:
            raise ValueError("This cron job has not been saved yet")
        return self._api.get_cronjob(self.id)

    def run_now(self) -> RunResponse:
        """Trigger a run of the cron job now"""
        run = self._api.run_cronjob(self.id)
        self.last_run = run["cronjob"].last_run
        return run["run"]

    def __repr__(self) -> str:
        disabled = " [disabled]" if not self.enabled else ""
        not_saved = " [not saved -- call create()]" if not self.id else ""
        return f"<CronJob {self.name} ({self._schedule}){disabled}{not_saved}>"


class CronJobSequence(RootModel[Sequence[CronJob]]):
    def _repr_html_(self) -> str:
        rows = "\n".join(
            f"""
            <tr>
                <td>{cronjob.name}</td>
                <td>{cronjob._schedule}{" (disabled)" if not cronjob.enabled else ""}{" (not saved)" if not cronjob.id else ""}</td>
                <td>{cronjob.last_run}</td>
            </tr>
        """
            for cronjob in self.root
        )
        return f"""
        <table>
            <tr>
                <th>Name</th>
                <th>Schedule</th>
                <th>Last run</th>
            </tr>
            {rows}
        </table>
        """

    def __iter__(self) -> Iterator[CronJob]:
        return iter(self.root)

    def __getitem__(self, item: int) -> CronJob:
        return self.root[item]

    def __setitem__(self, item: int, value: CronJob) -> None:
        self.root[item] = value

    def __len__(self) -> int:
        return len(self.root)

    def __repr__(self) -> str:
        return repr(self.root)
