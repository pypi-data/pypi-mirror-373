"""Build an Entanglement graph from a yaml file or directory of yaml files."""

from typing import Union, Dict
from pathlib import Path
import warnings
import yaml

from requests.exceptions import HTTPError
from retry import retry
from rich.tree import Tree
from rich import print
from tqdm import tqdm
import shapely
import click

import geodesic
import geodesic.boson.middleware as middleware
from geodesic.cql import CQLFilter


def resolve_id(id: str, tags: Dict[str, str]) -> str:
    """Resolve an id to a full name using tags or UIDs.

    Args:
        id (str): The id to resolve.
        tags (Dict[str, str]): A dictionary of tags to full names.
    """
    if id in tags.keys():  # its an internal tag
        return tags[id]
    elif ":" in id:  # it looks like a full name
        return id
    elif id.startswith("0x"):  # it looks like an UID
        try:
            obj = geodesic.Object().load(uid=id)
        except Exception as e:
            raise NameError(f"[bold red]Error loading object with uid {id}: {e}")

        return obj.full_name


def create_nodes(nodes: list, proj: geodesic.Project, dry_run: bool = False, tree: Tree = None):
    """Create and save simple nodes from a list of dictionaries, and gather dataset specs.

    Args:
        nodes (list): A list of dictionaries representing nodes.
        proj (geodesic.Project): The project to add nodes to.
        dry_run (bool, optional): Dry run. Don't commit anything to Entanglement. Defaults to False.
        tree (Tree, optional): A rich Tree object to add node names to. Defaults to None.
    """
    add_nodes = []
    add_ds = []
    tags = {}
    connections = []
    for node in tqdm(nodes, desc="Creating nodes"):
        try:
            obj_class = node.get("object_class", "*")

            full_name = ":".join(
                [
                    obj_class,
                    node.get("domain", "*"),
                    node.get("category", "*"),
                    node.get("type", "*"),
                    node.get("name", "*"),
                ]
            )

            tag = node.get("tag")
            if tag:
                tags[tag] = full_name
                del node["tag"]

            # replace 'self' tags
            if "connections" in node:
                new_connections = node.pop("connections")
                for connection in new_connections:
                    if connection.get("subject") == "self":
                        connection["subject"] = full_name

                    if connection.get("object") == "self":
                        connection["object"] = full_name

                    connections.append(connection)

            # handle dataset definitions
            if obj_class == "dataset":
                method = node.pop("method")

                if not method:
                    raise ValueError(
                        "[bold red]Error creating dataset node: 'method' key must be specified"
                    )

                ds_spec = prep_datasets(node, method, proj)
                if ds_spec:
                    add_ds.append(ds_spec)

                if tag:
                    tree.add(f"[magenta]{node['name']} (tag: {tag})")
                else:
                    tree.add(f"[magenta]{node['name']}")

            # handle node geometry
            else:
                if "geometry" in node:
                    try:
                        node["geometry"] = shapely.from_wkt(node["geometry"]).__geo_interface__
                    except Exception as e:
                        raise ValueError(
                            f"[bold red]Error parsing node geometry: {node['name']}" f"{e}"
                        )

                obj = geodesic.Object(**node, project=proj)
                add_nodes.append(obj)

                if tag:
                    tree.add(f"[magenta]{obj.name} (tag: {tag})")
                else:
                    tree.add(f"[magenta]{obj.name}")

        except Exception as e:
            raise ValueError(f"[bold red]Error creating object: {node['name']}, {e}")

    print(tree)
    if not dry_run:
        print("Adding nodes to project...")
        geodesic.entanglement.add_objects(add_nodes, project=proj, show_progress=True)
    return add_nodes, add_ds, tags, connections


