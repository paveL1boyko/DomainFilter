from data_access import SQLiteDomainsTable, SQLiteRulesTable
from domain_analysis import DomainAnalyzer


class MainApp:
    def __init__(self, db_path):
        self.domains_db = SQLiteDomainsTable(db_path)
        self.rules_db = SQLiteRulesTable(db_path)
        self.analyzer = DomainAnalyzer(self.domains_db, self.rules_db)

    def run(self):
        self.analyzer.run(clear_db=True)


if __name__ == "__main__":
    app = MainApp("domains.sqllite")
    app.run()