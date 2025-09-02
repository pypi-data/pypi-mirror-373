import io
import json
import mimetypes
import os
import pickle
from typing import Any, Dict, Tuple

import pandas as pd


from ..._resource import SyncAPIResource


__all__ = ["Upload"]


class Upload(SyncAPIResource):

    def artifact_file(
        self,
        path_to_file: str,
        project_id: str,
        component_id: str,
        file_name: str = "",
        description: str = "",
    ):
        """Register an artifact on the Modulos platform.

        Args:
            path_to_file (str): The path to the file.
            project_id (str): The project ID.
            component_id (str): The component ID.
            file_name (str, optional): The name of the file. If it is an empty string,
            it will take name of the given file. Defaults to "".
            description (str, optional): The description of the file. Defaults to "".
        """

        with open(path_to_file, "rb") as f:
            files = {
                "file": (
                    os.path.basename(path_to_file),
                    f,
                    mimetypes.guess_type(path_to_file)[0] or "application/octet-stream",
                )
            }

            self._post(
                f"/projects/{project_id}/evidence",
                url_params={
                    "component_id": component_id,
                    "file_name": file_name,
                    "description": description,
                },
                files=files,
            )
            # TODO: Handle response and return
            return None

    def artifact_result(
        self,
        result: pd.DataFrame | Dict[str, Any] | Any,
        file_name: str,
        project_id: str,
        component_id: str,
        description: str = "",
    ):
        """Register an artifact on the Modulos platform. It is uploaded as a file using
        the given name. The file type is determined by the file extension if possible.

        Args:
            result (pd.DataFrame | Dict[str, Any] | str | Any): The result.
            filename (str): The name of the result.
            project_id (str): The project ID.
            component_id (str): The component ID.
            description (str, optional): The description of the file. Defaults to "".
        """

        mimetype = mimetypes.guess_type(file_name)[0]

        if mimetype == "text/csv":
            if isinstance(result, pd.DataFrame):
                str_buffer = io.StringIO()
                result.to_csv(str_buffer, index=False)
                str_buffer.seek(0)
                file: Dict[str, Tuple[str, io.StringIO | io.BytesIO, str]] = {
                    "file": (
                        file_name,
                        str_buffer,
                        mimetype,
                    )
                }
            elif isinstance(result, dict):
                try:
                    result_json = json.dumps(result)
                except Exception:
                    raise Exception("Could not convert result to JSON.")
                df = pd.read_json(result_json)
                str_buffer = io.StringIO()
                df.to_csv(str_buffer, index=False)
                str_buffer.seek(0)
                file = {
                    "file": (
                        file_name,
                        str_buffer,
                        mimetype,
                    )
                }
            else:
                raise Exception(
                    "Result must be a pandas DataFrame or a dict if it saved as a CSV "
                    "file."
                )
        elif mimetype == "application/json":
            if isinstance(result, dict):
                try:
                    result_json = json.dumps(result)
                except Exception:
                    raise Exception("Could not convert result to JSON.")
                str_buffer = io.StringIO()
                str_buffer.write(result_json)
                str_buffer.seek(0)
                file = {
                    "file": (
                        file_name,
                        str_buffer,
                        mimetype,
                    )
                }
            elif isinstance(result, pd.DataFrame):
                try:
                    result_json = result.to_json()
                except Exception:
                    raise Exception("Could not convert result to JSON.")
                str_buffer = io.StringIO()
                str_buffer.write(result_json)
                str_buffer.seek(0)
                file = {
                    "file": (
                        file_name,
                        str_buffer,
                        mimetype,
                    )
                }
            else:
                raise Exception(
                    "Result must be a pandas DataFrame or a dict if it saved as a JSON "
                    "file."
                )
        elif mimetype == "text/plain":
            if isinstance(result, str):
                str_buffer = io.StringIO()
                str_buffer.write(result)
                str_buffer.seek(0)
                file = {
                    "file": (
                        file_name,
                        str_buffer,
                        mimetype,
                    )
                }
            else:
                raise Exception("Result must be a string if it saved as a text file.")
        else:
            if file_name.endswith(".pkl"):
                byte_buffer = io.BytesIO()
                pickle.dump(result, byte_buffer)
                byte_buffer.seek(0)
                file = {
                    "file": (
                        file_name,
                        byte_buffer,
                        "application/octet-stream",
                    )
                }
            else:
                raise Exception(
                    "Result can be saved as a csv, text file or json file. "
                    "If that is not possible, use a <name>.pkl as filename "
                    "and the result is saved as pickle file."
                )

        self._post(
            f"/projects/{project_id}/evidence",
            url_params={
                "component_id": component_id,
                "file_name": file_name,
                "description": description,
            },
            files=file,
        )
        # TODO: Handle response and return
        return None
