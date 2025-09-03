#  Copyright 2022-present, the Waterdip Labs Pvt. Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json
from typing import List, Union

import click

from dcs_sdk.__version__ import __version__
from dcs_sdk.sdk.config.config_loader import Comparison, data_diff_config_loader
from dcs_sdk.sdk.data_diff.data_differ import diff_db_tables
from dcs_sdk.sdk.utils.utils import post_comparison_results


@click.version_option(version=__version__, package_name="dcs-sdk", prog_name="DCS SDK")
@click.group(help=f"DCS SDK version {__version__}")
def main():
    pass


@main.command(
    short_help="Starts DCS SDK",
)
@click.option(
    "-C",
    "--config-path",
    required=True,
    default=None,
    help="Specify the file path for configuration",
)
@click.option(
    "--save-json",
    "-j",
    is_flag=True,
    help="Save data into JSON file",
)
@click.option(
    "--json-path",
    "-jp",
    required=False,
    default="dcs_report.json",
    help="Specify the file path for JSON file",
)
@click.option(
    "--compare",
    required=True,
    help="Run only specific comparison using comparison name",
)
@click.option(
    "--stats",
    is_flag=True,
    help="Print stats about data diff",
)
@click.option(
    "--url",
    required=False,
    help="Specify the server URL to send data",
)
@click.option(
    "--html-report",
    is_flag=True,
    help="Save table as HTML",
)
@click.option(
    "--report-path",
    required=False,
    default="dcs_report.html",
    help="Specify the file path for HTML report",
)
@click.option(
    "--table",
    "display_table",
    is_flag=True,
    help="Display Comparison in table format",
)
def run(
    config_path: Union[str, None],
    save_json: bool = False,
    json_path: str = "dcs_report.json",
    compare: str = None,
    stats: bool = False,
    url: str = None,
    html_report: bool = False,
    report_path: str = "dcs_report.html",
    display_table: bool = False,
):
    data_diff_cli(
        config_path=config_path,
        save_json=save_json,
        json_path=json_path,
        compare=compare,
        url=url,
        is_cli=True,
        show_stats=stats,
        html_report=html_report,
        report_path=report_path,
        display_table=display_table,
    )


def data_diff_cli(
    config_path,
    save_json: bool,
    json_path: str,
    report_path: str,
    compare: str,
    url: str,
    is_cli: bool = True,
    show_stats: bool = False,
    html_report: bool = False,
    display_table: bool = False,
):
    comparisons: List[Comparison] = data_diff_config_loader(config_path)
    comp_name_found = False
    result = None
    try:
        for comparison in comparisons:
            if comparison.comparison_name == compare:
                result = diff_db_tables(
                    config=comparison,
                    is_cli=is_cli,
                    show_stats=show_stats,
                    save_html=html_report,
                    html_path=report_path,
                    display_table=display_table,
                )
                total_seconds = result.get("meta", {}).get("seconds", 0)
                print(f"Time took: {total_seconds:.2f} {'seconds' if total_seconds > 1 else 'second'}")
                comp_name_found = True

        if not comp_name_found:
            raise ValueError(f"Comparison name {compare} not found in the config file")
        if result and url:
            post_comparison_results(
                comparison_data=result,
                url=url,
                is_cli=is_cli,
            )
        if save_json:
            if result:
                with open(json_path, "w") as f:
                    f.write(json.dumps(result))

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
