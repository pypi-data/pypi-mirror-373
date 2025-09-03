"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import click
from tabulate import tabulate

from qalita.__main__ import pass_config
from qalita.internal.utils import logger, ask_confirmation, test_connection
from qalita.internal.request import send_api_request


@click.group()
@click.option("-s", "--source", type=int, help="Source ID")
@click.pass_context
def source(ctx, source):
    """Manage Qalita Platform Sources"""
    ctx.ensure_object(dict)
    ctx.obj["SOURCE"] = source


@source.command()
@pass_config
def list(config):
    """List sources that are accessible to the agent"""
    config.load_source_config()

    sources = []
    headers = [
        "ID",
        "Name",
        "Type",
        "Reference",
        "Sensitive",
        "Visibility",
        "Description",
        "Validity",
    ]

    for source in config.config["sources"]:
        sources.append(
            [
                source.get("id", ""),
                source.get("name", ""),
                source.get("type", ""),
                source.get("reference", ""),
                source.get("sensitive", ""),
                source.get("visibility", ""),
                source.get("description", ""),
                source.get("validate", ""),
            ]
        )

    print(tabulate(sources, headers, tablefmt="simple"))


def source_version(source):
    """Determine the source version.

    If the source type isn't specifically handled, fallback to 1.0.0.
    """
    version = "1.0.0"
    return version


@pass_config
def validate_source(config):
    """Validate a source configuration"""
    logger.info("------------- Source Validation -------------")
    config.load_source_config()
    agent_conf = config.load_agent_config()

    total_sources = 0
    error_count = 0

    source_names = []

    for i, source in enumerate(config.config["sources"]):
        total_sources += 1
        is_source_valid = True  # Assuming the source is valid initially

        # check for name
        if "name" not in source:
            logger.error(f"Source number [{total_sources}] has no name")
            is_source_valid = False

        # check for type
        if "type" not in source:
            logger.error(f"Source number [{total_sources}] has no type")
            is_source_valid = False

        # Check for duplicate names
        if source["name"] in source_names:
            logger.error(f"Duplicate source name: [{source['name']}]")
            is_source_valid = False
        else:
            source_names.append(source["name"])

        # check for description
        if "description" not in source:
            logger.warning(
                f"Source [{source['name']}] has no description, defaulting to empty string"
            )
            config.config["sources"][i]["description"] = ""

        # check for reference
        if "reference" not in source:
            logger.warning(
                f"Source [{source['name']}] has no reference status, defaulting to False"
            )
            config.config["sources"][i]["reference"] = False

        # check for Sensitive
        if "sensitive" not in source:
            logger.warning(
                f"Source [{source['name']}] has no sensitive status, defaulting to False"
            )
            config.config["sources"][i]["sensitive"] = False

        # check for visibility
        if "visibility" not in source:
            logger.warning(
                f"Source [{source['name']}] has no visibility status, defaulting to private"
            )
            config.config["sources"][i]["visibility"] = "private"

        # check type
        type_for_test = source["type"]
        if type_for_test == "database":
            type_for_test = source["config"].get("type", "database")
        if type_for_test in [
            "mysql", "postgresql", "sqlite", "mongodb", "oracle", "s3", "gcs", "azure_blob", "hdfs",  "file", "folder"
        ]:
            if not test_connection(source["config"], type_for_test):
                logger.error(f"Connection test failed for source [{source['name']}] of type {type_for_test}")
                is_source_valid = False
        elif source["type"] == "database":
            if "config" in source:
                for key, value in source["config"].items():
                    # If the value starts with '$', assume it's an environment variable
                    if str(value).startswith("$"):
                        env_var = value[1:]
                        # Get the value of the environment variable
                        env_value = os.getenv(env_var)
                        if env_value is None:
                            logger.warning(
                                f"The environment variable [{env_var}] for the source [{source['name']}] is not set"
                            )
                            is_source_valid = False
        elif source["type"] == "file":
            # check if config parameter is present
            if "config" not in source:
                logger.error(
                    f"Source [{source['name']}] is of type file but has no config"
                )
                is_source_valid = False
            else:
                # check for path in config
                if "path" not in source["config"]:
                    logger.error(
                        f"Source [{source['name']}] is of type file but has no path in config"
                    )
                    is_source_valid = False
                else:
                    # check for read access to path
                    path = source["config"]["path"]
                    if not os.access(path, os.R_OK):
                        logger.error(
                            f"Source [{source['name']}] has a path in config, but it cannot be accessed"
                        )
                        is_source_valid = False

        # If all checks pass, mark the source as valid
        if is_source_valid:
            source["validate"] = "valid"
            logger.success(f"Source [{source['name']}] validated")
        else:
            source["validate"] = "invalid"
            logger.error(f"Source [{source['name']}] is invalid")
            error_count += 1

    if error_count == 0:
        logger.success("All sources validated")
    else:
        logger.error(f"{error_count} out of {total_sources} sources are invalid")

    # Write the config file
    config.save_source_config()


