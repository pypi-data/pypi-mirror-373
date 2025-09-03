import sys
import argparse

def main():
    parser = argparse.ArgumentParser(prog="denario")
    subparsers = parser.add_subparsers(dest="command")

    # `denario run`
    run_parser = subparsers.add_parser("run", help="Run the Denario Streamlit app")

    args = parser.parse_args()

    if args.command == "run":
        try:
            from denario_app.cli import run
            run()
        except ImportError:
            print("❌ DenarioApp not installed. Install with: pip install denario-app")
            sys.exit(1)
    else:
        parser.print_help()
