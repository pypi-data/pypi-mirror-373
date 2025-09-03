import click

import stadle.lib.util.bm_upload as bm_upload


@click.group()
@click.version_option()
def cli():
    print("Welcome to STADLE")


@cli.command()
@click.option(
    "--config_path",
    "-cfp",
    metavar="config_path",
    type=str,
    default="agent_config.json",
    help="Config file to use when sending base model"
)

def upload_model(config_path):
    print(f"Uploading base model using configuration file {config_path}")
    bm_upload.upload_bm_from_config(config_path)