def validate_source_object(config, source: dict, skip_connection: bool = False, exclude_name: str | None = None) -> bool:
    """Validate a single source object before persisting.

    - Ensures name/type present
    - Ensures name is unique among existing sources (exclude_name can be provided to ignore the current one)
    - Optionally tests connection for supported types (skip when data is incomplete)
    """
    is_valid = True

    # name/type presence
    if not source.get("name"):
        logger.error("Source has no name")
        is_valid = False
    if not source.get("type"):
        logger.error("Source has no type")
        is_valid = False

    # uniqueness
    if config and hasattr(config, "config"):
        if config.config is None:
            try:
                config.load_source_config()
            except Exception:
                pass
        existing = config.config.get("sources", []) if config.config else []
        for s in existing:
            if s.get("name") == source.get("name") and (exclude_name is None or s.get("name") != exclude_name):
                logger.error(f"Duplicate source name: [{source.get('name')}] already exists")
                is_valid = False
                break

    # connection test (optional)
    if not skip_connection:
        t = source.get("type")
        conf = source.get("config", {}) or {}
        type_for_test = t
        if t == "database":
            type_for_test = conf.get("type", "database")
        supported = [
            "mysql",
            "postgresql",
            "sqlite",
            "mongodb",
            "oracle",
            "s3",
            "gcs",
            "azure_blob",
            "hdfs",
            "file",
            "folder",
        ]
        if type_for_test in supported:
            if not test_connection(conf, type_for_test):
                logger.error(f"Connection test failed for source [{source.get('name')}] of type {type_for_test}")
                is_valid = False

    return is_valid


@source.command()
def validate():
    """Validate a source configuration"""
    validate_source()


