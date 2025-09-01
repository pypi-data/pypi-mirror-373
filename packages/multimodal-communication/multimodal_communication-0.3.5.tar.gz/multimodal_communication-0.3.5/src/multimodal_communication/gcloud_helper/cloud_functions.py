import os
import pandas as pd
import polars as pl
import json
import pickle as pkl
import warnings
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = os.getenv("GCLOUD_PROJECT_ID")


class CloudHelper:
    """
    A class to more easily upload, download, and delete files from Google Cloud. Only to be used by the user of the computer,
    as credentials are tied to the computer user as explained below:

    When interacting with Google Cloud Client libraries, the library can auto-detect the
    credentials to use. Make sure the ADC credentials are downloaded on the personal device as outlined below

    //  set up ADC as described in https://cloud.google.com/docs/authentication/external/set-up-adc
    //  2. Replace the project variable.
    //  3. Make sure that the user account or service account that you are using
    //  has the required permissions. For this sample, you must have "storage.buckets.list".
    """

    def __init__(self, obj=None, path=None, project_id=PROJECT_ID):
        if obj is not None and path is not None:
            raise ValueError(
                "Only one of 'obj' or 'path' should be provided, not both."
            )

        if not project_id:
            raise ValueError("A valid 'project_id' must be provided.")

        self.obj = obj
        self.path = path
        self.project_id = project_id
        self.storage_client = storage.Client(project=self.project_id)

    def _get_bucket(self, bucket_name):
        return self.storage_client.bucket(bucket_name)

    def _infer_file_type(self, file_name):
        ext = os.path.splitext(file_name)[1].lower()
        return {
            ".csv": "csv",
            ".json": "json",
            ".pkl": "pickle",
            ".pickle": "pickle",
            ".parquet": "parquet",
            ".pq": "parquet",
            ".txt": "txt",
        }.get(ext, None)

    def upload_to_cloud(self, bucket_name, file_name, file_type=None):
        if file_type is None:
            file_type = self._infer_file_type(file_name)
            if file_type is None:
                raise ValueError(f"Cannot infer file_type from filename: {file_name}")

        bucket = self._get_bucket(bucket_name)
        blob = bucket.blob(file_name)

        if self.path:
            blob.upload_from_filename(self.path)
        elif self.obj is not None:
            from io import BytesIO

            if file_type == "csv":
                if isinstance(self.obj, pd.DataFrame):
                    csv_data = self.obj.to_csv(index=False)
                elif isinstance(self.obj, pl.DataFrame):
                    csv_data = self.obj.write_csv(include_header=True)
                else:
                    raise ValueError(
                        "Only pandas or polars DataFrames supported for CSV."
                    )
                blob.upload_from_string(csv_data, content_type="text/csv")

            elif file_type == "pickle":
                blob.upload_from_string(
                    pkl.dumps(self.obj), content_type="application/octet-stream"
                )

            elif file_type == "parquet":
                buffer = BytesIO()
                if isinstance(self.obj, pd.DataFrame):
                    self.obj.to_parquet(buffer, index=False)
                elif isinstance(self.obj, pl.DataFrame):
                    self.obj.write_parquet(buffer)
                else:
                    raise ValueError(
                        "Only pandas or polars DataFrames supported for Parquet."
                    )
                buffer.seek(0)
                blob.upload_from_file(buffer, content_type="application/octet-stream")

            elif file_type == "txt" and isinstance(self.obj, str):
                blob.upload_from_string(self.obj, content_type="text/plain")

            elif file_type == "json":
                if not isinstance(self.obj, dict):
                    raise ValueError(
                        "For JSON uploads, `self.obj` must be a dictionary"
                    )
                json_str = json.dumps(self.obj, indent=2)
                blob.upload_from_string(json_str, content_type="application/json")

            else:
                raise ValueError(
                    f"Unsupported combination of file_type='{file_type}' and object type."
                )
        else:
            raise ValueError("Either 'path' or 'obj' must be set.")

    def download_from_cloud(
        self, gs_filepath, file_type=None, use_polars: bool = False
    ):
        """
        Downloads file from cloud. Tries to infer file type if not specified.
        Set use_polars=True to return a polars.DataFrame instead of pandas.
        """
        if not gs_filepath.startswith("gs://"):
            gs_filepath = "gs://" + gs_filepath

        try:
            bucket_name, *blob_path = gs_filepath.replace("gs://", "").split("/", 1)
            blob_path = blob_path[0]
            bucket = self._get_bucket(bucket_name)
            blob = bucket.blob(blob_path)

            if not blob.exists():
                warnings.warn(
                    f"File not found @ {gs_filepath}. Returning empty DataFrame."
                )
                return pl.DataFrame() if use_polars else pd.DataFrame()

            if file_type is None:
                file_type = self._infer_file_type(blob_path)

            data = blob.download_as_bytes()
            from io import BytesIO

            if file_type == "csv":
                if use_polars:
                    return pl.read_csv(BytesIO(data))
                return pd.read_csv(BytesIO(data))

            elif file_type == "pickle":
                return pkl.loads(data)

            elif file_type == "parquet":
                if use_polars:
                    return pl.read_parquet(BytesIO(data))
                return pd.read_parquet(BytesIO(data))

            elif file_type == "txt":
                return data.decode("utf-8")

            elif file_type == "json":
                text = data.decode("utf-8")
                return json.loads(text)

            else:
                raise ValueError(
                    f"Unsupported or unspecified file type for download: '{file_type}'"
                )
        except Exception as e:
            warnings.warn(f"Error downloading file: {e}. Returning empty DataFrame.")
            return pl.DataFrame() if use_polars else pd.DataFrame()

    def delete_from_cloud(self, bucket_name, file_name):
        bucket = self._get_bucket(bucket_name)
        blob = bucket.blob(file_name)
        if blob.exists():
            blob.delete()
        else:
            warnings.warn(
                f"No such file '{file_name}' found in bucket '{bucket_name}'."
            )
