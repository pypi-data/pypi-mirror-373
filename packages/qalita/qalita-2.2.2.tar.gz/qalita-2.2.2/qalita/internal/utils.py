"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import tarfile
import os
import json
import base64
import click

from qalita.internal.logger import init_logging

logger = init_logging()


def get_version():
    return "2.2.2"


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def ask_confirmation(message):
    """This function just asks for confirmation interactively from the user"""
    return click.confirm(message, default=False)


def validate_token(token: str):
    try:
        # Step 1: Split the token
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        # Step 2: Decode base64 (adding padding if necessary)
        payload_encoded = parts[1]
        missing_padding = len(payload_encoded) % 4
        if missing_padding:
            payload_encoded += "=" * (4 - missing_padding)

        payload_json = base64.urlsafe_b64decode(payload_encoded).decode("utf-8")

        # Step 3: Parse as JSON
        payload = json.loads(payload_json)

        # Step 4: Extract the user ID
        user_id = payload.get("sub")

        # Step 5: Check if role is "admin" or "dataengineer"
        role = payload.get("role")
        valid_roles = {"admin", "dataengineer"}
        has_valid_role = role in valid_roles

        # Step 6: Check if scopes contain required permissions
        required_scopes = {"agent.get", "pack.create", "source.create"}
        scopes = set(payload.get("scopes", []))
        has_required_scopes = required_scopes.issubset(scopes)

        return {
            "user_id": user_id,
            "role_valid": has_valid_role,
            "scopes_valid": has_required_scopes,
        }

    except Exception as e:
        return {"error": str(e)}


def test_connection(config, type_):
    """Test connectivity for a given source type. Returns True if OK, False otherwise."""
    try:
        if type_ in ["mysql"]:
            import pymysql
            conn = pymysql.connect(
                host=config["host"],
                port=int(config["port"]),
                user=config["username"],
                password=config["password"],
                database=config["database"],
                connect_timeout=5
            )
            conn.close()
        elif type_ in ["postgresql"]:
            import psycopg2
            conn = psycopg2.connect(
                host=config["host"],
                port=int(config["port"]),
                user=config["username"],
                password=config["password"],
                dbname=config["database"],
                connect_timeout=5
            )
            conn.close()
        elif type_ == "sqlite":
            import sqlite3
            conn = sqlite3.connect(config["file_path"], timeout=5)
            conn.close()
        elif type_ == "mongodb":
            from pymongo import MongoClient
            uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.server_info()
        elif type_ == "s3":
            import boto3
            s3 = boto3.client(
                's3',
                aws_access_key_id=config["access_key"],
                aws_secret_access_key=config["secret_key"],
                region_name=config["region"]
            )
            s3.head_bucket(Bucket=config["bucket"])
        elif type_ == "gcs":
            from google.cloud import storage
            client = storage.Client.from_service_account_json(config["credentials_json"])
            bucket = client.get_bucket(config["bucket"])
            # Optionally check prefix exists
        elif type_ == "azure_blob":
            from azure.storage.blob import BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string(config["connection_string"])
            container_client = blob_service_client.get_container_client(config["container"])
            container_client.get_container_properties()
        elif type_ == "hdfs":
            from hdfs import InsecureClient
            url = f"http://{config['namenode_host']}:{config['port']}"
            client = InsecureClient(url, user=config["user"])
            client.status(config["path"], strict=False)
        elif type_ == "folder":
            if not os.path.isdir(config["path"]):
                raise Exception(f"Folder {config['path']} not found")
            if not os.access(config["path"], os.R_OK):
                raise Exception(f"No read access to folder {config['path']}")
        elif type_ == "oracle":
            # Use python-oracledb in thin mode (no Instant Client required)
            import oracledb
            conn = oracledb.connect(
                user=config["username"],
                password=config["password"],
                host=config["host"],
                port=int(config["port"]),
                service_name=config["database"],
            )
            conn.close()
        # FTP support removed for security reasons
        elif type_ == "file":
            if not os.path.isfile(config["path"]):
                raise Exception(f"File {config['path']} not found")
            if not os.access(config["path"], os.R_OK):
                raise Exception(f"No read access to file {config['path']}")
        else:
            logger.warning(f"Connection test not implemented for type {type_}")
            return None
        return True
    except Exception as e:
        logger.error(f"Connection test failed for type {type_}: {e}")
        return False