@source.command()
@click.option(
    "--skip-validate",
    is_flag=True,
    default=False,
    envvar="QALITA_SKIP_VALIDATE",
    help="Skip validation of sources before pushing",
)
@pass_config
def push(config, skip_validate):
    """Publish a source to the Qalita Platform"""
    if not skip_validate:
        validate_source()
    else:
        logger.warning("Skipping source validation as requested.")
    logger.info("------------- Source Publishing -------------")
    logger.info("Publishing sources to the Qalita Platform...")

    invalid_count = 0  # To count failed publishing sources
    agent_conf = config.load_agent_config()
    config.load_source_config()

    if not config.config["sources"]:
        logger.warning("No sources to publish, add new sources > qalita source add")
        return

    if skip_validate:
        valid_source = len(config.config["sources"])
    else:
        valid_source = sum(
            1 for source in config.config["sources"] if source.get("validate") == "valid"
        )

    if valid_source == 0:
        logger.warning("No valid sources to publish")
        return

    r = send_api_request(
        request="/api/v2/sources",
        mode="get",
    )

    if r.status_code == 200:
        response_data = r.json()
        if not response_data:  # If response_data is an empty list
            logger.info("No sources found on the remote platform.")
            response_data = []  # Ensure it's always iterable
    else:
        raise

    for i, source in enumerate(config.config["sources"]):
        if skip_validate or source.get("validate") == "valid":
            logger.info(f"Processing source [{source['name']}] ...")

            # Find a matching source in response_data
            matched_source = next(
                (
                    s
                    for s in response_data
                    if s["name"] == source["name"] and s["type"] == source["type"]
                ),
                None,
            )

            if matched_source:
                # If source is already published, check for updates
                update_source = False

                if matched_source["versions"]:
                    if (
                        source_version(source)
                        == matched_source["versions"][0]["sem_ver_id"]
                    ):
                        if (
                            source["visibility"] == matched_source["visibility"]
                            and source["description"] == matched_source["description"]
                            and source["sensitive"] == matched_source["sensitive"]
                            and source["reference"] == matched_source["reference"]
                        ):
                            source_synced = False
                            if "id" in source and source["id"] == matched_source["id"]:
                                pass
                            else:
                                config.config["sources"][i]["id"] = matched_source["id"]
                                source_synced = True

                            if source_synced:
                                config.save_source_config()
                                logger.success(
                                    f"Source [{source['name']}] already published with id [{matched_source['id']}] synced with local config"
                                )
                            else:
                                logger.info(
                                    f"Source [{source['name']}] already published with id [{matched_source['id']}], no need to sync local config"
                                )
                        else:
                            update_source = True
                    else:
                        logger.info("Version mismatch")
                        update_source = True
                else:
                    logger.info("No version found")
                    update_source = True

                if update_source:
                    if source["visibility"] != matched_source["visibility"]:
                        if not ask_confirmation(
                            "Are you sure you want to publish a public source? Public sources are visible for partners. Be careful about what you share."
                        ):
                            continue

                    r = send_api_request(
                        request=f"/api/v2/sources/{matched_source['id']}",
                        mode="put",
                        data={
                            "description": source["description"],
                            "visibility": source["visibility"],
                            "sensitive": source["sensitive"],
                            "reference": source["reference"],
                        },
                    )
                    logger.success(f"Source [{source['name']}] updated")
                    continue
                else:
                    continue

            logger.info(f"Publishing new source [{source['name']}] ...")

            if source["visibility"] == "public":
                if not ask_confirmation(
                    "Are you sure you want to publish a public source? Public sources are visible for partners. Be careful about what you share."
                ):
                    continue

            r = send_api_request(
                request=f"/api/v1/sources/publish",
                mode="post",
                data={
                    "name": source["name"],
                    "type": source["type"],
                    "description": source["description"],
                    "reference": source["reference"],
                    "sensitive": source["sensitive"],
                    "visibility": source["visibility"],
                    "version": source_version(source),
                },
            )

            if r.status_code != 200:
                logger.warning(
                    f"Failed to publish source [{source['name']}] {r.status_code} - {r.text}"
                )
                invalid_count += 1
            else:
                source_id = r.json()["id"]
                logger.success(f"Source published with id [{source_id}]")
                config.config["sources"][i]["id"] = source_id
                config.save_source_config()

    if invalid_count > 0:
        logger.warning(f"{invalid_count} source(s) skipped due to validation errors.")


