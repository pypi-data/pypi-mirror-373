import json

import click

import geodesic
import geodesic.config as config
from geodesic.cli.build_graph import cli as build_graph
from geodesic.cli.build_project import cli as build_project


@click.command()
@click.option(
    "-p",
    "--port",
    type=int,
    help="a port on your machine which can be used to run the code fetching "
    "server, removing the need to manually copy-paste auth code. "
    "If not specified, defaults to 8080. "
    "Please note that not all ports may be enabled in your OAuth provider's "
    "list of allowed callback URLs. This is only used for direct oauth2 "
    "authentication (uncommon).",
)
@click.option("-n", "--name", type=str, help="the name of the cluster to authenticate against")
@click.option(
    "-H",
    "--host",
    type=str,
    help="the host of the cluster to authenticate against"
    " (e.g. https://api.geodesic.seerai.space)",
)
def authenticate(port, name, host):
    """Authenticate geodesic."""
    geodesic.authenticate(port_override=port, name=name, host=host)


@click.command()
@click.argument("resource", type=click.Choice(["clusters", "active-config"]))
def get(resource):
    """List resources."""
    cm = config.ConfigManager()

    if resource == "clusters":
        clusters, active = cm.list_configs()
        for cluster in clusters:
            if cluster == active:
                print(f"[*] {cluster}")
            else:
                print(f"[ ] {cluster}")
    elif resource == "active-config":
        cfg = cm.get_active_config()
        print(json.dumps(cfg.to_dict(), indent=4, sort_keys=True))


@click.command()
@click.argument("resource", type=click.Choice(["cluster"]))
@click.argument("value")
def set(resource, value):
    """Set resource."""
    cm = config.ConfigManager()

    if resource == "cluster":
        active = value
        cm.set_active_config(active)


@click.command()
@click.argument("image", type=str)
def validate(image):
    """Validate a Tesseract model.

    IMAGE is the image and tag to validate, e.g. my-model-container:v0.0.1
    """
    import geodesic.tesseract.models.validate as _validate

    validator = _validate.ValidationManager(image=image, cli=True)
    validator.run()


@click.group()
def build():
    """build/manage projects or graphs."""


build.add_command(build_graph, "graph")
build.add_command(build_project, "project")


@click.group()
def main():
    pass


main.add_command(authenticate)
main.add_command(get)
main.add_command(set)
main.add_command(validate)
main.add_command(build)

if __name__ == "__main__":
    main()
