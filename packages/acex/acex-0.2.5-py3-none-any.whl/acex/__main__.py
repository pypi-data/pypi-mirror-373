
import argparse
from acex.makeapp import Make

def main():
    args = parse_args()
    if args.init:
        init_project(args.inventory)

def parse_args():
    parser = argparse.ArgumentParser(description="A simple example package.")
    parser.add_argument("--init", action='store_true', help="Init new project")
    parser.add_argument(
        "--inventory", 
        type=str,
        choices=["local"],
        help="Select type of inventory, default is 'local' which uses yml file")
    return parser.parse_args()

def init_project(inventory_type):
    m = Make()
    m.inventory_type = inventory_type
    m.build_skeleton()

if __name__ == "__main__":
    main()