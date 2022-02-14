"""Entrypoint for reproducible when run as a module"""
import sys
from . import reproducible


def main() -> None:
    """Main entry point when function is executed as a module"""
    reproducible.main(sys.argv[1:])
