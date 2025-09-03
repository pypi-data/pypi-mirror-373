from __future__ import annotations

import getpass
import json
import os
import re
from datetime import datetime
from os import PathLike
from typing import Dict, Tuple

import pandas as pd
import pyproj
from pandas._typing import ReadCsvBuffer

from baec.coordinates import CoordinateReferenceSystems
from baec.measurements.measurement_device import MeasurementDevice
from baec.measurements.settlement_rod_measurement import (
    SettlementRodMeasurement,
    StatusMessage,
    StatusMessageLevel,
)
from baec.measurements.settlement_rod_measurement_series import (
    SettlementRodMeasurementSeries,
)
from baec.project import Project

try:
    import boto3
    from botocore import exceptions
except ImportError as e:
    raise ImportError(
        "Please make sure that you installed baec with the correct extension. "
        f"Use pip install baec[aws] to use this model. {e}"
    )


class Credentials:
    def __init__(
        self,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
    ) -> None:
        """
        Credentials needs to refer to the AWS credential file given by Basetime.

        Parameters
        ----------
        aws_access_key_id: str, optional
            The access key to use when creating the client.This is entirely optional, and if not provided,
            the credentials configured for the session will automatically be used. You only need to provide
            this argument if you want to override the credentials used for this specific client.
        aws_secret_access_key: : str, optional
            The secret key to use when creating the client.  Same semantics as aws_access_key_id above.
        """
        if aws_access_key_id is None:
            if "BASETIME_KEY_ID" not in os.environ:
                self.aws_access_key_id = input(
                    "Authentication is needed. What is your BaseTime key ID?"
                )
            else:
                self.aws_access_key_id = os.environ["BASETIME_KEY_ID"]
        else:
            self.aws_access_key_id = aws_access_key_id

        if aws_secret_access_key is None:
            if "BASETIME_ACCESS_KEY" not in os.environ:
                self.aws_secret_access_key = getpass.getpass("What is your access key?")
            else:
                self.aws_secret_access_key = os.environ["BASETIME_ACCESS_KEY"]
        else:
            self.aws_secret_access_key = aws_secret_access_key

    @classmethod
    def from_csv(
        cls,
        filepath_or_buffer: (
            str | PathLike[str] | ReadCsvBuffer[bytes] | ReadCsvBuffer[str]
        ),
    ) -> "Credentials":
        """
        Any valid string path is acceptable. Credentials needs to refer to the AWS credential file given by Basetime.

        Parameters
        ----------
        filepath_or_buffer: filepath_or_buffer: str | PathLike[str] | ReadCsvBuffer[bytes] | ReadCsvBuffer[str]

        Returns
        -------
        Credentials

        Raises
        ------
        ValueError/ClientError
            If the provided credential file does not contain the correct credentials.
            If the wrong type of value is given for the credential file.
        TypeError
            If the credential file does not contain credentials.
        ValueError
            If the list of measurements is empty.
            If the measurements are not for the same project, device or object.
        IOError
            If ZBASE file cannot be parsed by Pandas
        FileNotFoundError
            If filepath_or_buffer is requested but doesn't exist.

        """
        # Read the credentials file
        try:
            dict_credentials = pd.read_csv(filepath_or_buffer).to_dict("records")[0]
        except pd.errors.ParserError as e:
            raise IOError(
                f"Errors encountered while parsing contents of the credentials file: \n {e}"
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(e)
        except ValueError:
            raise ValueError(
                "Wrong type of credentials file given, str | PathLike[str] | ReadCsvBuffer[bytes] | "
                "ReadCsvBuffer[str], Any valid string path is acceptable."
            )
        return cls(
            dict_credentials["Access key ID"], dict_credentials["Secret access key"]
        )


class BaseTimeBucket:
    """
    Class object to get a list of projects and Point IDs or to import measurements as a SettlementRodMeasurementSeries.
    """

    def __init__(
        self,
        credentials: Credentials,
    ):
        """
        Initializes a ProjectsIDs object.

        Parameters
        ----------
        credentials : str | PathLike[str] | ReadCsvBuffer[bytes] | ReadCsvBuffer[str]
            Any valid string path is acceptable. Credentials needs to refer to the AWS credential file given by Basetime.

        Returns
        -------
        ProjectsIDs

        Raises
        ------
        ValueError/ClientError
            If the provided credential file does not contain the correct credentials.
            If the wrong type of value is given for the credential file.
        TypeError
            If the input types are incorrect.
            If the credential file does not contain credentials.
        ValueError
            If the list of measurements is empty.
            If the measurements are not for the same project, device or object.
        IOError
            If ZBASE file cannot be parsed by Pandas
        FileNotFoundError
            If filepath_or_buffer is requested but doesn't exist.
        """

        # Create boto3 client and resource for connecting to AWS S3
        s3c = boto3.client(
            service_name="s3",
            region_name="eu-west-1",
            aws_access_key_id=credentials.aws_access_key_id,
            aws_secret_access_key=credentials.aws_secret_access_key,
        )
        s3r = boto3.resource(
            service_name="s3",
            region_name="eu-west-1",
            aws_access_key_id=credentials.aws_access_key_id,
            aws_secret_access_key=credentials.aws_secret_access_key,
        )

        # Create boto3 client for using the lamdba functions
        lambda_client = boto3.client(
            service_name="lambda",
            region_name="eu-west-1",
            aws_access_key_id=credentials.aws_access_key_id,
            aws_secret_access_key=credentials.aws_secret_access_key,
        )

        # Create the dictionary to translate the error codes. Get the error_codes file from the AWS S3 bucket
        dict_errors = {}
        try:
            for line in (
                s3r.Object("basetime-general", "error_codes.txt")
                .get()["Body"]
                .read()
                .decode("utf-8")
                .split("\n")
            ):
                error_line = line.split(",")
                dict_errors[int(error_line[0])] = {
                    "basetime error": error_line[1],
                    "description": error_line[2],
                    "status message level": error_line[3],
                }
        except exceptions.ClientError:
            raise ValueError(
                "The AWS Access Key ID you provided does not exist in our records."
            )

        # Initialize all attributes
        self.s3c = s3c
        self.s3r = s3r
        self.credentials = credentials
        self.lambda_c = lambda_client
        self.dict_errors = dict_errors
        self.dic_projects = self.get_users_projects_ids()
        self._settlement_cache: Dict[
            Tuple[str, str], SettlementRodMeasurementSeries
        ] = {}

    def get_users_projects_ids(self) -> Dict:
        """
        Call Lambda function in the Basetime AWS environment, to get the projets and point ID's of the objects the
        user is allow to get.
        Return the dictionary containing every User as a key, then the Project as key, the value is a list of all the Point IDs.
        - Company/user
            - projects
                - point IDs
        """

        function_name = "api-gateway-project_get"
        payload = {
            "headers": {
                "Authorization": self.credentials.aws_access_key_id
                + ","
                + self.credentials.aws_secret_access_key
            }
        }

        response = self.lambda_c.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )

        response_ids = json.loads(response["Payload"].read())
        try:
            self.dic_projects = json.loads(response_ids["body"])
        except KeyError:
            raise KeyError(
                "Credentials are not registrated. Contact Basetime to grant access to the projects."
            )
        return self.dic_projects

    def make_settlement_rod_measurement_series(
        self, project: str, rod_id: str
    ) -> SettlementRodMeasurementSeries:
        """
        Make a SettlementRodMeasurementSeries:

        Initialize by checking if the values are inside the S3 environment of Basetime, by using variable [dic_projects].
        Iterate through all the folders in the S3 environment. The environment has the following folder structure:
        - Company uuid
            - Folders with project uuids
                - Files of point uuids
                    - Each file contans a full history of all the measurements of the point uuid.
                    - Everytime a customers generates a new point uuid, a new file will be created.

        SettlementRodMeasurement creating:
            - Split Basetime EPSG code to list of EPSG numbers to add to CoordinateReferenceSystems
            - Split error codes into multiple StatusMessage classes
            - Add all values to the SettlementRodMeasurement class
        """

        if (
            project,
            rod_id,
        ) in self._settlement_cache:
            return self._settlement_cache[
                (
                    project,
                    rod_id,
                )
            ]

        if project in self.dic_projects and rod_id in self.dic_projects[project]:
            list_SettlementRodMeasurement = []

            function_name = "api-gateway-get-data"

            payload = {
                "headers": {
                    "Authorization": self.credentials.aws_access_key_id
                    + ","
                    + self.credentials.aws_secret_access_key,
                    "Project": project,
                    "Point_ID": rod_id,
                }
            }

            response = self.lambda_c.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )
            response_payload = json.loads(response["Payload"].read())

            try:
                measurement_serie = json.loads(response_payload["body"])
            except KeyError:
                raise KeyError(
                    "Credentials missing for this Rod ID. Contact Basetime to grant access to the project."
                )
            if "Invalid request" in measurement_serie:
                raise KeyError("missing headers: Authorization, Projects, Point_ID")

            list_epsg_codes = self.convert_epsg_string_to_list_int(
                measurement_serie["Coordinate projection"]
            )

            coordinate_reference_systems = (
                CoordinateReferenceSystems(
                    pyproj.CRS.from_user_input(list_epsg_codes[0]),
                    (
                        pyproj.CRS.from_user_input(list_epsg_codes[1])
                        if len(list_epsg_codes) == 2
                        else (
                            pyproj.CRS.from_user_input(list_epsg_codes[0])
                            if len(list_epsg_codes) == 1
                            else None
                        )
                    ),
                )
                if list_epsg_codes
                else CoordinateReferenceSystems(None, None)
            )

            baec_project = Project(
                id_=measurement_serie["Project uuid"],
                name=measurement_serie["Project name"],
            )
            object_id = measurement_serie["Object ID"]

            for date_measurement in measurement_serie["Measurements"]:
                measurement = measurement_serie["Measurements"][date_measurement]

                if measurement["Error Codes"] in [" ", "[]"]:
                    status_messages = [
                        StatusMessage(
                            code=7000,
                            description="Measurement approved",
                            level=StatusMessageLevel.OK,
                        )
                    ]
                else:
                    try:
                        error_string_list = measurement["Error Codes"][1:-1].split(",")
                        error_integer_list = [int(num) for num in error_string_list]
                    except (ValueError, TypeError):
                        error_integer_list = [7000]
                    status_messages = [
                        StatusMessage(
                            code=error_code,
                            description=self.dict_errors[error_code]["description"],
                            level=(
                                StatusMessageLevel.INFO
                                if self.dict_errors[error_code]["status message level"]
                                == "INFO"
                                else (
                                    StatusMessageLevel.WARNING
                                    if self.dict_errors[error_code][
                                        "status message level"
                                    ]
                                    == "WARNING"
                                    else StatusMessageLevel.ERROR
                                )
                            ),
                        )
                        for error_code in error_integer_list
                        if self.dict_errors[error_code]["status message level"]
                        in ["OK", "INFO", "WARNING", "ERROR"]
                    ]

                if measurement_serie["Project type"] == "SettlementRods":
                    rod_bottom_z = measurement["Coordinates Soil"]["Height groundplate"]
                    ground_surface_z = measurement["Coordinates Soil"]["Height Soil"]
                else:
                    rod_bottom_z = float("nan")
                    ground_surface_z = float("nan")

                test_measurement = SettlementRodMeasurement(
                    project=baec_project,
                    device=MeasurementDevice(
                        id_=measurement["Device name"],
                        qr_code=measurement["QR-code"],
                    ),
                    object_id=object_id,
                    date_time=datetime.strptime(date_measurement, "%Y-%m-%dT%H:%M:%S"),
                    coordinate_reference_systems=coordinate_reference_systems,
                    rod_top_x=measurement["Coordinates Local"]["Easting"]
                    or float("nan"),
                    rod_top_y=measurement["Coordinates Local"]["Northing"]
                    or float("nan"),
                    rod_top_z=measurement["Coordinates Local"]["Height"]
                    or float("nan"),
                    rod_length=measurement["Vertical offset (meters)"] or float("nan"),
                    rod_bottom_z=rod_bottom_z or float("nan"),
                    ground_surface_z=ground_surface_z or float("nan"),
                    status_messages=status_messages,
                    temperature=measurement["Temperature (Celsius)"] or float("nan"),
                    voltage=measurement["Voltage Locator One (mV)"] or float("nan"),
                )

                list_SettlementRodMeasurement.append(test_measurement)

        elif project in self.dic_projects:
            raise ValueError(
                f"{project} is in the project list, but not rod_id: {rod_id}"
            )
        else:
            raise ValueError(f"{project} is not in the project list")

        if (
            project,
            rod_id,
        ) not in self._settlement_cache:
            self._settlement_cache[
                (
                    project,
                    rod_id,
                )
            ] = SettlementRodMeasurementSeries(list_SettlementRodMeasurement)
        return SettlementRodMeasurementSeries(list_SettlementRodMeasurement)

    @staticmethod
    def convert_epsg_string_to_list_int(epsg_string: str) -> list:
        """
        Converts a Basetime coordinate projection to a list of string containing the EPSG codes.

        Input: Basetime coordinate string (for example: "RDNAPTrans (28992,5709)")

        Output: list of EPSG numbers (for example: [28992,5709])

        If list has a length of 2, XY and Z projection are present.
        If the list has a length of 1, only the XY projection is present.
        If the list is empty, no projection could be transformed.
        """
        pattern = r"\((\d+)(?:,(\d+))?\)"
        matches = re.findall(pattern, epsg_string)

        if matches:
            if matches[0][1]:
                num1, num2 = map(int, matches[0])
                return [num1, num2]
            else:
                num1 = int(matches[0][0])
                return [num1]
        else:
            return []