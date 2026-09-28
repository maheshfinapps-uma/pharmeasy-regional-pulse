"""Part 3 — Draft CII report generator."""
from pathlib import Path

FLAGGED = {
    "Bengaluru": (-15.02, -1.52),
    "Guntur": (122.19, -28.11),
    "Hyderabad": (16.29, 20.61),
    "Karimnagar": (23.63, -44.00),
    "Tirupati": (66.87, -17.07),
    "Vijayawada": (2.06, -12.02),
    "Visakhapatnam": (-62.46, 99.12),
    "Warangal": (-22.03, -14.84),
}

def draft_report_v1():
    blocks = []
    for region, (apr_may, may_jun) in FLAGGED.items():
        blocks.append(
            f"### {region}\n"
            f"- **Context:** {region} was flagged under the 8% operational movement rule. [MEDIUM]\n"
            f"- **Insight:** April-to-May movement was {apr_may:+.2f}%; May-to-June movement was {may_jun:+.2f}%. [HIGH]\n"
            f"- **Implication:** Review order- and category-level detail before attributing a business cause. [MEDIUM]\n"
        )
    return "# Draft CII Report\n\n" + "\n".join(blocks)

if __name__ == "__main__":
    text = draft_report_v1()
    Path(__file__).resolve().parent.joinpath("draft_report_v1.md").write_text(text, encoding="utf-8")
    print(text)
