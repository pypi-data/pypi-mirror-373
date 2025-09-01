# pytest-plugins
An advanced pytest plugin designed for Python projects, offering robust features and utilities to enhance the testing workflow. <br>
It includes improved `conftest.py` fixtures, automated test result reporting, detailed logging, and seamless integration with external tools for a streamlined and efficient testing experience.

---

## 🚀 Features
- ✅ **better-report**: Enhanced test result tracking and structured JSON reporting. 
generate `execution_results.json`, `test_results.json`, and `test_report`.md under `tests/results_output/` directory.
  - flags:
    - `--better-report`: Enable the better report feature.
    - `--output-dir`: Specify the output directory for the report files (default is `root_project/results_output/`).
    - `--traceback`: Include detailed traceback information in the report.
    - `--md-report`: Generate a Markdown report of the test results.
    - `repo-name`: Specify the git repository name for the report.
    - `--pr-number`: Include a pull request number in the report for better traceability.
    - `--mr-number`: Include a merge request number in the report for better traceability.
    - `--pipeline-number`: Include a CI pipeline number in the report for better traceability.
    - `--commit`: Include the commit hash in the report for better traceability.
    - `--add-parameters`: Add the test parameters as fields to the test results.
    - `--pytest-command`: Add the detailed information about the pytest command-line to the "execution_results.json" file
<br> <br>
- ✅ **maxfail-streak**: Stop test execution after a configurable number of consecutive failures.
    - flags:
      - `--maxfail-streak=N`: Stop test execution after `N` consecutive failures.
<br> <br>
- ✅ **fail2skip**: Change failing tests to skipped, allowing for better test management and reporting.
- flags:
  - `--fail2skip`: Enable the fail2skip feature.
    - `@pytest.mark.fail2skip`: Decorator to mark tests that should be skipped on failure.
<br> <br>
- ✅ **verbose-param-ids**: Enhance test IDs with parameter names for better clarity in pytest reports.
- flags:
    - `--verbose-param-ids`: Include parameter names in pytest test IDs (e.g., `(param1: value1, param2: value2)` instead of `(param1-param2))`

---

## 📦 Installation
```bash
pip install pytest-plugins
```

---

### 🔧 Usage
##### Add the following to your `pytest.ini` file to enable the plugin features:
```ini
[pytest]
addopts =
    --better-report
    --output-dir=logs
    --pr-number=123
;    --mr-number=123
    --fail2skip
    --maxfail-streak=3
    --add-parameters
    --pytest-command
    --verbose-param-ids
    --md-report
    --traceback
```

---

## 🤝 Contributing
If you have a helpful tool, pattern, or improvement to suggest:
Fork the repo <br>
Create a new branch <br>
Submit a pull request <br>
I welcome additions that promote clean, productive, and maintainable development. <br>

---

## 🙏 Thanks
Thanks for exploring this repository! <br>
Happy coding! <br>
