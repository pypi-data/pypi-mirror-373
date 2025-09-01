"""
Report the offending libraries from a given project,version in a short format suitable for jira/slack notifications. Include all subprojects.

@Author: Fabio Arciniegas <fabio_arciniegas@trendmicro.com>

Based on samples from synopsys hub blackduck api by @author: gsnyder
"""

import argparse
from io import StringIO
from blackduck.HubRestApi import HubInstance
import pandas as pd
import os
import sys
import json
from . import eprint

def summary(df, cutoff, headers, style="SHORT", urls=True,hub=None):
    hub = hub or HubInstance()
    if df is None:
        return
    df["Total"] = df.loc[:, headers["critical"] : headers[cutoff]].sum(axis=1)
    output_results(df[df["Total"] > 0], style, urls)


def output_results(df_unsorted, style="SHORT", urls=True):
    """
    Format a dataframe with the results
    """
    df = df_unsorted.sort_values(by=["Component"])
    if style == "SHORT":
        for index, rec in df.iterrows():
            url = "" if not urls else rec["URL"]
            print(f"{rec['Project']} {rec['Component']} {rec['Version']} {url}")
    if style == "HTML":
        if df.empty:
            return
        print("<ul>")
        last_group = None
        for index, rec in df.iterrows():
            if last_group != rec["Component"]:
                print(
                    f"<li><a href='{rec['URL']}'>{rec['Component']} {rec['Version']}</a> affects "
                )
                last_group = rec["Component"]
            print(rec["Project"] + " ")
        print("</ul>")
    if style == "PANDAS":
        print(df.to_string(index=False, header=False))
    if style == "CSV":
        output = StringIO()
        df.to_csv(output, index=False, header=False)
        print(output.getvalue())
    if style == "JSON":
        output = StringIO()
        df.to_json(output, orient="records")
        print(output.getvalue())


def cves(project_name,version_name,hub=None):
    hub = hub or HubInstance()
    """
    Return a json object with the stats of the project.
    :param str project: The project name in blackduck
    :param str version: The version name in blackduck
    :param bool operational: whether to include operational risks (security risks only otherwise)
    :param dict headers: headers for resulting frame
    :param int tree : level of indentation fo tree print -1 for no tree
    """
    project = hub.get_project_by_name(project_name)
    if not project:
        raise NameError("Project name invalid/not found.")

    project_id = project["_meta"]["href"].split("/")[-1]
    version = hub.get_version_by_name(project, version_name)
    if not version:
        eprint(f"!!??? {project_name} {version_name}")
        raise NameError("Version name invalid/not found.")
    version_id = version["_meta"]["href"].split("/")[-1]
    bom_components = None

    bom = hub.get_vulnerable_bom_components(
        version, limit="999"
    )  
    df = pd.DataFrame(
        {
            "Component": [],
            "CVE": [],
            "CVE NAME": [],
            "CVE DESCRIPTION": [],
            "SCORE": [],
            "REMEDIATION": [],
            "URL": [],
            "CWEID": [],
        }
    )

    for component in bom["items"]:
        compName = component.get("componentName", "Missing")
        cve = component.get("vulnerabilityWithRemediation", "Missing")
        cve_name = cve.get("vulnerabilityName")
        cve_description = cve.get("description")
        score = cve.get("overallScore")
        remediation = cve.get("remediationStatus")
        cweId = cve.get("cweId")
        # TODO: point to specific component in link
        cve_url = f"https://blackduck.trendmicro.com/ui/projects/{project_id}/versions/{version_id}/vulnerability-bom"
        df.loc[len(df)] = [
            compName,
            cve_description,
            cve_name,
            cve_description,
            score,
            remediation,
            cve_url,
            cweId,
        ]
    json_data = json.dumps(df.to_dict("records"))
    return json_data


def stats(
    project_name,
    version_name,
    operational,
    cutoff,
    headers={
        "c": "Component",
        "v": "Version",
        "critical": "Critical Security Risk",
        "high": "High Security Risk",
        "medium": "Medium Security Risk",
        "low": "Low Security Risk",
    },
    tree=0,
    alternative_enpoint=False,
    hub=HubInstance,
):
    """
    Return a pandas frame with the stats of the project.
    :param str project: The project name in blackduck
    :param str version: The version name in blackduck
    :param bool operational: whether to include operational risks (security risks only otherwise)
    :param dict headers: headers for resulting frame
    :param int tree : level of indentation fo tree print -1 for no tree
    """
    hub = hub or HubInstance()
    project = hub.get_project_by_name(project_name)
    if not project:
        raise NameError("Project name invalid/not found.")

    project_id = project["_meta"]["href"].split("/")[-1]
    version = hub.get_version_by_name(project, version_name)
    if not version:
        eprint(f"Issue with {project_name} {version_name}")
        raise NameError("Version name invalid/not found.")
    version_id = version["_meta"]["href"].split("/")[-1]
    bom_components = None

    try:

        bom_components = hub.get_version_components(
            version,
            limit="999&filter=securityRisk%3Acritical&filter=securityRisk%3Ahigh&filter=securityRisk%3Amedium&filter=securityRisk%3Alow",
        )
    except Exception as e:
        eprint(e)
        raise RuntimeError("Configuration file may be missing or invalid")

    projectlist = []
    compnamelist = []
    compversionlist = []
    compurllist = []
    critsecrisklist = []
    highsecrisklist = []
    medsecrisklist = []
    lowsecrisklist = []

    total_df = pd.DataFrame(
        {
            "Project": [],
            "Component": [],
            "Version": [],
            "URL": [],
            headers["critical"]: [],
            headers["high"]: [],
            headers["medium"]: [],
            headers["low"]: [],
        }
    )

    for component in bom_components["items"]:
        compName = component.get("componentName", "Missing")
        compVersion = component.get("componentVersionName", "Missing")
        if tree > -1:
            eprint(("\t" * tree) + component["componentName"])
        if component["componentType"] == "SUB_PROJECT":
            total_df = pd.concat(
                [
                    total_df,
                    stats(
                        compName,
                        compVersion,
                        operational,
                        cutoff,
                        headers=headers,
                        tree=tree + 1 if tree > -1 else -1,
                    ),
                ]
            )
            continue

        projectlist.append(project_name)
        securityRiskProfile = component["securityRiskProfile"]
        compnamelist.append(compName)
        compversionlist.append(compVersion)
        compurllist.append(component.get("componentVersion", "Missing"))
        lowsecrisklist.append(securityRiskProfile["counts"][2]["count"])
        medsecrisklist.append(securityRiskProfile["counts"][3]["count"])
        highsecrisklist.append(securityRiskProfile["counts"][4]["count"])
        critsecrisklist.append(securityRiskProfile["counts"][5]["count"])

    df = pd.DataFrame(
        {
            "Project": projectlist,
            "Component": compnamelist,
            "Version": compversionlist,
            "URL": compurllist,
            headers["critical"]: critsecrisklist,
            headers["high"]: highsecrisklist,
            headers["medium"]: medsecrisklist,
            headers["low"]: lowsecrisklist,
        }
    )

    total_df = pd.concat([total_df, df])
    if cutoff == "medium":
        total_df.drop(columns=[headers["low"]], inplace=True)
    if cutoff == "high":
        total_df.drop(columns=[headers["medium"], headers["low"]], inplace=True)
    if cutoff == "critical":
        total_df.drop(
            columns=[headers["medium"], headers["low"], headers["high"]], inplace=True
        )
    return total_df.drop_duplicates()


