import sqlite3
from abc import ABC, abstractmethod


class DomainsTableInterface(ABC):
    @abstractmethod
    def get_all_domains(self) -> list[tuple[str, str]]:
        """Fetch all domain names and associated project ids."""
        pass


class RulesTableInterface(ABC):
    @abstractmethod
    def insert_rule(self, regexp: str, project_id: str) -> None:
        """Insert a rule into the table."""
        pass

    @abstractmethod
    def delete_rules(self, condition: str | None = None) -> None:
        """Delete rules based on a condition."""
        pass


class SQLiteBase:
    """Base class for SQLite operations."""

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()


class SQLiteDomainsTable(SQLiteBase, DomainsTableInterface):
    def get_all_domains(self) -> list[tuple[str, str]]:
        query = "SELECT name, project_id FROM domains;"
        return self.cursor.execute(query).fetchall()


class SQLiteRulesTable(SQLiteBase, RulesTableInterface):
    def insert_rule(self, regexp: str, project_id: str) -> None:
        query = "INSERT INTO rules (regexp, project_id) VALUES (?, ?);"
        self.cursor.execute(query, (regexp, project_id))
        self.conn.commit()

    def delete_rules(self, condition: str | None = None) -> None:
        if condition:
            query = f"DELETE FROM rules WHERE {condition};"
        else:
            query = "DELETE FROM rules;"
        self.cursor.execute(query)
        self.conn.commit()
