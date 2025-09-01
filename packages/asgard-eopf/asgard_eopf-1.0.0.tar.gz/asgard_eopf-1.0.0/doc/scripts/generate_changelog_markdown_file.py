#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2023 CS GROUP
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
Script to automatically generate a changelog file for ASGARD project
"""
import json
import os
import os.path as osp
from pathlib import Path
from typing import Dict

import gitlab
from mdutils.mdutils import MdUtils  # type: ignore
from tomark import Tomark  # type: ignore


def gitlab_issue_to_json(gitlab_token: str, project_id: int, path_to_json: str):
    """
    Retrieve information on the different releases of ASGARD to build the changelog file

    Parameters
    ----------
    your_gitlab_token: str
        your gitlab access token to the project repository
    project_id: int
        Gitlab identifier of the current project
    path_to_json: str
        path to the output json file containing information about milestones

    """
    # Dictionary with all issues per milestone
    all_issues: Dict = {"released": {}, "unreleased": {}}

    # Connection
    # private token or personal token authentication (self-hosted GitLab instance)
    gl = gitlab.Gitlab(url="https://gitlab.eopf.copernicus.eu", private_token=gitlab_token)

    # Get the right project from the list of eopf projects
    project = gl.projects.get(project_id)

    # Get all milestones from the project
    milestone_list = list(project.milestones.list(get_all=True))

    # Add information on unreleased and released milestones in the dictionary
    for active_milestone_info in milestone_list:
        milestone_name, milestone_description, milestone_date = (
            active_milestone_info.title,
            active_milestone_info.description,
            active_milestone_info.due_date,
        )
        closed_issues = project.issues.list(state="closed", milestone=milestone_name, get_all=True)
        open_issues = project.issues.list(state="opened", milestone=milestone_name, get_all=True)
        release_status = "released" if active_milestone_info.expired else "unreleased"
        all_issues[release_status][milestone_name] = {
            "due_date": milestone_date if milestone_date else "Unknown",
            "description": milestone_description,
            "issues": [
                {
                    "id": x.attributes["iid"],
                    "state": x.attributes["state"],
                    "title": x.attributes["title"],
                }
                for x in open_issues + closed_issues  # type: ignore
            ],
        }

    # Write the final dirctionary to a Python file
    with open(path_to_json, "w", encoding="UTF-8") as fp:
        json.dump(all_issues, fp)


def generate_markdown_from_json(json_input_path: str, path_to_markdown: str):
    """
    Generate the changelog markdown file from the json data

    Parameters
    ----------
    json_input_path: str
        path to the json file containing information about milestones

    path_to_markdown: str
        path to the output changelog markdown file
    """

    with open(json_input_path, encoding="UTF-8") as json_file:
        issue_dict = json.load(json_file)

        # Generate the structure of our markdown file
        md_file = MdUtils(file_name=path_to_markdown, title="ASGARD changelog file")
        md_file.new_paragraph("All notable changes of ASGARD are documented in this file. \n\n")

        # Construct section for unreleased milestones
        md_file.new_header(level=1, title="Future/unreleased milestones")
        for milestone, content in issue_dict["unreleased"].items():
            md_file.new_header(level=2, title="Milestone " + milestone + " - Due date: " + content["due_date"])
            md_file.new_paragraph(content["description"])
            if len(content["issues"]) != 0:
                md_file.new_paragraph(Tomark.table(content["issues"]))
            md_file.write("\n\n")

        # Construct section for passed releases
        md_file.new_header(level=1, title="Past releases")
        for milestone, content in issue_dict["released"].items():
            md_file.new_header(level=2, title="Milestone " + milestone + " - Release date: " + content["due_date"])
            md_file.new_paragraph(content["description"])
            if len(content["issues"]) != 0:
                md_file.new_paragraph(Tomark.table(content["issues"]))
            md_file.write("\n\n")

        md_file.create_md_file()


if __name__ == "__main__":
    # Input variables

    # You first have to set this environment variable with your Gitlab token
    # Use the following command in a command prompte: export your_eopf_gitlab_token="VALUE_OF_YOUR_TOKEN"
    YOUR_GITLAB_TOKEN = os.getenv("YOUR_EOPF_GITLAB_TOKEN")
    ASGARD_PROJECT_ID = 52

    # Generate intermediary and output files in the /build/changelog_files folder of the documentation
    PATH_TO_CHANGELOG_DATA = osp.join(Path(__file__).parents[1].absolute().as_posix(), "build", "changelog_files")

    # Check if the folder to write json data exists and create it if it is not the case
    if not os.path.exists(PATH_TO_CHANGELOG_DATA):
        os.makedirs(PATH_TO_CHANGELOG_DATA)

    # osp.abspath(os.path.join(os.getcwd()))
    json_path = osp.join(PATH_TO_CHANGELOG_DATA, "changelog_content.json")
    markdown_path = osp.join(PATH_TO_CHANGELOG_DATA, "changelog.md")

    if not YOUR_GITLAB_TOKEN:
        raise KeyError(
            "You first have to define your Gitlab token -> use the following command:"
            "export YOUR_EOPF_GITLAB_TOKEN= 'YOUR_GITLAB_TOKEN'"
            "In order to generate your token, follow the instructions on"
            "https://sde.pages.eopf.copernicus.eu/sde/main/user-manual/gitlab-setup.html",
        )
    # Generate json data from the gitlab ASGARD project
    gitlab_issue_to_json(YOUR_GITLAB_TOKEN, ASGARD_PROJECT_ID, json_path)

    # Generate markdown file from json data
    generate_markdown_from_json(json_path, markdown_path)
