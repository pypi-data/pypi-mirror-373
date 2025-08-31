def generate_md_report(report: dict) -> str:
    status_icons = {
        "passed": "✅",
        "failed": "❌",
        "failed-skipped": "⚠️",
        "skipped": "⏭️",
        "collected": "📋"
    }
    rows = [
        "| No. | Test Name | Status | Duration | Message |",
        "|:---:|-----------|:------:|:--------:|---------|"
    ]
    stats = {"passed": 0, "failed": 0, "failed-skipped": 0, "skipped": 0, "collected": 0}
    for index, test in enumerate(report.values(), start=1):
        status = test["test_status"]
        stats[status] += 1
        name = test["test_full_name"]
        icon = status_icons.get(status, status)
        duration = f"{test['test_duration_sec']:.2f}s"
        msg = (
            test["exception_message"]["message"]
            if test["exception_message"]
            else "-"
        )
        rows.append(f"|{index}| `{name}` | {icon} {status} | {duration} | `{msg}` |")

    total_summary = f"\n🧪 Total: {len(report)} &nbsp;&nbsp;| &nbsp;&nbsp;" + " &nbsp;&nbsp;| &nbsp;&nbsp;".join(
        f"{icon} {k.capitalize()}: {v}" for k, v in stats.items()
        for icon in [status_icons.get(k, "")]
    )

    return "## ✅ Test Report Summary\n\n" + "\n".join(rows) + f'\n<br> \n\n### Summary: <br> \n{total_summary}'
