import os
import pandas as pd
import polars as pl
import numpy as np
import json
import pickle as pkl
import warnings
import boto3
from botocore.exceptions import ClientError
from typing import Union, Optional
from io import BytesIO
from dotenv import load_dotenv
from deltalake import DeltaTable, write_deltalake

# Load environment variables
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")


class S3CloudHelper:
    def __init__(
        self,
        obj: Union[pd.DataFrame, pl.DataFrame, dict, str, None] = None,
        path: str = None,
        region_name: str = AWS_REGION,
    ):
        if obj is not None and path is not None:
            raise ValueError(
                "Only one of 'obj' or 'path' should be provided, not both."
            )

        self.obj = obj
        self.path = path

        self.s3_client = boto3.client(
            "s3",
            region_name=region_name,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

    def _infer_file_type(self, file_name: str) -> Optional[str]:
        ext = os.path.splitext(file_name)[1].lower()
        return {
            ".csv": "csv",
            ".json": "json",
            ".pkl": "pickle",
            ".pickle": "pickle",
            ".parquet": "parquet",
            ".pq": "parquet",
            ".txt": "txt",
            "": None,
        }.get(ext, None)

    def upload_to_s3(
        self,
        bucket_name: str,
        file_name: str,
        file_type: str = None,
        use_delta: bool = False,
    ):
        if use_delta:
            if not isinstance(self.obj, (pd.DataFrame, pl.DataFrame)):
                raise ValueError(
                    "Delta upload only supports pandas or polars DataFrames."
                )

            if isinstance(self.obj, pl.DataFrame):
                df = self.obj.to_pandas()
            else:
                df = self.obj

            # Ensure no null columns before uploading to delta lake
            df = self._fix_null_columns(df)

            delta_path = f"s3://{bucket_name}/{file_name}"
            write_deltalake(
                delta_path,
                df,
                mode="overwrite",
                storage_options={"AWS_REGION": AWS_REGION},
            )
            return

        # Normal non-delta handling
        if file_type is None:
            file_type = self._infer_file_type(file_name)
            if file_type is None:
                raise ValueError(f"Cannot infer file_type from filename: {file_name}")

        if self.path:
            self.s3_client.upload_file(self.path, bucket_name, file_name)
            return

        if self.obj is not None:
            buffer = BytesIO()

            if file_type == "csv":
                if isinstance(self.obj, pd.DataFrame):
                    self.obj.to_csv(buffer, index=False)
                elif isinstance(self.obj, pl.DataFrame):
                    buffer.write(self.obj.write_csv().encode("utf-8"))
                buffer.seek(0)
                self.s3_client.upload_fileobj(buffer, bucket_name, file_name)

            elif file_type == "parquet":
                if isinstance(self.obj, pd.DataFrame):
                    self.obj.to_parquet(buffer, index=False)
                elif isinstance(self.obj, pl.DataFrame):
                    self.obj.write_parquet(buffer)
                buffer.seek(0)
                self.s3_client.upload_fileobj(buffer, bucket_name, file_name)

            elif file_type == "json":
                json_str = json.dumps(self.obj, indent=2)
                self.s3_client.put_object(
                    Body=json_str.encode("utf-8"), Bucket=bucket_name, Key=file_name
                )

            elif file_type in ("pickle", "pkl"):
                pkl.dump(self.obj, buffer)
                buffer.seek(0)
                self.s3_client.upload_fileobj(buffer, bucket_name, file_name)

            elif file_type == "txt":
                self.s3_client.put_object(
                    Body=self.obj.encode("utf-8"), Bucket=bucket_name, Key=file_name
                )
            else:
                raise ValueError(f"Unsupported file type {file_type}")

    def download_from_s3(
        self,
        s3_filepath: str,
        file_type: str = None,
        use_polars: bool = False,
        use_delta: bool = False,
    ):
        if use_delta:
            dt = DeltaTable(s3_filepath, storage_options={"AWS_REGION": AWS_REGION})
            return dt.to_pandas() if not use_polars else pl.from_pandas(dt.to_pandas())

        # Normal handling
        if s3_filepath.startswith("s3://"):
            s3_filepath = s3_filepath[5:]

        bucket_name, *blob_path = s3_filepath.split("/", 1)
        blob_path = blob_path[0]

        is_prefix = not any(
            blob_path.endswith(ext)
            for ext in [".csv", ".parquet", ".json", ".pkl", ".pickle", ".txt"]
        )

        if is_prefix:
            files = self.list_files(bucket=bucket_name, prefix=blob_path)
            if not files:
                return pl.DataFrame() if use_polars else pd.DataFrame()

            if use_polars:
                if file_type == "csv":
                    return pl.scan_csv(files)
                elif file_type == "parquet":
                    return pl.scan_parquet(files)
            else:
                raise ValueError("Lazy multi-file read only supported with Polars.")
        else:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=blob_path)
            data = response["Body"].read()
            buffer = BytesIO(data)

            if file_type is None:
                file_type = self._infer_file_type(blob_path)

            if file_type == "csv":
                return pl.read_csv(buffer) if use_polars else pd.read_csv(buffer)
            elif file_type == "parquet":
                return (
                    pl.read_parquet(buffer) if use_polars else pd.read_parquet(buffer)
                )
            elif file_type == "json":
                return json.loads(data.decode("utf-8"))
            elif file_type in ("pickle", "pkl"):
                return pkl.loads(data)
            elif file_type == "txt":
                return data.decode("utf-8")

    def upsert_to_s3(
        self,
        bucket_name: str,
        file_name: str,
        new_data: Union[pd.DataFrame, pl.DataFrame],
        use_delta: bool = True,
        partition_by: Optional[list[str]] = None,
        drop_duplicates_by: list[str] | None = None,
    ):
        """
        Upsert new_data into Delta Lake table on S3 at file_name.
        partition_by: columns to partition table by (e.g., ['league', 'season'])
        key_columns: columns used to identify duplicates for upsert (e.g., ['id'])

        NOTE:
        - new_data must be pandas or polars DataFrame.
        - If table exists, load metadata and perform merge on keys, else write new.
        """
        if not use_delta:
            raise ValueError("Upsert is only supported for Delta Lake tables.")

        if isinstance(new_data, pl.DataFrame):
            new_data = new_data.to_pandas()

        delta_path = f"s3://{bucket_name}/{file_name}"

        # Validate partition columns exist in new_data
        if partition_by:
            missing_partitions = [p for p in partition_by if p not in new_data.columns]
            if missing_partitions:
                raise ValueError(
                    f"Partition columns missing from data: {missing_partitions}"
                )

        # Check if Delta table exists
        if self._delta_table_exists(delta_path):
            # Load existing DeltaTable metadata
            dt = DeltaTable(delta_path, storage_options={"AWS_REGION": AWS_REGION})
            existing_df = dt.to_pandas()

            # Combine existing and new data, remove duplicates based on key_columns
            combined_df = pd.concat([existing_df, new_data], ignore_index=True)

            # Drop duplicates either by specific columns, or else all columns
            if drop_duplicates_by:
                combined_df = combined_df.drop_duplicates(
                    subset=drop_duplicates_by, keep="last"
                )
            else:
                combined_df = combined_df.drop_duplicates(keep="last")

            # Ensure no null columns
            combined_df = self._fix_null_columns(combined_df).reset_index(drop=True)

            # Overwrite Delta table with combined_df, partitioned
            write_deltalake(
                delta_path,
                combined_df,
                mode="overwrite",
                partition_by=partition_by,
                storage_options={"AWS_REGION": AWS_REGION},
            )
        else:
            # Ensure no null columns before uploading
            new_data = self._fix_null_columns(new_data)
            # Table does not exist: write new data directly, partitioned
            write_deltalake(
                delta_path,
                new_data,
                mode="overwrite",
                partition_by=partition_by,
                storage_options={"AWS_REGION": AWS_REGION},
            )

    def delete_from_s3(self, bucket_name: str, file_name: str) -> bool:
        """
        Deletes a single object or all objects under a given prefix from an S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            key_or_prefix (str): The key of a single object or a prefix (folder path)
                                 to delete. If it ends with '/', it's treated as a prefix.
                                 If it points to a Delta Lake table path, it will delete
                                 all files associated with that Delta table.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            # If it's a Delta Lake path, it typically means deleting the base folder
            # which includes _delta_log and data files.
            # We assume a Delta Lake path ends with a partition structure or just the table name.
            # E.g., 'my-delta-table/' or 'my-delta-table/part_col=val/'

            # Check if it looks like a Delta Lake table path (does not contain specific file extensions)
            is_delta_table_path = not any(
                file_name.endswith(ext)
                for ext in [".csv", ".parquet", ".json", ".pkl", ".pickle", ".txt"]
            ) and (file_name.endswith("/") or "/" in file_name)

            if is_delta_table_path and self._delta_table_exists(
                f"s3://{bucket_name}/{file_name}"
            ):
                # For Delta Lake tables, delete the entire directory
                print(
                    f"Attempting to delete Delta Lake table at: s3://{bucket_name}/{file_name}"
                )
                objects_to_delete = []
                paginator = self.s3_client.get_paginator("list_objects_v2")
                pages = paginator.paginate(Bucket=bucket_name, Prefix=file_name)
                for page in pages:
                    if "Contents" in page:
                        for obj in page["Contents"]:
                            objects_to_delete.append({"Key": obj["Key"]})

                if objects_to_delete:
                    # S3 delete_objects can take up to 1000 keys at once
                    for i in range(0, len(objects_to_delete), 1000):
                        batch = objects_to_delete[i : i + 1000]
                        self.s3_client.delete_objects(
                            Bucket=bucket_name, Delete={"Objects": batch, "Quiet": True}
                        )
                    print(
                        f"Successfully deleted Delta Lake table objects under prefix: {file_name}"
                    )
                    return True
                else:
                    print(
                        f"No objects found to delete for Delta Lake table at: {file_name}"
                    )
                    return False

            elif file_name.endswith("/"):
                # If it's a prefix (folder), list and delete all objects under it
                print(f"Attempting to delete all objects under prefix: {file_name}")
                objects_to_delete = []
                paginator = self.s3_client.get_paginator("list_objects_v2")
                pages = paginator.paginate(Bucket=bucket_name, Prefix=file_name)
                for page in pages:
                    if "Contents" in page:
                        for obj in page["Contents"]:
                            objects_to_delete.append({"Key": obj["Key"]})

                if objects_to_delete:
                    for i in range(0, len(objects_to_delete), 1000):
                        batch = objects_to_delete[i : i + 1000]
                        self.s3_client.delete_objects(
                            Bucket=bucket_name, Delete={"Objects": batch, "Quiet": True}
                        )
                    print(f"Successfully deleted all objects under prefix: {file_name}")
                    return True
                else:
                    print(f"No objects found to delete under prefix: {file_name}")
                    return False
            else:
                # If it's a single key (file), delete it directly
                print(f"Attempting to delete single object: {file_name}")
                self.s3_client.delete_object(Bucket=bucket_name, Key=file_name)
                print(f"Successfully deleted single object: {file_name}")
                return True

        except ClientError as e:
            warnings.warn(f"Failed to delete S3 object(s) or prefix '{file_name}': {e}")
            return False

    def list_files(self, bucket: str, prefix: str) -> list[str]:
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            return [
                f"s3://{bucket}/{obj['Key']}"
                for obj in response.get("Contents", [])
                if not obj["Key"].endswith("/")
            ]
        except ClientError as e:
            warnings.warn(
                f"Failed to list files in bucket '{bucket}' with prefix '{prefix}': {e}"
            )
            return []

    def _delta_table_exists(self, s3_path: str) -> bool:
        """
        Quick check: look for the _delta_log/ folder in the Delta table path on S3.
        """
        if s3_path.startswith("s3://"):
            s3_path = s3_path[5:]

        bucket, *key_parts = s3_path.split("/", 1)
        prefix = key_parts[0] if key_parts else ""

        # Remove trailing slash from prefix if present (to avoid double slashes)
        prefix = prefix.rstrip("/")

        s3 = boto3.client("s3", region_name=AWS_REGION)
        try:
            # Try both _delta_log/ and _delta_log (without trailing slash)
            for delta_log_prefix in [f"{prefix}/_delta_log/", f"{prefix}/_delta_log"]:
                response = s3.list_objects_v2(
                    Bucket=bucket,
                    Prefix=delta_log_prefix,
                    MaxKeys=1,
                )
                if "Contents" in response and len(response["Contents"]) > 0:
                    return True

            # If neither found, return False
            return False

        except ClientError:
            return False

    def _fix_null_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        new_dtypes = {}
        for col in df.columns:
            # If the entire column is null
            if df[col].isna().all():
                # Default to float to be safe
                new_dtypes[col] = np.float64
        if new_dtypes:
            df = df.astype(new_dtypes)
        return df
