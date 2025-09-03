# luma CLI User Guide

## Metadata ingestion

### dbt

Follow below instructions to add metadata to your dbt models and then ingest it (together with built-in dbt metadata) into Luma.

1. Add required owners and groups

    See [Luma instance configuration](#luma-instance-configuration) for details on how to set up owners and groups in your Luma instance.

2. Add metadata

    Navigate to the YAML file corresponding to the resource you want to add metadata to. Use the `meta` key to add custom key-value pairs within the YAML file. Here’s an example where a model is tagged with owner and domain information:

    ```yaml
    models:
    - name: my_table
        description: "This is my example table"
        meta:
        owners:
            - email: "dana@example.com"
            type: "Business Owner"
            - email: "dana@example.com"
            type: "Technical Owner"
        domains:
            - finance
    ```

3. Generate metadata JSON files

    To generate model metadata, execute the following commands:

    - `dbt deps`
    - `dbt docs generate`

    Next, to generate model run metadata, execute the following commands:

    - `dbt run`
    - `dbt test`

4. Ingest the metadata into Luma

    Execute the [`luma dbt ingest`](./api_reference.md#luma-dbt-ingest) command to ingest the metadata into Luma.

### Postgres

To ingest metadata from a PostgreSQL database into Luma, execute the designated command:

```console
luma postgres ingest --luma-url <url> --username <username> --password <password> --host <host> --database <database>
```

### Other sources

For all other sources, use the `luma metadata ingest` command.

!!! note "Inspecting metadata locally"

    These instructions assume the source system has already been configured correctly. For source-specific instructions, see [Configuring metadata source systems](#configuring-metadata-source-systems).

#### Configuration

##### 1. Install the required dependencies

```console
uv sync
```

##### 2. Configure source credentials

First, copy the example credentials file:

```console
cp .dlt/secrets.toml.example .dlt/secrets.toml
```

Then, edit the file and add the credentials for the source you want to extract data from.

#### Ingesting metadata

To ingest metadata into a Luma instance, execute:

```console
luma ingest <source> --luma-url <url>
```

!!! info "Inspecting metadata locally"

    For local testing, you can instead load the metadata into a local DuckDB instance:

    ```console
    python src/luma/metadata/sources/<source>/pipeline.py
    ```

## Luma instance configuration

### Owners

In the directory where you run the `luma` from, a `.luma` folder can be created containing a `owners.yaml` file. Initialize this using the command:

[`luma config init`](./api_reference.md#luma-config-init)

This allows you to centralize and manage owner information effortlessly.

#### `owners.yaml`

The `owners.yaml` file serves as a centralized location to define each owner, including their name, email, and title. You can then tag various metadata resources using only the email address of the owner, and optionally specify the type of owner.

An owner is defined with the following attributes:

- **`email`**: A unique key representing the owner's email address. This field is required.
  - **Example**: `"someone@example.com"`
- **`first_name`**: The first name of the owner, optional.
  - **Example**: `"Aaron"`
- **`last_name`**: The last name of the owner, a required field.
  - **Example**: `"Jackson"`
- **`title`**: The title or role of the owner within the organization, a required field.
  - **Example**: `"Data Analyst"`

#### Example

Below is an example structure of the `owners.yaml` file located at *.luma/owners.yaml*:

```yaml
owners:
  - email: "dave@example.com"
    first_name: "Dave"
    last_name: "Cotterall"
    title: "Director"
  - email: "michelle@example.com"
    first_name: "Michelle"
    last_name: "Dunne"
    title: "CTO"
  - email: "dana@example.com"
    first_name: "Dana"
    last_name: "Pawlak"
    title: "HR Manager"
```

#### Tagging metadata with owners

Once the `owners.yaml` file is set up, you can tag various metadata resources with owner information through the metadata definition of that asset. Below is an example for `dlt`:

```yaml
models:
    - name: my_table
    description: "This is my example table"
    meta:
        owners:
        - email: "dana@example.com"
            type: "Business Owner"
        - email: "dana@example.com"
            type: "Technical Owner"
```

### Groups

In the directory where you run the `luma`, a `.luma` folder can be created containing a `config.yaml` file. Initialize this using the command:

[`luma config init`](./api_reference.md#luma-config-init)

You can organize your catalog into groups of metadata to facilitate easier management. For instance, you might have 'Departments' to categorize assets by organization department or 'Data Product' to group all assets under a specific product in the Luma Catalog.

The `groups` key in the `config.yaml` contains a list of objects defining specific characteristics, detailed below:

#### Properties

- **`meta_key`**: A required string that represents the key identifier.
  - **Example**: `"data_product"`
- **`slug`**: A required string that yields a URL-friendly version of the label.
  - **Example**: `"data-products"`
- **`label_plural`**: A required string for the plural form of the label.
  - **Example**: `"Data Products"`
- **`label_singular`**: A required string for the singular form of the label.
  - **Example**: `"Data Product"`
- **`icon`**: A required string indicating an icon associated with the group, chosen from [HeroIcons](https://heroicons.com).
  - **Example**: `"Cube"`
- **`in_sidebar`**: An optional boolean that determines whether the group should be displayed in the sidebar. By default, True.
  - **Example**: `true`
- **`visible`**: An optional boolean that determines whether the group should be displayed in Luma UI. By default, True.
  - **Example**: `true`

#### Example

```yaml
# .luma/config.yaml
groups:
  - meta_key: "department"
    slug: "departments"
    label_plural: "Departments"
    label_singular: "Department"
    icon: "Cube"
    in_sidebar: true
    visible: true
  - meta_key: "data_product"
    slug: "data-products"
    label_plural: "Data Products"
    label_singular: "Data Product"
    icon: "Cloud"
    in_sidebar: true
```

#### Tagging metadata with groups

In `luma`, assets can be tagged to belong to one or more groups through the metadata definition of that asset.

##### DBT

In the properties file, use the `meta` key to add custom key-value pairs. Here's an example for a model:

```yaml
models:
- name: my_table
    description: "This is my example table"
    meta:
      department: "HR"
```

## Configuring metadata source systems

Some systems require additional configuration to enable metadata extraction.

### PowerBI

#### Creating a Service Principal

There are multiple ways to authenticate with PowerBI REST API. Below we use the Service Principal (also referred to as "app", "Azure app", "Entra app", "PowerBI app", and OAuth2 client credentials) authentication method.

**NOTE** This authentication method only allows using a subset of the PowerBI REST API (the admin endpoints). For a full list of supported endpoints, see https://learn.microsoft.com/en-us/fabric/admin/metadata-scanning-enable-read-only-apis#considerations-and-limitations.

1. [Create an app](https://learn.microsoft.com/en-us/power-bi/developer/embedded/embed-service-principal#step-1---create-an-azure-ad-app)
2. [Create a Microsoft Entra Security Group](https://learn.microsoft.com/en-us/entra/fundamentals/how-to-manage-groups#create-a-basic-group-and-add-members)
3. Add the app to the group
4. [Enable the Power BI service admin settings](https://learn.microsoft.com/en-us/power-bi/developer/embedded/embed-service-principal#step-3---enable-the-power-bi-service-admin-settings)

    Make sure to choose "Specify security groups" and add the group you created in step 2.

5. [Enable to app to use REST API admin endpoints](https://learn.microsoft.com/en-us/fabric/admin/metadata-scanning-enable-read-only-apis#method) (step 4)

    Make sure to choose "Specify security groups" and add the group you created in step 2.
  
    Here's how to get to those tenant settings:

    ![tenant settings](./_static/admin-portal-tenant-settings.png)

6. In PowerBI, add the group to the workspace (role must be Member or higher)

    ![add service principal group as workspace member](./_static/add-sp-group-to-workspace.png)
    ![add service principal group as workspace member - part 2](./_static/pbi-workspace-sp-group-access.png)

#### Configuring the PowerBI instance

To track the lineage of our data, we need to build a link from a table to a dataset, and then from a dataset to a dashboard. Fortunately, this information is available via PowerBI REST API's `admin/workspaces/getInfo` endpoint. However, retrieving this information from this endpoint requires getting a few things right.

Since we will use parameters to enable retrieving extra information from the `getInfo` endpoint, we need to enable additional two PowerBI tenant settings in app.powerbi.com -> Settings -> Admin portal -> Tenant settings (section "Admin API Settings"):

- Enhance admin APIs responses with detailed metadata
- Enhance admin APIs responses with DAX and mashup expressions

Make sure to choose "Specify security groups" and add the group you created in step 2 of the initial setup.
