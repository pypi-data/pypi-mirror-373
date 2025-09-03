from enum import StrEnum
from typing import Optional, List, Literal

from pydantic import BaseModel, ConfigDict, Field, constr


class FileType(StrEnum):
    """Enumeration of the file types for the input files.

    Attributes:
        STAT_VAR_PER_COLUMN: Variable per column file type.
        STAT_VAR_PER_ROW: Variable per row file type.
    """

    STAT_VAR_PER_COLUMN = "variablePerColumn"
    STAT_VAR_PER_ROW = "variablePerRow"


class MCFFileName(BaseModel):
    file_name: constr(strip_whitespace=True, pattern=r".*\.mcf$")


class ObservationProperties(BaseModel):
    """Representation of the ObservationProperties section of the InputFiles section of the config file
    This is for the implicit schema only.

    Attributes:
        unit: Unit of the observation.
        observationPeriod: Observation period of the data.
        scalingFactor: Scaling factor for the data.
        measurementMethod: Measurement method used for the data.
    """

    unit: Optional[str] = None
    observationPeriod: Optional[str] = None
    scalingFactor: Optional[str] = None
    measurementMethod: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class ColumnMappings(BaseModel):
    """Representation of the ColumnMappings section of the InputFiles section of the config file
    This is for explicit schema only

    Attributes:
        variable: Variable name.
        entity: Entity name.
        date: Date of the observation.
        value: Value of the observation.
        unit: Unit of the observation.
        scalingFactor: Scaling factor for the data.
        measurementMethod: Measurement method used for the data.
        observationPeriod: Observation period of the data.
    """

    variable: Optional[str] = None
    entity: Optional[str] = None
    date: Optional[str] = None
    value: Optional[str] = None
    unit: Optional[str] = None
    scalingFactor: Optional[str] = None
    measurementMethod: Optional[str] = None
    observationPeriod: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class InputFile(BaseModel):
    """Representation of the InputFiles section of the config file

    Attributes:
        provenance: Provenance of the data.
        ignoreColumns: List of columns to ignore.
    """

    provenance: str
    ignoreColumns: Optional[List[str]] = None
    # Allow since inherited classes will have extra fields
    model_config = ConfigDict(extra="allow")
    data_format: FileType = Field(..., alias="format")


class ImplicitSchemaFile(InputFile):
    """Representation of the ColumnFile section of the config file
    This is what is known as the implicit schema.

    Attributes:
        entityType: Type of the entity (e.g., Country, State).
        observationProperties: Properties of the observation.
        # Inherited from InputFile
        provenance: Provenance of the data.
        ignoreColumns: List of columns to ignore.
        # Automatically set
        data_format: Format of the data (variable per column).
            This attribute is represented as "format" in the JSON.

    """

    entityType: str
    observationProperties: ObservationProperties
    data_format: Literal["variablePerColumn"] = Field(
        default="variablePerColumn", alias="format"
    )


class ExplicitSchemaFile(InputFile):
    """Representation of the RowFile section of the config file
    This is what is known as the explicit schema.

    Attributes:

        columnMappings:  If headings in the CSV file does not use the default names,
             the equivalent names for each column. (explicit schema only).

        # Inherited from InputFile
        provenance: Provenance of the data.
        ignoreColumns: List of columns to ignore.
        # Automatically set
        data_format: Format of the data (variable per row).
            This attribute is represented as "format" in the JSON.
    """

    columnMappings: ColumnMappings
    data_format: Literal["variablePerRow"] = Field(
        default="variablePerRow", alias="format"
    )