def prep_middleware(node):
    """Prepare middleware for a dataset."""
    midware_steps = []
    for step in node["middleware"]:
        if "method" not in step:
            raise ValueError(
                f"[bold red]Error preparing middleware for dataset {node['name']}: "
                f"method must be provided"
            )

        step_split = step.pop("method").split(".")
        method_name = step_split[0]
        if len(step_split) == 2:
            cls_name, method_name = step_split
            warnings.warn("Usage of <class>.<method> is deprecated. Use <method> instead.")
        method = getattr(middleware, method_name)
        midware = method(**step)

        midware_steps.append(midware)

    node["middleware"] = midware_steps
    return node


def prep_datasets(node: dict, method: str, proj: geodesic.Project):
    """Prepare node specs for datasets."""
    ds_spec = {"method": method}

    if "middleware" in node:
        node = prep_middleware(node)

    if "filter" in node:
        node["filter"] = CQLFilter(node["filter"])

    # handle from_<format> methods
    if method.startswith("from_"):
        del node["object_class"]
        ds_spec = {"method": getattr(geodesic.Dataset, method), "kwargs": node}
        return ds_spec

    if "dataset" not in node.keys():
        raise ValueError(
            f"[bold red]Error preparing dataset {node['name']}: dataset must be provided"
        )

    ds_spec["dataset"] = node.pop("dataset")

    if "dataset_project" in node:
        ds_spec["dataset_project"] = geodesic.get_project(node.pop("dataset_project"))
    else:
        ds_spec["dataset_project"] = proj

    # prepare WKT intersect geometry
    if "intersects" in node:
        node["intersects"] = shapely.from_wkt(node["intersects"]).__geo_interface__

    # for join: prepare right dataset reference
    if method == "join":
        if "right_dataset" in node:
            ds_spec["right_dataset"] = node.pop("right_dataset")

        if "right_dataset_project" in node:
            ds_spec["right_dataset_project"] = geodesic.get_project(
                node.pop("right_dataset_project")
            )
        else:
            ds_spec["right_dataset_project"] = proj

    # for union: prepare other dataset references
    elif method == "union":
        other_datasets = []
        for ods_spec in node.pop("others"):
            if "dataset" not in ods_spec.keys():
                raise ValueError(
                    f"[bold red]Error preparing dataset {node['name']}: "
                    f"other dataset path must be provided"
                )

            # handle other dataset project
            if "project" in ods_spec:
                ods_spec["project"] = geodesic.get_project(ods_spec.pop("project"))
            else:
                ods_spec["project"] = proj

            other_datasets.append(ods_spec)
        node["others"] = other_datasets

    node["project"] = proj
    ds_spec["kwargs"] = node
    return ds_spec


@retry(HTTPError, tries=30, delay=10)
def save_ds(ds: geodesic.Dataset, reindex: bool = False):
    """Save a dataset and reindex if necessary. Retry on HTTPError."""
    ds.save()
    try:
        if reindex:
            ds.reindex()
    except HTTPError:
        pass
    return ds


