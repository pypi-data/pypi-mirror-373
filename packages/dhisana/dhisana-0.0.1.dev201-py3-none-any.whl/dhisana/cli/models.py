import click

@click.group()
def model_cli():
    """Commands for managing models."""
    pass

@model_cli.command()
def list():
    """List all available models."""
    # Example placeholder logic for listing models
    click.echo("Available models: model1, model2, model3")

@model_cli.command()
@click.argument('model_name')
def add(model_name):
    """Add a new model."""
    # Example placeholder logic for adding a model
    click.echo(f"Model '{model_name}' has been added.")

@model_cli.command()
@click.argument('model_name')
def delete(model_name):
    """Delete an existing model."""
    # Example placeholder logic for deleting a model
    click.echo(f"Model '{model_name}' has been deleted.")