def push_programmatic(config, skip_validate: bool = False, approve_public: bool = False):
    """Programmatic push for sources without interactive prompts.

    Returns a tuple (ok: bool, message: str)
    """
    # try:
    if not skip_validate:
        try:
            validate_source.__wrapped__(config)  # type: ignore[attr-defined]
        except Exception:
            validate_source(config)  # type: ignore[misc]
    else:
        logger.warning("Skipping source validation as requested.")

    logger.info("------------- Source Publishing (programmatic) -------------")
    agent_conf = config.load_agent_config()
    config.load_source_config()

    if not config.config.get("sources"):
        msg = "No sources to publish."
        logger.warning(msg)
        return False, msg

    if skip_validate:
        valid_source = len(config.config["sources"])
    else:
        valid_source = sum(1 for s in config.config["sources"] if s.get("validate") == "valid")
    if valid_source == 0:
        msg = "No valid sources to publish"
        logger.warning(msg)
        return False, msg

    # Helper to call request functions without requiring a Click context
    def _send(cfg, **kwargs):
        try:
            return send_api_request.__wrapped__(cfg, **kwargs)  # type: ignore[attr-defined]
        except Exception:
            return send_api_request(cfg, **kwargs)  # type: ignore[misc]

    r = _send(config, request="/api/v2/sources", mode="get")
    if r.status_code == 200:
        response_data = r.json() or []
    else:
        msg = f"Remote platform error: {r.status_code}"
        logger.error(msg)
        return False, msg

    pushed = 0
    skipped = 0

    for i, source in enumerate(config.config["sources"]):
        if not (skip_validate or source.get("validate") == "valid"):
            continue

        # find matched source
        matched_source = next((s for s in response_data if s.get("name") == source.get("name") and s.get("type") == source.get("type")), None)

        if matched_source:
            update_source = False
            if matched_source.get("versions"):
                if source_version(source) == matched_source["versions"][0]["sem_ver_id"]:
                    # sync id if missing
                    if source.get("id") != matched_source.get("id"):
                        config.config["sources"][i]["id"] = matched_source.get("id")
                        config.save_source_config()
                    # check if metadata changed
                    if not (
                        source.get("visibility") == matched_source.get("visibility")
                        and source.get("description") == matched_source.get("description")
                        and source.get("sensitive") == matched_source.get("sensitive")
                        and source.get("reference") == matched_source.get("reference")
                    ):
                        update_source = True
                else:
                    update_source = True
            else:
                update_source = True

            if update_source:
                if source.get("visibility") == "public" and not approve_public:
                    logger.warning(f"Skipping public source without approval: {source.get('name')}")
                    skipped += 1
                    continue
                r = _send(
                    config,
                    request=f"/api/v2/sources/{matched_source['id']}",
                    mode="put",
                    data={
                        "description": source.get("description"),
                        "visibility": source.get("visibility"),
                        "sensitive": source.get("sensitive"),
                        "reference": source.get("reference"),
                    },
                )
                if r.status_code == 200:
                    pushed += 1
                else:
                    logger.warning(f"Failed to update source [{source.get('name')}] {r.status_code} - {r.text}")
                    skipped += 1
            continue

        # create new source
        if source.get("visibility") == "public" and not approve_public:
            logger.warning(f"Skipping public source without approval: {source.get('name')}")
            skipped += 1
            continue
        r = _send(
            config,
            request=f"/api/v1/sources/publish",
            mode="post",
            data={
                "name": source.get("name"),
                "type": source.get("type"),
                "description": source.get("description"),
                "reference": source.get("reference"),
                "sensitive": source.get("sensitive"),
                "visibility": source.get("visibility"),
                "version": source_version(source),
            },
        )
        if r.status_code != 200:
            logger.warning(f"Failed to publish source [{source.get('name')}] {r.status_code} - {r.text}")
            skipped += 1
        else:
            source_id = r.json().get("id")
            config.config["sources"][i]["id"] = source_id
            config.save_source_config()
            pushed += 1

    if pushed > 0:
        return True, f"Published/updated {pushed} source(s). Skipped {skipped}."
    return False, "No sources were published."
    # except Exception as e:
    #     return False, f"Failed to push sources: {e}"