def create_datasets(
    datasets: list,
    proj: geodesic.Project,
    dry_run: bool = False,
    reindex: bool = False,
):
    """Create and save datasets from a list of dictionaries."""
    for ds_spec in datasets:
        method = ds_spec["method"]

        # handle from_<format> datasets
        if callable(method):
            ds_spec["proj"] = proj
            ds = method(**ds_spec["kwargs"])
            if not dry_run:
                save_ds(ds, reindex)

        # handle other dataset types
        elif method in ["view", "join", "union"]:
            if dry_run:
                # For now just forget about this stuff. We need to check for datasets that will be
                # created in this run of the tool.
                continue

            ds_obj_class, ds_domain, ds_category, ds_type, ds_name = ds_spec["dataset"].split(":")
            ds_proj = ds_spec.pop("dataset_project", proj)

            base_ds = geodesic.get_objects(
                search=f"name='{ds_name}'",
                domain=ds_domain,
                category=ds_category,
                type=ds_type,
                object_class=ds_obj_class,
                project=ds_proj.uid,
            )
            if len(base_ds) == 0:
                if dry_run:
                    # during dry run, the objects might be in the yaml not in
                    # geodesic so check the tags
                    if ds_spec["dataset"] not in ds_spec.values():
                        raise ValueError(
                            "Error finding base dataset: no results in Geodesic or current yaml "
                            f"for {ds_spec['dataset']}"
                        )
                else:
                    raise ValueError(
                        f"[bold red]Error finding base dataset: no results for {ds_spec['dataset']}"
                        f"in project {ds_proj.name}"
                    )
            elif len(base_ds) > 1:
                raise ValueError(
                    f"[bold red]Error finding base dataset: too many results for "
                    f"{ds_spec['dataset']} in project {ds_proj.name}"
                )
            else:
                base_ds = base_ds[0]

            if method == "view":
                ds = base_ds.view(**ds_spec["kwargs"])
                if not dry_run:
                    save_ds(ds, reindex)

            elif method == "join":
                rds_obj_class, rds_domain, rds_category, rds_type, rds_name = ds_spec[
                    "right_dataset"
                ].split(":")
                rds_proj = ds_spec.pop("right_dataset_project", proj)

                right_ds = geodesic.get_objects(
                    search=f"name='{rds_name}'",
                    domain=rds_domain,
                    category=rds_category,
                    type=rds_type,
                    object_class=rds_obj_class,
                    project=rds_proj.uid,
                )
                if len(right_ds) == 0:
                    raise ValueError(
                        f"[bold red]Error finding right dataset: "
                        f"no results for {ds_spec['right_dataset']} in project {rds_proj.name}"
                    )
                if len(right_ds) > 1:
                    raise ValueError(
                        f"[bold red]Error finding right dataset: too many results for "
                        f"{ds_spec['right_dataset']} in project {rds_proj.name}"
                    )
                else:
                    right_ds = right_ds[0]
                    ds_spec["kwargs"]["right_dataset"] = right_ds

                ds = base_ds.join(**ds_spec["kwargs"])
                if not dry_run:
                    save_ds(ds, reindex)

            elif method == "union":
                other_datasets = []
                for ods_spec in ds_spec["kwargs"].pop("others"):
                    ods_obj_class, ods_domain, ods_category, ods_type, ods_name = ods_spec[
                        "dataset"
                    ].split(":")
                    ods_proj = ods_spec["project"]

                    new_ods = geodesic.get_objects(
                        search=f"name='{ods_name}'",
                        domain=ods_domain,
                        category=ods_category,
                        type=ods_type,
                        object_class=ods_obj_class,
                        project=ods_spec["project"].uid,
                    )
                    if len(new_ods) == 0:
                        raise ValueError(
                            f"[bold red]Error finding other dataset: "
                            f"no results for {ods_spec['dataset']} in project {ods_proj.name}"
                        )
                    if len(new_ods) > 1:
                        raise ValueError(
                            f"[bold red]Error finding other dataset: too many results for "
                            f"{ods_spec['dataset']} in project {ods_proj.name}"
                        )
                    else:
                        other_datasets.append(new_ods[0])

                ds_spec["kwargs"]["others"] = other_datasets

                ds = base_ds.union(**ds_spec["kwargs"])
                if not dry_run:
                    save_ds(ds, reindex)


