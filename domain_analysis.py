from collections import Counter

import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer

from config import DISTANCE_THRESHOLD
from data_access import DomainsTableInterface, RulesTableInterface


class DomainProcessor:
    """Class to process and cluster domains."""

    def __init__(self, threshold: int = DISTANCE_THRESHOLD):
        self.threshold = threshold

    def filter_domains_by_level(self, domains_list: list[str]) -> list[str]:
        return [domain for domain in domains_list if len(domain.split(".")) >= 3]

    def cluster_domains(self, project_domains: list[str]) -> list[int]:
        vectorizer = TfidfVectorizer(tokenizer=lambda x: x.split("."), token_pattern=None)
        X = vectorizer.fit_transform(project_domains)
        cluster_model = AgglomerativeClustering(n_clusters=None, distance_threshold=self.threshold)
        return cluster_model.fit_predict(X.toarray())

    def identify_garbage_domains(self, project_domains_df: pd.DataFrame) -> list[str]:
        filtered_domains = self.filter_domains_by_level(project_domains_df["name"].tolist())
        labels = self.cluster_domains(filtered_domains)
        most_common_label = Counter(labels).most_common(1)[0][0]
        return [domain for i, domain in enumerate(filtered_domains) if labels[i] == most_common_label]


class RuleManager:
    """Class to manage and generate regex patterns based on garbage domains."""

    def __init__(self, rules_table: RulesTableInterface):
        self.rules_table = rules_table

    def generate_regex(self, domain: str) -> str:
        return ".*" + ".".join(domain.split(".")[-3:])

    def update_rules_table(self, patterns: dict[str, list[str]], clear_db: bool = False) -> None:
        if clear_db:
            self.rules_table.delete_rules()
        for project, domains in patterns.items():
            for domain in domains:
                regex = self.generate_regex(domain)
                self.rules_table.insert_rule(regex, project)


class DomainAnalyzer:
    """Class to analyze domains and update rules based on analysis."""

    def __init__(self, domains_table: DomainsTableInterface, rules_table: RulesTableInterface):
        self.domains_table = domains_table
        self.rules_table = rules_table
        self.processor = DomainProcessor()
        self.manager = RuleManager(rules_table)
        self.domains_df = pd.DataFrame(self.domains_table.get_all_domains(), columns=["name", "project_id"])

    def process_all_projects(self) -> dict[str, list[str]]:
        unique_projects = self.domains_df["project_id"].unique()
        garbage_domains = {}
        for project in unique_projects:
            project_domains_df = self.domains_df[self.domains_df["project_id"] == project]
            garbage_domains_list = self.processor.identify_garbage_domains(project_domains_df)
            garbage_domains[project] = garbage_domains_list
        return garbage_domains

    def run(self, clear_db: bool = False) -> None:
        garbage_domains = self.process_all_projects()
        print(garbage_domains)
        self.manager.update_rules_table(garbage_domains, clear_db)
