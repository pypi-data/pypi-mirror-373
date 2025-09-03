import uuid
import datetime

from typing import Literal

from pydantic import BaseModel, ConfigDict

from ..._resource import SyncAPIResource


class TestingLogBase(BaseModel):
    testing_metric_id: uuid.UUID
    value: str


class TestingLog(TestingLogBase):
    id: uuid.UUID
    created_at: datetime.datetime
    project_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class TestingMetricBase(BaseModel):
    name: str
    type: Literal["string", "integer", "float"]
    description: str


class TestingMetric(TestingMetricBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_by_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


__all__ = ["Logs"]


class Logs(SyncAPIResource):

    def _get_modulos_client_source_id(self, project_id: str) -> str:
        """Get the source ID for the Modulos client."""

        response = self._get(f"/v2/testing/sources/?project_id={project_id}")

        if response.ok:

            sources = response.json()

            source = next(
                (source for source in sources if source["mode"] == "push"), None
            )
            if source:
                return source["id"]
            else:
                raise ValueError("Could not find a push source for the project.")

        else:
            print(f"Could not get source ID: {response.text}")
            return ""

    def log_metric(
        self,
        metric_id: str,
        value: str | int | float,
        project_id: str,
    ) -> TestingLog | None:
        """Log a metric for a project.

        Args:
            metric_id (str): The metric ID.
            value (str | int | float): The value of the metric.
            project_id (str): The project ID.

        Returns:
            TestingLog | None: The logged metric.
        """

        response = self._post(
            f"/v1/projects/{project_id}/testing/logs",
            data={
                "testing_metric_id": metric_id,
                "value": value,
            },
        )

        return TestingLog.model_validate(response.json())

    def create_metric(
        self,
        name: str,
        project_id: str,
        type: Literal["string", "integer", "float"],
        description: str,
    ) -> TestingMetric | None:
        """Create a metric for a project.

        Args:
            name (str): The name of the metric.
            project_id (str): The project ID.
            type (Literal["string", "integer", "float"]): The type of the metric.
            description (str): The description of the metric.

        Returns:
            TestingMetric | None: The created metric.
        """

        source_id = self._get_modulos_client_source_id(project_id)
        response = self._post(
            f"/v2/testing/sources/{source_id}/metrics?project_id={project_id}&source_id={source_id}",  # noqa E501
            data={
                "name": name,
                "type": type,
                "description": description,
            },
        )

        return TestingMetric.model_validate(response.json())

    def get_metrics(self, project_id: str) -> list[TestingMetric] | None:
        """Get metrics for a project.

        Args:
            project_id (str): The project ID.

        Returns:
            list[TestingMetric] | None: The metrics.
        """

        source_id = self._get_modulos_client_source_id(project_id)
        response = self._get(
            f"/v2/testing/sources/{source_id}/metrics?project_id={project_id}&source_id={source_id}"  # noqa E501
        )

        return [TestingMetric.model_validate(metric) for metric in response.json()]

    def get_metric(self, metric_id: str, project_id: str) -> TestingMetric | None:
        """Get a metric for a project.

        Args:
            metric_id (str): The metric ID.
            project_id (str): The project ID.

        Returns:
            TestingMetric | None: The metric.
        """

        source_id = self._get_modulos_client_source_id(project_id)
        response = self._get(
            f"/v2/testing/sources/{source_id}/metrics?project_id={project_id}&source_id={source_id}&metric_id={metric_id}"  # noqa E501
        )

        return TestingMetric.model_validate(response.json())
