import json
from typing import List, Dict, Any

def generate_sarif_report(findings: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Génère un rapport au format SARIF v2.1.0.
    """
    results = []
    for finding in findings:
        results.append({
            "ruleId": finding['rule_id'],
            "message": {
                "text": finding['details']['description']
            },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": finding['file_path']
                    },
                    "region": {
                        "startLine": 1 # Pour un vrai outil, il faudrait trouver le numéro de ligne
                    }
                }
            }]
        })

    tool_rules = []
    for rule in rules:
        tool_rules.append({
            "id": rule['id'],
            "name": rule['name'],
            "shortDescription": {
                "text": rule['details']['description']
            },
            "fullDescription": {
                "text": rule['details']['recommendation']
            },
            "help": {
                "text": f"CWE: {rule['details'].get('cwe')}\nMASVS: {rule['details'].get('masvs')}"
            },
            "properties": {
                "tags": ["security", "android", rule.get('masvs', '').lower()],
                "precision": "high",
                "problem.severity": rule.get('severity', 'UNKNOWN').lower()
            }
        })

    report = {
        "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "TitanShield CLI",
                    "version": "0.1.0",
                    "informationUri": "https://titanshield.tech", 
                    "rules": tool_rules
                }
            },
            "results": results
        }]
    }
    return report