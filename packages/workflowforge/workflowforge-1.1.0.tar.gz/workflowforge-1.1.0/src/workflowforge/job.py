"""Definición de Jobs para workflows de GitHub Actions."""

from typing import Any

from pydantic import BaseModel, Field

from .environment import Environment
from .step import Step
from .strategy import Strategy


class Job(BaseModel):
    """Represents a job in a GitHub Actions workflow."""

    runs_on: str | list[str] = Field(..., description="Runner donde ejecutar el job")
    steps: list[Step] = Field(default_factory=list, description="Pasos del job")
    needs: str | list[str] | None = Field(None, description="Jobs de los que depende")
    if_condition: str | None = Field(
        None, alias="if", description="Condición para ejecutar el job"
    )
    strategy: Strategy | None = Field(None, description="Estrategia de matriz")
    environment: str | Environment | None = Field(
        None, description="Entorno de despliegue"
    )
    env: dict[str, str] | None = Field(None, description="Variables de entorno del job")
    defaults: dict[str, Any] | None = Field(
        None, description="Configuraciones por defecto"
    )
    timeout_minutes: int | None = Field(None, description="Timeout en minutos")
    continue_on_error: bool | None = Field(None, description="Continuar si hay error")
    container: str | dict[str, Any] | None = Field(
        None, description="Contenedor para el job"
    )
    services: dict[str, Any] | None = Field(None, description="Servicios del job")
    outputs: dict[str, str] | None = Field(None, description="Outputs del job")
    permissions: dict[str, str] | None = Field(None, description="Permisos del job")

    def add_step(self, step: Step) -> "Job":
        """Add a step to the job."""
        self.steps.append(step)
        return self

    def set_env(self, key: str, value: str) -> "Job":
        """Set an environment variable."""
        if self.env is None:
            self.env = {}
        self.env[key] = value
        return self

    def set_needs(self, *job_ids: str) -> "Job":
        """Set job dependencies."""
        if len(job_ids) == 1:
            self.needs = job_ids[0]
        else:
            self.needs = list(job_ids)
        return self

    def set_condition(self, condition: str) -> "Job":
        """Set condition for job execution."""
        self.if_condition = condition
        return self

    def set_timeout(self, minutes: int) -> "Job":
        """Set job timeout."""
        self.timeout_minutes = minutes
        return self

    def set_output(self, key: str, value: str) -> "Job":
        """Set job output."""
        if self.outputs is None:
            self.outputs = {}
        self.outputs[key] = value
        return self

    def set_permissions(self, permissions: dict[str, str]) -> "Job":
        """Set job permissions."""
        self.permissions = permissions
        return self

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Serialize job to dictionary, converting steps correctly."""
        data = super().model_dump(**kwargs)

        # Convertir steps usando su método to_dict()
        if "steps" in data and data["steps"]:
            data["steps"] = [step.to_dict() for step in self.steps]

        # Convertir environment si es un objeto Environment
        if "environment" in data and hasattr(data["environment"], "model_dump"):
            data["environment"] = data["environment"].model_dump()

        # Convertir if_condition a if
        if "if_condition" in data and data["if_condition"]:
            data["if"] = data["if_condition"]
            del data["if_condition"]

        # Convertir runs_on a runs-on
        if "runs_on" in data:
            data["runs-on"] = data["runs_on"]
            del data["runs_on"]

        return data
