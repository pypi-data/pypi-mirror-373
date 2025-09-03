import os
from pathlib import Path

import pandas as pd
import typer
from label_studio_sdk import LabelStudio
from yarl import URL

from lscli.vad.annotation import annotation_df

app = typer.Typer()


@app.command()
def annotation_df_cli(
    task_id: int = typer.Argument(..., help="Task ID"),
    df_path: Path = typer.Argument(..., help="Path to save the annotation dataframe"),
):
    api_key = os.getenv("LABEL_STUDIO_API_KEY")
    base_url = os.getenv("LABEL_STUDIO_BASE_URL")
    if not api_key:
        typer.echo("Error: LABEL_STUDIO_API_KEY environment variable is not set.")
        raise typer.Exit(code=1)
    if not base_url:
        typer.echo("Error: LABEL_STUDIO_BASE_URL environment variable is not set.")
        raise typer.Exit(code=1)

    client = LabelStudio(
        api_key=api_key,
        base_url=URL(base_url),
    )
    df = pd.read_csv(df_path, sep="\t")
    annotation_df(client, task_id, df)


def main():
    app()


if __name__ == "__main__":
    app()
