#!/usr/bin/env python

def versions(hub, project_name):
    """
    Get all projects with the given name.
    :param hub: Hub instance
    :param project_name: Project name
    :return: List of projects
    """
    projects = hub.get_projects(limit=300, parameters={"q": "name:{}".format(project_name)})
    results = {"project": f"{project_name}", "versions": []}
    for project in projects['items']:
        project_versions = hub.get_project_versions(project)
        for version in project_versions['items']:
            results["versions"].append(version['versionName'])
    return results