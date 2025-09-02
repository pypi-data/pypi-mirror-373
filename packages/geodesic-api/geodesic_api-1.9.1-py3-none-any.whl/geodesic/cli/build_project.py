from typing import Union
from pathlib import Path

# ruamel allows maintaining *most* formatting and comments in original yaml file
# the slightly strange approach at editing the project yaml is to maintain this persistence
# could always switch this back to a normal `import yaml` with minimal changes
from ruamel import yaml
import click

import geodesic
from geodesic.cli.build_graph import build_graph_from_yaml


def build_project_from_yaml(
    file: Union[str, Path] = "project.yaml",
    project: str = None,
    dry_run: bool = False,
    skip_graph: bool = False,
    reindex: bool = False,
    rebuild: bool = False,
):
    spec_path = Path(file) if isinstance(file, str) else file

    with open(spec_path, "r") as f:
        all_specs = yaml.load(f, Loader=yaml.RoundTripLoader)

    proj_ndx = [spec["name"] for spec in all_specs].index(project) if project is not None else 0
    proj_spec = all_specs[proj_ndx]
    if project is None:
        print(f'No project name provided. Using project "{proj_spec["name"]}"')

    if "uid" in proj_spec:
        proj_uid = all_specs[proj_ndx]["uid"]
        project = geodesic.get_project(proj_uid)
        print(f"Updating project: {project.name}")

        if project.name != proj_spec["name"]:
            print(f'Updating project name: "{project.name}" -> "{proj_spec["name"]}"')
            project.name = proj_spec["name"]

        if project.alias != proj_spec["alias"]:
            print(f'Updating project alias: "{project.alias}" -> "{proj_spec["alias"]}"')
            project.alias = proj_spec["alias"]

        if project.description != proj_spec["description"]:
            print(
                'Updating project description: '
                f'"{project.description}" -> "{proj_spec["description"]}"'
            )
            project.description = proj_spec["description"]

        if not dry_run:
            project.delete()
            project.pop("uid")
            project.create()

    else:
        print(f'Creating project: {proj_spec["name"]}')
        project = geodesic.Project(
            name=proj_spec["name"],
            alias=proj_spec["alias"],
            description=proj_spec["description"],
            keywords=proj_spec.get("keywords", []),
        )

        if not dry_run:
            project.create()
            # Write new uid back to yaml file
            all_specs[proj_ndx].insert(0, "uid", project.uid)
            with open(spec_path, "w") as f:
                yaml.dump(all_specs, f, Dumper=yaml.RoundTripDumper)

    if "permissions" in proj_spec:
        for user in proj_spec["permissions"]:
            user_permissions = {"read": user["read"], "write": user["write"]}
            if user_permissions != project.get_permissions(user["user"]):
                print(
                    'Updating permissions for user:'
                    f'{user.get("name", user["user"])} {user_permissions}'
                )
                if not dry_run:
                    project.update_permissions(user["user"], user_permissions)

    if ("nodes_path" in proj_spec) and (not skip_graph):
        print(f'Building project graph from nodes path: {proj_spec["nodes_path"]}')
        build_graph_from_yaml(
            file=proj_spec["nodes_path"],
            project=project,
            dry_run=dry_run,
            reindex=reindex,
            rebuild=rebuild,
        )


@click.command("build_project")
@click.option(
    "-f", "--file", type=str, help="Path to the yaml files to use.", default="project.yaml"
)
@click.option("-p", "--project", type=str, help="Project to add nodes and connections to.")
@click.option("--dry_run", is_flag=True, help="Dry run. Don't commit anything to Entanglement.")
@click.option("--skip_graph", is_flag=True, help="Skip graph build step.")
@click.option("--reindex", is_flag=True, help="Reindex datasets on creation.")
@click.option(
    "--rebuild",
    is_flag=True,
    help="Rebuild entire graph. Deletes all nodes before creating new ones. "
    "Only use this option if your yaml files contain *all* of your nodes.",
)
def cli(
    file: Union[str, Path] = "project.yaml",
    project: str = None,
    dry_run: bool = False,
    skip_graph: bool = False,
    reindex: bool = False,
    rebuild: bool = False,
):
    build_project_from_yaml(file, project, dry_run, skip_graph, reindex, rebuild)


if __name__ == "__main__":
    build_project_from_yaml()
