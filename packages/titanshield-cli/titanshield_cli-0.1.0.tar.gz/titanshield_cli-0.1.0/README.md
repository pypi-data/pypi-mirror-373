# TitanShield CLI 🛡️

**A fast, open-core Static Application Security Testing (SAST) scanner for Android applications, built to integrate seamlessly into your CI/CD pipeline.**

TitanShield CLI helps you find common, high-impact security issues in your Android apps before you commit. It's built for developers: fast, simple, and with clear results in the industry-standard SARIF format, ready for native integration with GitHub and GitLab.

[![PyPI version](https://badge.fury.io/py/titanshield-cli.svg)](https://badge.fury.io/py/titanshield-cli)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

---

## ✨ Key Features

-   **Fast APK Analysis:** Decompiles and scans your APK in minutes.
-   **High-Signal Rules:** Focuses on high-impact vulnerabilities with a low false-positive rate (hardcoded secrets, insecure configurations, weak cryptography, etc.).
-   **CI/CD Native Output:** Generates reports in SARIF format for native integration into the "Security" tab of your Pull Requests.
-   **Resource Control:** Allows you to limit the memory consumption of the JADX decompiler to fit any environment, from a local machine to a CI runner.
-   **Open-Core Engine:** A transparent, community-driven rule engine based on simple YAML files.

## 🚀 Installation

```bash
pip install titanshield-cli
```

(Prerequisites: A recent version of Java and the JADX decompiler must be installed and available in your system's PATH.)

## 🛠️ Usage
- Using the CLI is straightforward. Just point it at your APK file.
- For a quick overview in your console:
```bash
titanshield /path/to/your/app.apk 
```

- To generate a SARIF report for your CI/CD pipeline:
```bash
titanshield /path/to/your/app.apk --output sarif --file results.sarif
```

- To control memory usage on resource-constrained machines:

```bash
# Limit the JADX decompiler to 2GB of RAM
titanshield /path/to/your/app.apk --max-mem 2g
```

## 📈 Example: GitHub Actions Integration
Integrate TitanShield into your workflow in minutes and see security findings directly in your Pull Requests.

```Yaml
# .github/workflows/security-scan.yml
name: TitanShield SAST Scan

on: [push, pull_request]

jobs:
  sast_scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      # Add your APK build step here (example)
      - name: Build APK
        run: ./gradlew assembleRelease

      - name: Run TitanShield Scan
        run: |
          pip install titanshield-cli
          titanshield app/build/outputs/apk/release/app-release.apk --output sarif --file results.sarif

      - name: Upload SARIF Results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
```

## 💎 Go Deeper with the TitanShield Cloud Platform
The TitanShield CLI is designed to be your first line of defense. Our TitanShield Cloud Platform provides a much deeper analysis, including:
Advanced SAST: Full data-flow (taint) analysis to find complex injection and data leak vulnerabilities.
Centralized Dashboard: Track your security posture across all your projects over time.
DAST and Architecture Analysis: (Coming Soon)
Compliance Reporting: Generate reports for standards like MASVS and GDPR.

➡️ Join the private beta waitlist at [Titanshield](https://titanshield.tech).
## 🤝 Contributing
This is an open-core project. We welcome community contributions, especially to the rule packs! If you have an idea for a new rule, please open an issue or a pull request.