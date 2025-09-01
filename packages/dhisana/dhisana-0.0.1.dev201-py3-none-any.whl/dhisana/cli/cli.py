import click
from .models import model_cli
from .datasets import dataset_cli
from .predictions import prediction_cli

@click.group()
def cli():
    """Dhisana AI SDK CLI."""
    pass

# Add command groups from the respective CLI files
cli.add_command(model_cli)
cli.add_command(dataset_cli)
cli.add_command(prediction_cli)

def main():
    cli()

if __name__ == '__main__':
    main()
