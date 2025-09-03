<h1 align="center">
  DCS SDK v1.5.5
</h1>

> SDK for DataChecks


## Installation

> Python version `>=3.10,<3.13`

```bash

$ pip install dcs-sdk[all-dbs]

```

## Supported Databases

> Availability Status

| Database          | Code Name    | Supported |
| ----------------- | ------------ | --------- |
| PostgreSQL        | `postgres`   | ✅         |
| Snowflake         | `snowflake`  | ✅         |
| Trino             | `trino`      | ✅         |
| Databricks        | `databricks` | ✅         |
| Oracle            | `oracle`     | ✅         |
| MSSQL             | `mssql`      | ✅         |
| MySQL             | `mysql`      | ✅         |
| SAP Sybase IQ/ASE | `sybase`     | ✅         |
| File              | `file`       | ✅         |
| BigQuery          | `bigquery`   | ✅         |




## Available Commands



|    Option     | Short Option | Required |     Default     |                    Description                     |                                                 Example                                                  |
| :-----------: | :----------: | :------: | :-------------: | :------------------------------------------------: | :------------------------------------------------------------------------------------------------------: |
| --config-path |      -C      | **Yes**  |      None       |    Specify the file path for the configuration     |                        dcs-sdk run --config-path config.yaml --compare comp_name                         |
|   --compare   |              | **Yes**  |      None       | Run only specific comparison using comparison name |                        dcs-sdk run --config-path config.yaml --compare comp_name                         |
|  --save-json  |      -j      |    No    |      False      |           Save the data into a JSON file           |                  dcs-sdk run --config-path config.yaml --compare comp_name --save-json                   |
|  --json-path  |     -jp      |    No    | dcs_report.json |        Specify the file path for JSON file         |       dcs-sdk run --config-path config.yaml --compare comp_name --save-json --json-path ouput.json       |
|    --stats    |              |    No    |      False      |            Print stats about data diff             |                    dcs-sdk run --config-path config.yaml --compare comp_name --stats                     |
|     --url     |              |    No    |      None       |         Specify url to send data to server         |        dcs-sdk run --config-path config.yaml --compare comp_name --url=https://comapre/send/data         |
| --html-report |              |    No    |      False      |                 Save table as HTML                 |                 dcs-sdk run --config-path config.yaml --compare comp_name --html-report                  |
| --report-path |              |    No    | dcs_report.html |       Specify the file path for HTML report        |     dcs-sdk run --config-path config.yaml --compare comp_name --html-report --report-path table.html     |
|    --table    |              |    No    |      False      |         Display Comparison in table format         | dcs-sdk run --config-path config.yaml --compare comp_name --html-report --report-path table.html --table |



### Example Command [CLI]

```sh
$ dcs-sdk --version

$ dcs-sdk --help

$ dcs-sdk run -C example.yaml --compare comparison_one --stats -j -jp output.json --html-report --report-path result.html --table --url=https://comapre/send/data
```
