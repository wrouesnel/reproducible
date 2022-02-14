"""Entrypoint for reproducible when run as a module"""
import sys
from . import reproducible

reproducible.main(sys.argv[1:])
