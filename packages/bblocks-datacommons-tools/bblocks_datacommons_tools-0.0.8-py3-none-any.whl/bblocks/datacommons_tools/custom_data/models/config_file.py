from typing import Optional, Dict, Annotated

from pydantic import BaseModel, ConfigDict, model_validator, Field

from bblocks.datacommons_tools.custom_data.models.data_files import (
    ImplicitSchemaFile,
    ExplicitSchemaFile,
)
from bblocks.datacommons_tools.custom_data.models.sources import Source
from bblocks.datacommons_tools.custom_data.models.stat_vars import Variable


class Config(BaseModel):
    """Representation of the config file

    Attributes:
        includeInputSubdirs: Include input subdirectories.
        groupStatVarsByProperty: Group stat vars by property.
        inputFiles: Dictionary of input files.
        variables: Dictionary of variables.
        sources: Dictionary of sources.
    """

    includeInputSubdirs: Optional[bool] = None
    groupStatVarsByProperty: Optional[bool] = None
    inputFiles: Dict[
        str,
        Annotated[
            ImplicitSchemaFile | ExplicitSchemaFile, Field(discriminator="data_format")
        ],
    ]
    variables: Optional[Dict[str, Variable]] = None  # optional section
    sources: Dict[str, Source]

    # model configuration - to allow for extra fields and to populate by name
    # (for the "format" field) and forbid extra fields
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    @model_validator(mode="after")
    def validate_input_file_keys_are_csv(self) -> "Config":
        """Validate that all input file keys are .csv files"""

        for key in self.inputFiles:
            if not key.lower().endswith(".csv"):
                raise ValueError(f'Input file key "{key}" must be a .csv file name')
        return self

    @model_validator(mode="after")
    def validate_provenance_in_sources(self) -> "Config":
        """Validate that all input file provenances are in the sources section"""

        known_provenances = set()
        for source in self.sources.values():
            known_provenances.update(source.provenances.keys())

        # Validate that each InputFile provenance is among them
        for file_key, input_file in self.inputFiles.items():
            if input_file.provenance not in known_provenances:
                raise ValueError(
                    f'Input file "{file_key}" references unknown provenance "{input_file.provenance}".'
                )

        return self

    def validate_config(self) -> None:
        """Validate the config"""
        Config.model_validate(self.model_dump())

    @classmethod
    def from_json(cls, file_path: str) -> "Config":
        """Read the config from a JSON file

        Args:
            file_path: Path to the JSON file.

        Returns:
            Config: The config object.
        """

        with open(file_path, "r") as f:
            data = f.read()
        return cls.model_validate_json(data)
