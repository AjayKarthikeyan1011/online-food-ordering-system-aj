"""Entry point: python main.py [database_file]"""
import sys

from fos.cli import run

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "food_ordering.db")
