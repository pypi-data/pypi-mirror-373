import logging
import os
from pathlib import Path
from typing import Any
from pydantic import BaseModel


# -----------------------------------------------------------------------------
# Metadata models (Job Type)
# -----------------------------------------------------------------------------


class IMetadataModel(BaseModel):
    """Metadata for a transformation."""

    def get_input_query(
        self, input_name: str, **kwargs: Any
    ) -> Path | list[Path] | None:
        """
        Template method for getting the input path where the inputs of a job are stored.
        Should be overridden by subclasses.
        """
        return None

    def get_output_query(self, output_name: str) -> Path | None:
        """
        Template method for getting the output path to store results of a job.
        Should be overridden by subclasses.
        """
        return None

    def pre_process(self, job_path: Path, command: list[str]) -> list[str]:
        """
        Template method for process the inputs of a job.
        Should be overriden by subclasses.
        """
        return command

    def post_process(self, job_path: Path):
        """
        Template method for processing the outputs of a job.
        Should be overridden by subclasses.
        """
        pass

    def _store_output(self, output_name: str, src: str):
        """Store the output in the "filecatalog" directory."""
        # Get the output query
        output_path = self.get_output_query(output_name)
        if not output_path:
            raise RuntimeError("No output path defined.")
        output_path.mkdir(exist_ok=True, parents=True)

        # Send the output to the file catalog
        output_value = Path(src).name
        dest = output_path / output_value
        os.rename(src, dest)
        logging.info(f"Output stored in {dest}")


# -----------------------------------------------------------------------------


class TaskWithMetadataQuery(IMetadataModel):
    """
    TaskWithMetadataQuery is a class providing methods to query metadata and generate input paths based on the metadata.

    Methods
    -------
    get_input_query(**kwargs) -> Path | list[Path] | None
        Generates a query to retrieve input paths based on provided metadata.

    Example
    -------
    >>> query = TaskWithMetadataQuery()
    >>> input_path = query.get_input_query(site="LaPalma", campaign="PROD6")
    >>> print(input_path)
    [PosixPath('filecatalog/PROD6/LaPalma')]

    Attributes
    ----------
    Inherits attributes from IMetadataModel.
    """

    def get_input_query(
        self, input_name: str, **kwargs: Any
    ) -> Path | list[Path] | None:
        """
        Generates a query to retrieve input paths based on provided metadata.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments representing metadata attributes. Expected keys are:
            - site (str): The site name.
            - campaign (str): The campaign name.

        Returns
        -------
        Path | list[Path] | None
            A Path or list of Paths representing the input query based on the provided metadata.
            Returns None if neither site nor campaign is provided.

        Notes
        -----
        This is an example implementation. In a real implementation,
        an actual query should be made to the metadata service,
        resulting in an array of Logical File Names (LFNs) being returned.
        """
        site = kwargs.get("site", "")
        campaign = kwargs.get("campaign", "")

        # Example implementation
        if site and campaign:
            return [Path("filecatalog") / campaign / site]
        elif site:
            return Path("filecatalog") / site
        else:
            return None


# -----------------------------------------------------------------------------


class User(IMetadataModel):
    """User metadata model: does nothing."""