def create_connections(conns: list, proj: geodesic.Project, tags: Dict, dry_run: bool = False):
    """Create and save connections from a list of dictionaries."""
    added_conns = []
    for conn in tqdm(conns, desc="Creating connections"):
        if conn.get("subject") is None or conn.get("object") is None:
            # If a subject/object could not be found, skip this connection
            continue

        # Need to query for each node since the connection type wants the full object.
        s_proj, s_obj_class, s_domain, s_category, s_type, s_name = conn["subject"].split(":")
        o_proj, o_obj_class, o_domain, o_category, o_type, o_name = conn["object"].split(":")

        s = geodesic.get_objects(
            search=f"name='{s_name}'",
            domain=s_domain,
            category=s_category,
            type=s_type,
            object_class=s_obj_class,
            project=s_proj,
        )

        if len(s) == 0:
            if dry_run:
                # during dry run, the objects might be in the yaml not in geodesic so check the tags
                if conn["subject"] not in tags.values():
                    raise ValueError(
                        f"Error finding subject: no results in Geodesic or current"
                        f" yaml for {conn['subject']}"
                    )
            else:
                raise ValueError(
                    f"[bold red]Error finding subject: no results for in Geodesic {conn['subject']}"
                )
        if len(s) > 1:
            raise ValueError(
                f"[bold red]Error finding subject: too many results for {conn['subject']}"
            )

        o = geodesic.get_objects(
            search=f"name='{o_name}'",
            domain=o_domain,
            category=o_category,
            type=o_type,
            object_class=o_obj_class,
            project=o_proj,
        )
        if len(o) == 0:
            if dry_run:
                # during dry run, the objects might be in the yaml not in geodesic so check the tags
                if conn["object"] not in tags.values():
                    raise ValueError(
                        f"Error finding object: no results in Geodesic or current yaml"
                        f" for {conn['object']}"
                    )
            else:
                raise ValueError(f"[bold red]Error finding object: no results for {conn['object']}")
            continue
        if len(o) > 1:
            raise ValueError(
                f"[bold red]Error finding object: too many results for {conn['object']}"
            )

        subj = s[0]
        obj = o[0]
        try:
            c = geodesic.Connection(subject=subj, object=obj, predicate=conn["predicate"])
        except Exception as e:
            print(f"[bold red]Error creating connection: {conn['subject']}")
            print(f"[bold red]{e}")
        added_conns.append(c)

    if not dry_run:
        geodesic.entanglement.add_connections(added_conns, project=proj, show_progress=True)


def expand_dataset_tags(tags: dict, dataset_specs: list, proj: geodesic.Project):
    """Expand dataset tags to full names."""
    good_datasets = []
    for ds_spec in dataset_specs:
        # handle 'from_' datasets (no special treatment needed)
        if callable(ds_spec["method"]):
            good_datasets.append(ds_spec)

        # handle join/view/union base dataset reference
        elif ds_spec["method"] in ["view", "join", "union"]:
            ds_spec["dataset"] = resolve_id(ds_spec["dataset"], tags)

            # handle join right dataset reference
            if ds_spec["method"] == "join":
                ds_spec["right_dataset"] = resolve_id(ds_spec["right_dataset"], tags)

            # handle union other dataset references
            if ds_spec["method"] == "union":
                other_datasets = []
                for ods_spec in ds_spec["kwargs"].pop("others"):
                    new_ods = {"project": ods_spec.get("project", proj)}

                    new_ods["dataset"] = resolve_id(ods_spec["dataset"], tags)

                    other_datasets.append(new_ods)

                ds_spec["kwargs"]["others"] = other_datasets

            good_datasets.append(ds_spec)
    return good_datasets


def expand_connection_tags(tags: dict, connections: list, proj: geodesic.Project):
    """Expand connection tags to full names."""
    good_connections = []

    for connection in connections:
        if "subject_project" in connection:
            try:
                s_proj = geodesic.get_project(connection.pop("subject_project")).uid
            except ValueError:
                raise ValueError("Error preparing connection: 'subject_project' not found")
        else:
            s_proj = proj.uid

        if "object_project" in connection:
            try:
                o_proj = geodesic.get_project(connection.pop("object_project")).uid
            except ValueError:
                raise ValueError("Error preparing connection: 'object_project' not found")
        else:
            o_proj = proj.uid

        if set(connection.keys()) != {"subject", "predicate", "object"}:
            raise ValueError(
                "Error preparing connection: Must have 'subject', 'predicate', and 'object'"
                " to make connection"
            )
        if "subject" not in connection.keys():
            raise ValueError(
                "Error preparing connection: subject name, tag, or uid must be provided"
            )
        if "object" not in connection.keys():
            raise ValueError(
                "Error preparing connection: object name, tag, or uid must be provided"
            )

        connection["subject"] = f'{s_proj}:{resolve_id(connection["subject"], tags)}'
        connection["object"] = f'{o_proj}:{resolve_id(connection["object"], tags)}'

        good_connections.append(connection)

    return good_connections


