"""Definición de entornos para jobs."""

from typing import Any

from pydantic import BaseModel, Field


class Environment(BaseModel):
    """Represents deployment environment."""

    name: str = Field(..., description="Nombre del entorno")
    url: str | None = Field(None, description="URL del entorno")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Serialize environment."""
        result = {"name": self.name}
        if self.url:
            result["url"] = self.url
        return result


# Factory function para crear entornos fácilmente
def environment(name: str, url: str | None = None) -> Environment:
    """Crea un Environment de manera conveniente."""
    return Environment(name=name, url=url)
