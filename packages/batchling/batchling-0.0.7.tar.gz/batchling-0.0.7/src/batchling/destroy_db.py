from batchling.db.session import destroy_db, get_db

if __name__ == "__main__":
    with get_db() as db:
        destroy_db()
