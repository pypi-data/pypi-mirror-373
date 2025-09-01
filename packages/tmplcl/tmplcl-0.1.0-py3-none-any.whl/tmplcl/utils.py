import typer

SKIP_OPTION = typer.Option(
    parser=lambda _: _, hidden=True, expose_value=False
)
