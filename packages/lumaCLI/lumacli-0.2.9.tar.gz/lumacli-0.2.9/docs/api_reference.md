# `luma`

**Usage**:

```console
$ luma [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --version`: Show the version and exit.
* `-c, --config-dir TEXT`: The directory containing the Luma configuration file.  [env var: LUMA_CONFIG_DIR]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `status`: Retrieve the status of an ingestion.
* `ingest`: Ingest metadata from external sources into...
* `dbt`: Ingest metadata from dbt.
* `postgres`: Ingest metadata from Postgres.
* `config`: Manage Luma instance configuration.

## `luma status`

Retrieve the status of an ingestion.

**Usage**:

```console
$ luma status [OPTIONS] INGESTION_ID
```

**Arguments**:

* `INGESTION_ID`: Ingestion ID.  [required]

**Options**:

* `-l, --luma-url TEXT`: URL of the luma instance.  [env var: LUMA_URL; default: localhost:8000]
* `--help`: Show this message and exit.

## `luma ingest`

Ingest metadata from external sources into Luma.

**Usage**:

```console
$ luma ingest [OPTIONS] SOURCE:{powerbi|qlik_sense|sap}
```

**Arguments**:

* `SOURCE:{powerbi|qlik_sense|sap}`: [required]

**Options**:

* `-l, --luma-url TEXT`: URL of the luma instance.  [env var: LUMA_URL; default: localhost:8000]
* `-D, --dry-run`: Perform a dry run. Print the payload but do not send it.
* `--follow`: Follow the ingestion process until it&#x27;s completed.
* `-t, --follow-timeout INTEGER`: How many seconds to wait for the ingestion process to complete.  [env var: LUMA_TIMEOUT; default: 30]
* `--help`: Show this message and exit.

## `luma dbt`

**Usage**:

```console
$ luma dbt [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `ingest`: Sends 'manifest.json' and 'catalog.json' created by dbt
* `send-test-results`: Sends 'run_results.json' file

### `luma dbt ingest`

Sends a bundle of JSON files (manifest.json, catalog.json) located in the specified directory to a Luma endpoint.
If manifest.json and/or catalog.json files are not present in the directory, the command will fail. The file sources.json is optional. Uses the current working directory if 'metadata_dir' is not specified.

**Usage**:

```console
$ luma dbt ingest [OPTIONS]
```

**Options**:

* `-m, --metadata-dir PATH`: Specify the directory with dbt metadata files. Defaults to current working directory if not provided.
* `-l, --luma-url TEXT`: URL of the luma instance.  [env var: LUMA_URL]
* `-D, --dry-run`: Perform a dry run. Print the payload but do not send it.
* `--follow`: After the files are send to luma for ingesting, immediately start checking for the status every 1 second for 30 seconds until the ingestion is processed
* `--help`: Show this message and exit.

### `luma dbt send-test-results`

Sends the 'run_results.json' file located in the specified directory to a Luma endpoint.
The command will fail if the 'run_results.json' file is not present in the directory. The current working directory is used if 'metadata_dir' is not specified.

**Usage**:

```console
$ luma dbt send-test-results [OPTIONS]
```

**Options**:

* `-m, --metadata-dir PATH`: Specify the directory with dbt metadata files. Defaults to current working directory if not provided.
* `-l, --luma-url TEXT`: URL of the luma instance.  [env var: LUMA_URL]
* `-D, --dry-run`: Perform a dry run. Print the payload but do not send it.
* `--follow`: After the files are send to luma for ingesting, immediately start checking for the status every 1 second for 30 seconds until the ingestion is processed
* `--help`: Show this message and exit.

## `luma postgres`

Ingest metadata from Postgres.

**Usage**:

```console
$ luma postgres [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `ingest`: Ingest metadata from PostgreSQL database...

### `luma postgres ingest`

Ingest metadata from PostgreSQL database into a Luma ingestion endpoint.

**Usage**:

```console
$ luma postgres ingest [OPTIONS]
```

**Options**:

* `-l, --luma-url TEXT`: URL of the luma instance.  [env var: LUMA_URL; default: localhost:8000]
* `-u, --username TEXT`: The username for the PostgreSQL database.  [env var: LUMA_POSTGRES_USERNAME; required]
* `-d, --database TEXT`: The name of the PostgreSQL database.  [env var: LUMA_POSTGRES_DATABASE; required]
* `-h, --host TEXT`: The host address of the PostgreSQL database.  [env var: LUMA_POSTGRES_HOST; default: localhost]
* `-p, --port TEXT`: The port number for the PostgreSQL database.  [env var: LUMA_POSTGRES_PORT; default: 5432]
* `-P, --password TEXT`: The password for the PostgreSQL database.  [env var: LUMA_POSTGRES_PASSWORD; required]
* `-D, --dry-run`: Perform a dry run. Print the payload but do not send it.
* `-c, --config-dir PATH`: Specify the directory with the config files. Defaults to ./.luma  [env var: LUMA_CONFIG_DIR; default: ./.luma]
* `-n, --no-config`: Set this flag to prevent sending configuration data along with the request.
* `--help`: Show this message and exit.

## `luma config`

**Usage**:

```console
$ luma config [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `init`: Initialize the configuration.
* `send`: Send the current configuration information...
* `show`: Display the current configuration...

### `luma config init`

Initialize the configuration.

**Usage**:

```console
$ luma config init [OPTIONS]
```

**Options**:

* `-c, --config-dir PATH`: Specify the directory with the config files. Defaults to ./.luma  [env var: LUMA_CONFIG_DIR; default: ./.luma]
* `-f, --force`: Force the operation
* `--help`: Show this message and exit.

### `luma config send`

Send the current configuration information to luma

**Usage**:

```console
$ luma config send [OPTIONS]
```

**Options**:

* `-c, --config-dir PATH`: Specify the directory with the config files. Defaults to ./.luma  [env var: LUMA_CONFIG_DIR; default: ./.luma]
* `-l, --luma-url TEXT`: URL of the luma instance.  [env var: LUMA_URL]
* `--help`: Show this message and exit.

### `luma config show`

Display the current configuration information.

**Usage**:

```console
$ luma config show [OPTIONS]
```

**Options**:

* `-c, --config-dir PATH`: Specify the directory with the config files. Defaults to ./.luma  [env var: LUMA_CONFIG_DIR; default: ./.luma]
* `--help`: Show this message and exit.

## `luma status`

Retrieve the status of an ingestion.

**Usage**:

```console
$ luma status [OPTIONS] COMMAND [ARGS]...
```

**Arguments**:

* `ingestion_id TEXT`: Ingestion ID. [default: None] [required]

**Options**:

* `-l, --luma-url TEXT`: URL of the luma instance.  [env var: LUMA_URL]
* `--help`: Show this message and exit.
