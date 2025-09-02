import yaml
import re
import os
from typing import List, Dict, Any

def load_rules_from_dir(rules_directory: str) -> List[Dict[str, Any]]:
    """Charge les règles depuis un dossier de fichiers YAML."""
    all_rules = []
    for filename in os.listdir(rules_directory):
        if filename.endswith(('.yml', '.yaml')):
            with open(os.path.join(rules_directory, filename), 'r') as f:
                rules_in_file = yaml.safe_load(f)
                if isinstance(rules_in_file, list):
                    all_rules.extend(rules_in_file)
    return all_rules

def run_rules_on_file(file_path: str, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Exécute les règles sur un seul fichier."""
    findings = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        for rule in rules:
            if re.search(rule['pattern'], content, re.MULTILINE):
                finding = {
                    "rule_id": rule['id'],
                    "file_path": file_path,
                    "name": rule['name'],
                    "severity": rule['severity'],
                    "details": rule['details'],
                }
                findings.append(finding)
    except Exception as e:
        print(f"Could not analyze file {file_path}: {e}")
    return findings