def build_graph_from_yaml(
    file: Union[str, Path],
    project: geodesic.Project = None,
    dry_run: bool = False,
    reindex: bool = False,
    rebuild: bool = False,
):
    """Build a graph from a yaml file or directory of yaml files.

    Args:
        file (Union[str, Path]): Path to the yaml files or directory of yaml files.
        project (geodesic.Project, optional): Project to add nodes and connections to.
            Defaults to None.
        dry_run (bool, optional): Dry run. Don't commit anything to Entanglement. Defaults to False.
        reindex (bool, optional): Reindex datasets on creation. Defaults to False.
        rebuild (bool, optional): Rebuild entire graph. Deletes all nodes before creating new ones.
            Defaults to False.

    """
    data_path = Path(file) if isinstance(file, str) else file

    if data_path.is_dir():
        yaml_files = list(data_path.glob("*.yaml"))
    else:
        yaml_files = [data_path]

    if not yaml_files:
        raise ValueError(f"No yaml files found in {data_path}")

    print(f"Building graph from {len(yaml_files)} yaml files...")

    proj = geodesic.set_active_project(project)

    root_tree = Tree(f"[bold purple]{str(data_path)}")

    if rebuild:
        print("[bold red]Clearing project for rebuild.")
        for obj in geodesic.get_objects():
            obj.delete()

    objects = []
    datasets = []
    connections = []
    tags = {}
    for file in yaml_files:
        with file.open() as f:
            file_nodes = yaml.safe_load(f)
            if file_nodes is None:
                continue

        if len(yaml_files) > 1:
            t = root_tree.add(f"[green]{file.name} ({len(file_nodes)} nodes)")
        else:
            t = root_tree

        add_objs, add_ds, new_tags, new_connections = create_nodes(
            nodes=file_nodes, proj=proj, dry_run=dry_run, tree=t
        )

        tag_collisions = set(tags.keys()).intersection(new_tags.keys())
        if len(tag_collisions) > 0:
            raise ValueError(
                "[bold red]Error creating connection: object tag collision on the"
                f"following tags: {tag_collisions}"
            )
        tags.update(new_tags)

        objects = objects + add_objs
        datasets = datasets + add_ds
        connections = connections + new_connections

    print(f"Nodes: {[n['name'] for n in objects]}")
    datasets = expand_dataset_tags(tags, datasets, proj)
    create_datasets(datasets=datasets, proj=proj, dry_run=dry_run, reindex=reindex)

    connections = expand_connection_tags(tags, connections, proj)
    create_connections(conns=connections, proj=proj, tags=tags, dry_run=dry_run)

    return objects, datasets, connections


@click.command("build_graph")
@click.option("-f", "--file", type=str, help="Path to the yaml files or directory of yaml files.")
@click.option(
    "-p",
    "--project",
    type=str,
    envvar="PROJECT_ID",
    help="Project to add nodes and connections to.",
)
@click.option("--dry_run", is_flag=True, help="Dry run. Don't commit anything to Entanglement.")
@click.option("--reindex", is_flag=True, help="Reindex datasets on creation.")
@click.option(
    "--rebuild",
    is_flag=True,
    help="Rebuild entire graph. Deletes all nodes before creating new ones. "
    "Only use this option if your yaml files contain *all* of your nodes.",
)
def cli(
    file: Union[str, Path],
    project: geodesic.Project = None,
    dry_run: bool = False,
    reindex: bool = False,
    rebuild: bool = False,
):
    """CLI entrypoint for building a graph from yaml files."""
    build_graph_from_yaml(file, project, dry_run, reindex, rebuild)


if __name__ == "__main__":
    cli()
