from database.connection import get_connection


def upsert_user(username, display_name, role_name="tester", status="active"):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO findata_users (username, display_name, role_name, status)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    display_name = VALUES(display_name),
                    role_name = VALUES(role_name),
                    status = VALUES(status)
                """,
                (username, display_name, role_name, status),
            )
        connection.commit()
    return get_user(username)


def get_user(username):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM findata_users WHERE username = %s", (username,))
            return cursor.fetchone()


def add_watchlist_item(item_type, symbol, name, created_by="tester"):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO findata_watchlist (item_type, symbol, name, created_by)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    item_id = LAST_INSERT_ID(item_id)
                """,
                (item_type, symbol, name or symbol, created_by),
            )
            item_id = cursor.lastrowid
        connection.commit()
    return get_watchlist_item(item_id)


def list_watchlist_items(created_by=None):
    sql = "SELECT * FROM findata_watchlist"
    params = ()
    if created_by:
        sql += " WHERE created_by = %s"
        params = (created_by,)
    sql += " ORDER BY item_id DESC"

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return list(cursor.fetchall())


def get_watchlist_item(item_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM findata_watchlist WHERE item_id = %s", (item_id,))
            return cursor.fetchone()


def delete_watchlist_item(item_id):
    item = get_watchlist_item(item_id)
    if not item:
        return None

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM findata_watchlist WHERE item_id = %s", (item_id,))
        connection.commit()
    return item


def clear_watchlist_items(created_by=None):
    sql = "DELETE FROM findata_watchlist"
    params = ()
    if created_by:
        sql += " WHERE created_by = %s"
        params = (created_by,)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
        connection.commit()


def add_test_run_log(suite_name, passed_count, failed_count, duration_seconds):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO test_run_logs (suite_name, passed_count, failed_count, duration_seconds)
                VALUES (%s, %s, %s, %s)
                """,
                (suite_name, passed_count, failed_count, duration_seconds),
            )
            run_id = cursor.lastrowid
        connection.commit()
    return get_test_run_log(run_id)


def get_test_run_log(run_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM test_run_logs WHERE run_id = %s", (run_id,))
            return cursor.fetchone()