def push_single_programmatic(config, source_name: str, approve_public: bool = False):
    """Programmatically publish or update a single source by name.

    Returns a tuple (ok: bool, message: str)
    """
    # Helper to send API requests regardless of Click context
    def _send(cfg, **kwargs):
        try:
            return send_api_request.__wrapped__(cfg, **kwargs)  # type: ignore[attr-defined]
        except Exception:
            return send_api_request(cfg, **kwargs)  # type: ignore[misc]

    # Load configs
    config.load_source_config()

    # Find the local source
    sources = config.config.get("sources", []) or []
    local = next((s for s in sources if s.get("name") == source_name), None)
    if not local:
        return False, f"Source '{source_name}' not found in local config."

    # Fetch remote sources
    r = _send(config, request="/api/v2/sources", mode="get")
    if r.status_code != 200:
        return False, f"Remote platform error: {r.status_code}"
    remote_list = r.json() or []

    # Try to match by name and type
    matched = next((s for s in remote_list if s.get("name") == local.get("name") and s.get("type") == local.get("type")), None)

    # Update existing
    if matched:
        if local.get("visibility") == "public" and not approve_public:
            return False, f"Skipped public source without approval: {local.get('name')}"
        r = _send(
            config,
            request=f"/api/v2/sources/{matched['id']}",
            mode="put",
            data={
                "description": local.get("description"),
                "visibility": local.get("visibility"),
                "sensitive": local.get("sensitive"),
                "reference": local.get("reference"),
            },
        )
        if r.status_code == 200:
            # sync id locally
            for i, src in enumerate(sources):
                if src.get("name") == source_name:
                    config.config["sources"][i]["id"] = matched.get("id")
                    config.save_source_config()
                    break
            return True, f"Source '{source_name}' updated."
        return False, f"Failed to update source '{source_name}': {r.status_code}"

    # Create new
    if local.get("visibility") == "public" and not approve_public:
        return False, f"Skipped public source without approval: {local.get('name')}"
    r = _send(
        config,
        request="/api/v1/sources/publish",
        mode="post",
        data={
            "name": local.get("name"),
            "type": local.get("type"),
            "description": local.get("description"),
            "reference": local.get("reference"),
            "sensitive": local.get("sensitive"),
            "visibility": local.get("visibility"),
            "version": source_version(local),
        },
    )
    if r.status_code != 200:
        return False, f"Failed to publish source '{source_name}': {r.status_code}"
    source_id = r.json().get("id")
    for i, src in enumerate(sources):
        if src.get("name") == source_name:
            config.config["sources"][i]["id"] = source_id
            config.save_source_config()
            break
    return True, f"Source '{source_name}' published."

