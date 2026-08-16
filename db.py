# export_conversation_data.py

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from sqlalchemy import MetaData, Table, inspect, select

from app.db.database import engine


# ============================================================
# CONFIG
# ============================================================

OUTPUT_FILE = Path("conversation_db_export.json")

# Tables we want to export.
#
# The script automatically checks which of these actually exist.
TABLES_TO_EXPORT = [
#    "conversations",
#    "conversation_messages",
#    "messages",
#    "buyer_leads",
"conversation_sessions"
]


# ============================================================
# JSON SERIALIZATION
# ============================================================

def json_serializer(value):
    """
    Convert PostgreSQL/Python values into JSON-safe values.
    """

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, bytes):
        return value.decode(
            "utf-8",
            errors="replace",
        )

    return str(value)


# ============================================================
# EXPORT TABLE
# ============================================================

def export_table(
    connection,
    metadata: MetaData,
    table_name: str,
):
    """
    Read every row from a table.
    """

    table = Table(
        table_name,
        metadata,
        autoload_with=connection,
    )

    stmt = select(table)

    # --------------------------------------------------------
    # ORDER RESULTS
    # --------------------------------------------------------

    # Prefer created_at when available.
    if "created_at" in table.c:
        stmt = stmt.order_by(
            table.c.created_at.asc()
        )

    elif "timestamp" in table.c:
        stmt = stmt.order_by(
            table.c.timestamp.asc()
        )

    elif "id" in table.c:
        stmt = stmt.order_by(
            table.c.id.asc()
        )

    result = connection.execute(
        stmt
    )

    rows = []

    for row in result:

        rows.append(
            dict(row._mapping)
        )

    return rows


# ============================================================
# MAIN
# ============================================================

def main():
    print()
    print("=" * 70)
    print("DATABASE CONVERSATION EXPORT")
    print("=" * 70)

    inspector = inspect(engine)

    existing_tables = set(
        inspector.get_table_names()
    )

    print()
    print("Tables found in database:")

    for table_name in sorted(existing_tables):
        print(
            f"  - {table_name}"
        )

    metadata = MetaData()

    export_data = {
        "exported_at": datetime.now().isoformat(),
        "tables": {},
    }

    # ========================================================
    # READ DATABASE
    # ========================================================

    with engine.connect() as connection:

        for table_name in TABLES_TO_EXPORT:

            print()
            print("-" * 70)

            if table_name not in existing_tables:

                print(
                    f"SKIP: {table_name} "
                    f"(table does not exist)"
                )

                continue

            print(
                f"Exporting: {table_name}"
            )

            rows = export_table(
                connection=connection,
                metadata=metadata,
                table_name=table_name,
            )

            export_data["tables"][
                table_name
            ] = rows

            print(
                f"Rows: {len(rows)}"
            )

    # ========================================================
    # SAVE JSON
    # ========================================================

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            export_data,
            file,
            indent=2,
            ensure_ascii=False,
            default=json_serializer,
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("EXPORT COMPLETE")
    print("=" * 70)

    for table_name, rows in export_data[
        "tables"
    ].items():

        print(
            f"{table_name:<25} {len(rows)} rows"
        )

    print()
    print(
        f"Saved to: {OUTPUT_FILE.resolve()}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()