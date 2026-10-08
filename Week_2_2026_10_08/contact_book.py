"""A small professional contact book backed by SQLite.

Run the interactive menu with:
    python contact_book.py

Or use command-line subcommands; see:
    python contact_book.py --help
"""

from __future__ import annotations

import argparse
import re
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Contact:
    """A contact record returned by the contact book."""

    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    company: str
    notes: str
    created_at: str
    updated_at: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class ContactBook:
    """Store and search contacts in a local SQLite database."""

    def __init__(self, database_path: str | Path = "contacts.db") -> None:
        self.database_path = Path(database_path)
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._create_schema()

    def _create_schema(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',
                company TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS contacts_email_unique
            ON contacts (email)
            WHERE email <> ''
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> ContactBook:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @staticmethod
    def _clean(value: str | None) -> str:
        return (value or "").strip()

    @classmethod
    def _validate(
        cls,
        first_name: str,
        last_name: str,
        email: str = "",
        phone: str = "",
    ) -> tuple[str, str, str, str]:
        first_name = cls._clean(first_name)
        last_name = cls._clean(last_name)
        email = cls._clean(email).lower()
        phone = cls._clean(phone)

        if not first_name:
            raise ValueError("First name is required.")
        if not last_name:
            raise ValueError("Last name is required.")
        if email and not EMAIL_PATTERN.fullmatch(email):
            raise ValueError("Please enter a valid email address.")
        if phone and not re.fullmatch(r"[0-9+().\-\s]{7,25}", phone):
            raise ValueError("Please enter a valid phone number.")
        return first_name, last_name, email, phone

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    @staticmethod
    def _row_to_contact(row: sqlite3.Row) -> Contact:
        return Contact(**dict(row))

    def add(
        self,
        first_name: str,
        last_name: str,
        email: str = "",
        phone: str = "",
        company: str = "",
        notes: str = "",
    ) -> Contact:
        first_name, last_name, email, phone = self._validate(
            first_name, last_name, email, phone
        )
        company, notes = self._clean(company), self._clean(notes)
        timestamp = self._now()
        try:
            cursor = self.connection.execute(
                """
                INSERT INTO contacts
                    (first_name, last_name, email, phone, company, notes,
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    first_name,
                    last_name,
                    email,
                    phone,
                    company,
                    notes,
                    timestamp,
                    timestamp,
                ),
            )
            self.connection.commit()
        except sqlite3.IntegrityError as error:
            raise ValueError("A contact with this email already exists.") from error
        return self.get(cursor.lastrowid)

    def get(self, contact_id: int) -> Contact:
        row = self.connection.execute(
            "SELECT * FROM contacts WHERE id = ?", (contact_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"No contact found with id {contact_id}.")
        return self._row_to_contact(row)

    def list_contacts(self) -> list[Contact]:
        rows = self.connection.execute(
            "SELECT * FROM contacts ORDER BY lower(last_name), lower(first_name), id"
        ).fetchall()
        return [self._row_to_contact(row) for row in rows]

    def search(self, query: str) -> list[Contact]:
        query = self._clean(query)
        if not query:
            return self.list_contacts()
        pattern = f"%{query}%"
        rows = self.connection.execute(
            """
            SELECT * FROM contacts
            WHERE first_name LIKE ? COLLATE NOCASE
               OR last_name LIKE ? COLLATE NOCASE
               OR email LIKE ? COLLATE NOCASE
               OR phone LIKE ? COLLATE NOCASE
               OR company LIKE ? COLLATE NOCASE
               OR notes LIKE ? COLLATE NOCASE
            ORDER BY lower(last_name), lower(first_name), id
            """,
            (pattern,) * 6,
        ).fetchall()
        return [self._row_to_contact(row) for row in rows]

    def update(self, contact_id: int, **changes: str) -> Contact:
        current = self.get(contact_id)
        values: dict[str, str] = {
            "first_name": current.first_name,
            "last_name": current.last_name,
            "email": current.email,
            "phone": current.phone,
            "company": current.company,
            "notes": current.notes,
        }
        unknown_fields = set(changes) - set(values)
        if unknown_fields:
            raise ValueError(f"Unknown contact fields: {', '.join(sorted(unknown_fields))}.")
        values.update({key: self._clean(value) for key, value in changes.items()})
        first_name, last_name, email, phone = self._validate(
            values["first_name"],
            values["last_name"],
            values["email"],
            values["phone"],
        )
        values.update(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
        )
        try:
            self.connection.execute(
                """
                UPDATE contacts
                SET first_name = ?, last_name = ?, email = ?, phone = ?,
                    company = ?, notes = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    values["first_name"],
                    values["last_name"],
                    values["email"],
                    values["phone"],
                    values["company"],
                    values["notes"],
                    self._now(),
                    contact_id,
                ),
            )
            self.connection.commit()
        except sqlite3.IntegrityError as error:
            raise ValueError("A contact with this email already exists.") from error
        return self.get(contact_id)

    def delete(self, contact_id: int) -> None:
        result = self.connection.execute(
            "DELETE FROM contacts WHERE id = ?", (contact_id,)
        )
        self.connection.commit()
        if result.rowcount == 0:
            raise KeyError(f"No contact found with id {contact_id}.")


