import argparse

from zenx.engine import Engine
from zenx.discovery import discover_local_module


def main():
    """
    A dedicated script to run and debug spiders by accepting a spider name
    as a command-line argument.
    """
    # Step 1: Set up the argument parser
    parser = argparse.ArgumentParser(description="Zenx Debug Runner")
    parser.add_argument("spider", help="The name of the spider to run")
    args = parser.parse_args()

    # Step 2: Discover spiders (needs to run from the project root)
    discover_local_module("spiders")

    # Step 3: Create an instance of your engine
    engine = Engine(forever=False)

    # Step 4: Run the spider specified in the command-line argument
    target_spider = args.spider
    engine.run_spider(target_spider)


if __name__ == "__main__":
    main()
