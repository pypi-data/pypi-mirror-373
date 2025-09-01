import argparse
from .server import mcp
def main():
    parser = argparse.ArgumentParser(
        description="Gives you the ability to convert mysql SQL to ElasticSearch DSL."
    )
    parser.parse_args()
    mcp.run()
if __name__ == "__main__":
    main()