def _print_contacts(contacts: Iterable[Contact]) -> None:
    contacts = list(contacts)
    if not contacts:
        print("No contacts found.")
        return
    print(f"{'ID':<4} {'Name':<24} {'Email':<28} {'Phone':<18} Company")
    print("-" * 90)
    for contact in contacts:
        print(
            f"{contact.id:<4} {contact.full_name:<24} {contact.email:<28} "
            f"{contact.phone:<18} {contact.company}"
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage your professional contacts.")
    parser.add_argument(
        "--database",
        default="contacts.db",
        help="SQLite database file (default: contacts.db)",
    )
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add a contact.")
    for name, required in (("first-name", True), ("last-name", True)):
        add_parser.add_argument(f"--{name}", required=required)
    for name in ("email", "phone", "company", "notes"):
        add_parser.add_argument(f"--{name}", default="")

    subparsers.add_parser("list", help="List all contacts.")
    search_parser = subparsers.add_parser("search", help="Search contacts.")
    search_parser.add_argument("query")

    update_parser = subparsers.add_parser("update", help="Update a contact.")
    update_parser.add_argument("id", type=int)
    for name in ("first-name", "last-name", "email", "phone", "company", "notes"):
        update_parser.add_argument(f"--{name}")

    delete_parser = subparsers.add_parser("delete", help="Delete a contact.")
    delete_parser.add_argument("id", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command is None:
        _interactive_menu(args.database)
        return 0

    try:
        with ContactBook(args.database) as book:
            if args.command == "add":
                contact = book.add(
                    args.first_name,
                    args.last_name,
                    args.email,
                    args.phone,
                    args.company,
                    args.notes,
                )
                print(f"Added contact #{contact.id}: {contact.full_name}")
            elif args.command == "list":
                _print_contacts(book.list_contacts())
            elif args.command == "search":
                _print_contacts(book.search(args.query))
            elif args.command == "update":
                changes = {
                    key.replace("-", "_"): value
                    for key, value in vars(args).items()
                    if key in {"first_name", "last_name", "email", "phone", "company", "notes"}
                    and value is not None
                }
                contact = book.update(args.id, **changes)
                print(f"Updated contact #{contact.id}: {contact.full_name}")
            elif args.command == "delete":
                book.delete(args.id)
                print(f"Deleted contact #{args.id}.")
    except (KeyError, ValueError) as error:
        print(f"Error: {error}")
        return 1
    return 0


def _interactive_menu(database_path: str) -> None:
    with ContactBook(database_path) as book:
        while True:
            print("\n=== Professional Contact Book ===")
            print("1. List contacts\n2. Search\n3. Add\n4. Update\n5. Delete\n6. Exit")
            choice = input("Choose an option: ").strip()
            try:
                if choice == "1":
                    _print_contacts(book.list_contacts())
                elif choice == "2":
                    _print_contacts(book.search(input("Search: ")))
                elif choice == "3":
                    contact = book.add(
                        input("First name: "),
                        input("Last name: "),
                        input("Email: "),
                        input("Phone: "),
                        input("Company: "),
                        input("Notes: "),
                    )
                    print(f"Added contact #{contact.id}.")
                elif choice == "4":
                    contact_id = int(input("Contact ID: "))
                    print("Press Enter to keep the current value.")
                    current = book.get(contact_id)
                    changes = {}
                    for field in ("first_name", "last_name", "email", "phone", "company", "notes"):
                        value = input(f"{field.replace('_', ' ').title()} [{getattr(current, field)}]: ")
                        if value:
                            changes[field] = value
                    book.update(contact_id, **changes)
                    print("Contact updated.")
                elif choice == "5":
                    book.delete(int(input("Contact ID: ")))
                    print("Contact deleted.")
                elif choice == "6":
                    print("Goodbye!")
                    return
                else:
                    print("Please choose a number from 1 to 6.")
            except (KeyError, ValueError) as error:
                print(f"Error: {error}")


if __name__ == "__main__":
    raise SystemExit(main())
