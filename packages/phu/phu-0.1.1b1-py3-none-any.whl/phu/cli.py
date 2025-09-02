from __future__ import annotations
from pathlib import Path
# import sys
import typer

from phu import __version__
from .seqclust import SeqClustConfig, Mode, _seqclust
from ._exec import CmdNotFound

app = typer.Typer(
    help="Phage utilities CLI",
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
    no_args_is_help=True
)

@app.callback(invoke_without_command=True)
def _root(ctx: typer.Context) -> None:
    # any global init here (env checks, logging setup, etc.)
    if ctx.invoked_subcommand is None and not ctx.resilient_parsing:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)  # exit code 0 when no subcommand is given

@app.command("seqclust")
def seqclust(
    mode: Mode = typer.Option(
        ..., "--mode", help="dereplication | votu-clustering | spp-clustering"
    ),
    input_contigs: Path = typer.Option(
        ..., "--input-contigs", exists=True, readable=True, help="Input FASTA"
    ),
    output_folder: Path = typer.Option(
        Path("clustered-contigs"), "--output-folder", help="Output directory"
    ),
    threads: int = typer.Option(
        0, "--threads", min=0, help="0=all cores; otherwise N threads"
    ),
):
    """
    Sequence clustering wrapper around external 'vclust' with three modes.
    """
    cfg = SeqClustConfig(
        mode=mode,
        input_contigs=input_contigs,
        output_folder=output_folder,
        threads=threads,
    )
    try:
        _seqclust(cfg)  # the runner command
    except FileNotFoundError as e:
        typer.echo(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except CmdNotFound as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        typer.echo(
            "Required executables on PATH: 'vclust' (or 'vclust.py') and 'seqkit'"
        )
        raise typer.Exit(1)


# @app.callback(invoke_without_command=True)
def main() -> None:
    app()

if __name__ == "__main__":
    main()
