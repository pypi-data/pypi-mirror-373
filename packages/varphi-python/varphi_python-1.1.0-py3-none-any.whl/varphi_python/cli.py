from pathlib import Path
import typer


def varphi_python(
    input_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to input Varphi source file"
    )
):
    """Compile a Varphi source code file to Python"""
    from varphi_devkit import compile_varphi
    from .core import VarphiToPythonCompiler
    typer.echo(compile_varphi(
        input_file.read_text(encoding="utf-8"),
        VarphiToPythonCompiler()
    ))

def main():
    typer.run(varphi_python)

if __name__ == "__main__":
    main()
