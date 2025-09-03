import argparse

from ec_tools.database import SqliteClient, SqliteQuery


def get_args():
    parser = argparse.ArgumentParser(description="Database CLI Tool")
    parser.add_argument(
        "-db",
        "--db-path",
        type=str,
        required=True,
        help="Path to the SQLite database file",
    )
    return parser.parse_args()


def process_db(sqlite_client: SqliteClient):
    list_all_tables = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = sqlite_client.execute(SqliteQuery(list_all_tables), commit=False)
    print("Tables in the database: ", tables)
    while True:
        sql = input("Enter SQL query (or 'exit' to quit): ")
        if sql.lower() == "exit" or sql == None:
            break
        try:
            results = sqlite_client.execute(SqliteQuery(sql), commit=True)
            for row in results:
                print(row)
        except Exception as e:
            print(f"Error executing query: {e}")


def main():
    args = get_args()
    print(f"Database path provided: {args.db_path}")
    sqlite_client = SqliteClient(args.db_path)
    process_db(sqlite_client)
