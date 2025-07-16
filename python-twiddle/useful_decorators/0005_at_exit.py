import atexit
import sqlite3

db_connection = sqlite3.connect("db.sqlite3")

def init_db():
    db_connection.execute("""
            CREATE TABLE IF NOT EXISTS timestamps (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

    print("Database initialised.")

def write_timestamp(id: int) -> None:
    """
    Write a timestamp record to the database.

    Args:
        id: The ID of the associated record
    """
    try:
        db_connection.execute("""
            INSERT INTO timestamps (id, timestamp)
            VALUES (?, CURRENT_TIMESTAMP)
        """, (id,))
        db_connection.commit()
    except Exception as e:
        print(f"Error writing timestamp: {e}")


def print_timestamps() -> None:
    """
    Print all timestamps from the database in a formatted way.
    """
    cursor = db_connection.cursor()
    try:
        cursor.execute("""
            SELECT id, timestamp 
            FROM timestamps 
            ORDER BY timestamp DESC
        """)

        records = cursor.fetchall()

        if not records:
            print("No timestamps found.")
            return

        print("\nTimestamps:")
        print("-" * 50)
        print(f"{'ID':^5} | {'Timestamp':^25}")
        print("-" * 50)

        for id, timestamp in records:
            print(f"{id:^5} | {timestamp:^25}")

        print("-" * 50)
        print(f"Total records: {len(records)}")

    except Exception as e:
        print(f"Error reading timestamps: {e}")
    finally:
        cursor.close()

@atexit.register
def exit_handler():
    db_connection.commit()
    print_timestamps()
    db_connection.close()
    print("Database closed.")

if __name__ == "__main__":
    init_db()
    write_timestamp(1)
    write_timestamp(2)
    write_timestamp(3)
    write_timestamp(1) # will throw an exception due to the duplicate key

