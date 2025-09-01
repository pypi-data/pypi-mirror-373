from pydantic import BaseModel, Field


class ColumnMap(BaseModel):
    """Column Map model."""

    name: str = Field(description="A new column name.")
    source: str = Field(
        description="A source column statement before alias with alias.",
    )
    allow_quote: bool = True

    def gen_source(self) -> str:
        """Generate source statement with quote flag."""
        return (
            f"{self.source} AS {self.name}"
            if self.allow_quote
            else f'"{self.source}" AS {self.name}'
        )
