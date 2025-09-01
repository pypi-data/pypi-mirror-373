#!/usr/bin/env python
# coding: utf8
#
# Copyright 2024 CS GROUP
# Licensed to CS GROUP (CS) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# CS licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Script in order to convert json files to markdown tables
"""
import glob
import json
import logging
import os


def read_json(file_path):
    """
    Read a json file and return loaded data
    """
    with open(file_path, "r", encoding="utf8") as json_file:
        return json.load(json_file)


def merge_json_files(file_paths, merged_file):
    """
    Merge multiple json files
    """
    merged_data = {}
    for file_path in file_paths:
        file_name = os.path.basename(file_path).split(".")[0]
        merged_data[file_name] = read_json(file_path)

    with open(merged_file, "w", encoding="utf8") as output_file:
        json.dump(merged_data, output_file)


def results_json_to_markdown_table(json_file):
    """
    Generate a markdown file from the merged json files containing multiple TDS results
    """
    data = read_json(json_file)

    title = json_file.split("/")[-1].split(".")[0]
    columns_head = ["Datasets", "ground", "altitude", "inverse_loc", "sun", "incidence", "footprint_r", "footprint_d"]

    header = f"| {' | '.join(columns_head)} | \n"
    header += f"| {' '.join([' --- |']*len(columns_head))}"

    markdown_body = ""
    for tds_name in data.keys():
        markdown_body += f"\n| {tds_name} |"
        tds_data = data[tds_name]
        for key in columns_head[1:]:
            if key in tds_data.keys():
                markdown_body += f" {tds_data[key]['max']:.3g} ({tds_data[key]['C90']:.3g}) | "

    markdown_content = header + markdown_body
    out_path = "/".join(json_file.split("/")[:-1])
    markdown_file = os.path.join(out_path, f"{title}.md")

    with open(markdown_file, "w", encoding="utf8") as output_markdown:
        output_markdown.write(markdown_content)
    print(f"Markdown table written to {title}.md")

    return markdown_file


def times_json_to_md_table(json_file, context):
    """
    Generate a markdown file from the merged json files containing multiple TDS times execution
    """
    data = read_json(json_file)

    title = json_file.split("/")[-1].split(".")[0]
    columns_head = ["Datasets", "direct loc", "inverse loc", "sun_angles", "incidence_angles", "footprint"]

    header = f"## {context} \n\n| {' | '.join(columns_head)} | \n"
    header += f"| {' '.join([' --- |']*len(columns_head))}"

    markdown_body = ""
    for tds_name in data.keys():
        markdown_body += f"\n| {tds_name} |"
        tds_data = data[tds_name]
        for key in columns_head[1:]:
            if key in tds_data.keys():
                markdown_body += f" {tds_data[key]:.3g} s | "

    markdown_content = header + markdown_body
    out_path = "/".join(json_file.split("/")[:-1])
    markdown_file = os.path.join(out_path, f"{title}.md")

    with open(markdown_file, "w", encoding="utf8") as md_file:
        md_file.write(markdown_content)
    logging.info("Markdown table written to %s.md", title)

    return markdown_file


if __name__ == "__main__":

    TEST_DIR = os.path.dirname(__file__)
    PARENT_DIR = os.path.join(os.path.dirname(TEST_DIR), "msi_validation")

    for root, _dirs, _files in os.walk(PARENT_DIR):
        json_files = sorted(glob.glob(os.path.join(root, "S2MSI_*.json")))

        if json_files:
            logging.info("Merge all json files in one in directory %s", root)
            dem_type = root.split("/")[-1]
            out_path_merged = os.path.join(PARENT_DIR, f"tds_merged_{dem_type}.json")
            merge_json_files(json_files, out_path_merged)

            logging.info("Convert %s in markdown file", out_path_merged.split("/")[-1])
            if "times" in dem_type:
                context_str = (
                    "Times execution running ASGARD (refactored or legacy, specified in the TDS name)"
                    f"using {dem_type.split('_')[-1]} DEM"
                )
                markdown_table = times_json_to_md_table(out_path_merged, context_str)
            else:
                context_str = (
                    "Error on results running ASGARD (refactored or legacy, specified in the TDS name)"
                    f"using {dem_type.split('_')[-1]} DEM"
                )
                markdown_table = results_json_to_markdown_table(out_path_merged)

            if os.path.exists(markdown_table):
                os.remove(out_path_merged)