@source.command()
@pass_config
def add(config):
    """Add a source to the local Qalita Config"""

    # initialize the source dict
    source = {}

    # hardcode empty source config
    source["config"] = {}

    # ask for the source name
    source["name"] = click.prompt("Source name")

    # ask for the source type
    source["type"] = click.prompt(
        "Source type (file, folder, postgresql, mysql, oracle, mssql, sqlite, mongodb, s3, gcs, azure_blob, hdfs)",
    )

    # Configure according to the selected source type
    if source["type"] == "file":
        source["config"]["path"] = click.prompt("Source file path")
    elif source["type"] == "folder":
        source["config"]["path"] = click.prompt("Source folder path")
    elif source["type"] in ["postgresql", "mysql", "oracle", "mssql"]:
        if source["type"] == "postgresql":
            db_type = click.prompt(
                "Source database Type (mysql, postgresql, oracle, mssql, sqlite, mongodb, ...)",
            )
        else:
            db_type = source["type"]
        source["config"]["type"] = db_type
        if db_type == "sqlite":
            source["config"]["file_path"] = click.prompt("SQLite file path")
        elif db_type == "oracle":
            source["config"]["host"] = click.prompt("Oracle host")
            source["config"]["port"] = click.prompt("Oracle port")
            source["config"]["username"] = click.prompt("Oracle username")
            source["config"]["password"] = click.prompt("Oracle password")
            source["config"]["database"] = click.prompt("Oracle service name")
        elif db_type == "mssql":
            source["config"]["host"] = click.prompt("MSSQL host")
            source["config"]["port"] = click.prompt("MSSQL port")
            source["config"]["username"] = click.prompt("MSSQL username")
            source["config"]["password"] = click.prompt("MSSQL password")
            source["config"]["database"] = click.prompt("MSSQL database")
        elif db_type == "mysql":
            source["config"]["host"] = click.prompt("MySQL host")
            source["config"]["port"] = click.prompt("MySQL port")
            source["config"]["username"] = click.prompt("MySQL username")
            source["config"]["password"] = click.prompt("MySQL password")
            source["config"]["database"] = click.prompt("MySQL database")
        elif db_type == "postgresql":
            source["config"]["host"] = click.prompt("PostgreSQL host")
            source["config"]["port"] = click.prompt("PostgreSQL port")
            source["config"]["username"] = click.prompt("PostgreSQL username")
            source["config"]["password"] = click.prompt("PostgreSQL password")
            source["config"]["database"] = click.prompt("PostgreSQL database")
        else:
            source["config"]["host"] = click.prompt("Source host")
            source["config"]["port"] = click.prompt("Source port")
            source["config"]["username"] = click.prompt("Source username")
            source["config"]["password"] = click.prompt("Source password")
            source["config"]["database"] = click.prompt("Source database")
        # Optional schema for PostgreSQL and Oracle
        if db_type in ("postgresql", "oracle"):
            schema = click.prompt("Schema (optional)", default="", show_default=False)
            if schema:
                source["config"]["schema"] = schema
        # Specify a table or an SQL query to restrict the scan scope. By default, '*' scans the entire database
        source["config"]["table_or_query"] = click.prompt(
            "Table name, list of table names or SQL query (default '*' scans the entire database)",
            default="*",
        )
    elif source["type"] == "mongodb":
        source["config"]["host"] = click.prompt("MongoDB host")
        source["config"]["port"] = click.prompt("MongoDB port")
        source["config"]["username"] = click.prompt("MongoDB username")
        source["config"]["password"] = click.prompt("MongoDB password")
        source["config"]["database"] = click.prompt("MongoDB database")
    elif source["type"] == "s3":
        source["config"]["bucket"] = click.prompt("S3 bucket name")
        source["config"]["prefix"] = click.prompt("S3 prefix (optional)", default="")
        source["config"]["access_key"] = click.prompt("S3 access key")
        source["config"]["secret_key"] = click.prompt("S3 secret key")
        source["config"]["region"] = click.prompt("S3 region")
    elif source["type"] == "gcs":
        source["config"]["bucket"] = click.prompt("GCS bucket name")
        source["config"]["prefix"] = click.prompt("GCS prefix (optional)", default="")
        source["config"]["credentials_json"] = click.prompt("GCS credentials JSON path")
    elif source["type"] == "azure_blob":
        source["config"]["container"] = click.prompt("Azure Blob container name")
        source["config"]["prefix"] = click.prompt("Blob prefix (optional)", default="")
        source["config"]["connection_string"] = click.prompt("Azure Blob connection string")
    elif source["type"] == "hdfs":
        source["config"]["namenode_host"] = click.prompt("HDFS namenode host")
        source["config"]["port"] = click.prompt("HDFS port")
        source["config"]["user"] = click.prompt("HDFS user")
        source["config"]["path"] = click.prompt("HDFS path")
    else:
        # Generic fallback
        click.echo(f"Unknown or unsupported source type: {source['type']}")
        click.echo("You can add keys manually in the YAML configuration file if needed.")

    # ask for the source description
    source["description"] = click.prompt("Source description")
    # ask for the source reference
    source["reference"] = click.prompt("Source reference", type=bool, default=False)
    # ask for the source sensitive
    source["sensitive"] = click.prompt("Source sensitive", type=bool, default=False)
    # ask for the source visibility
    source["visibility"] = click.prompt(
        "Source visibility",
        default="private",
        type=click.Choice(["private", "internal", "public"], case_sensitive=False),
    )

    config.load_source_config()
    if len(config.config["sources"]) > 0:
        # check if the source already exists
        for conf_source in config.config["sources"]:
            if conf_source["name"] == source["name"]:
                logger.error("Source already exists in config")
                return

    # add the source to the config
    new_source = {
        "name": source["name"],
        "config": source["config"],
        "type": source["type"],
        "description": source["description"],
        "reference": source["reference"],
        "sensitive": source["sensitive"],
        "visibility": source["visibility"],
    }

    # Pre-validate the source before saving
    if not validate_source_object(config, new_source, skip_connection=False):
        logger.error("Source validation failed, aborting add")
        return

    config.config["sources"].append(new_source)

    # save the config
    config.save_source_config()
    logger.success(f"Source [{source['name']}] added to the local config")
