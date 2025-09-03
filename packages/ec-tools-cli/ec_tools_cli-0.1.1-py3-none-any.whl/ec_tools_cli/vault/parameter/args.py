import argparse
import os

from ec_tools_cli.vault.parameter.parameter import Method, Parameter

DETAILED_DOC = """
Vault CLI tools for important file/password management with AES encryption.
Support:
  vault-cli list # List all stored items
  vault-cli insert -p <password> -k <key> -v <value> # Add a new item through command line
  vault-cli insert -p <password> -k <key> -f <file_path> # Add a new item through file
  vault-cli insert -p <password> -k <key> # Add a new item through interactive prompt
  vault-cli get -p <password> -k <key> # Retrieve an item in cli
  vault-cli get -p <password> -k <key> -o <output_file_path> # Retrieve an item and save to file
  vault-cli delete -k <key> # Delete an item
"""


def get_args() -> Parameter:
    parser = argparse.ArgumentParser(
        description="Vault CLI",
        epilog=DETAILED_DOC,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    home_path = os.path.expanduser("~")
    parser.add_argument(
        "-db",
        "--db-path",
        default=f"{home_path}/.ec_tools/ec_tools.db",
        help="Path to the SQLite database file",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="List all stored items")
    insert_parser = subparsers.add_parser("insert", help="Insert a new item")
    get_parser = subparsers.add_parser("get", help="Get an item")
    delete_parser = subparsers.add_parser("delete", help="Delete an item")

    # list parser has no additional arguments

    # insert parser
    insert_parser.add_argument("-p", "--password", help="Master password")
    insert_parser.add_argument("-k", "--key", help="Key for the item")
    insert_parser.add_argument("-v", "--value", help="Value for the item")
    insert_parser.add_argument("-f", "--file", help="File path to read the value from")

    # get parser
    get_parser.add_argument("-p", "--password", help="Master password")
    get_parser.add_argument("-k", "--key", help="Key for the item")
    get_parser.add_argument("-o", "--output", help="Output file path to save the value")
    get_parser.add_argument("-s", "--silent", action="store_true", help="Run silently with result only")

    # delete parser
    delete_parser.add_argument("-k", "--key", help="Key for the item")
    args = parser.parse_args()
    return Parameter(
        method=Method.from_str(args.command),
        **{k: v for k, v in vars(args).items() if k != "command"},
    )
