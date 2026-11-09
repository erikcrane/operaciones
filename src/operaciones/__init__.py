"""Generador de fichas PDF de ejercicios de matemáticas (multiplicaciones, divisiones...)."""


def main():
    """Punto de entrada del comando `operaciones` (ver pyproject.toml)."""
    from .cli import main as main_cli

    main_cli()
