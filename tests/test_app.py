"""Smoke test the complete Streamlit interface and default assessment."""

from pathlib import Path
from unittest import TestCase

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class StreamlitAppTests(TestCase):
    def test_all_demo_scenarios_render_and_assess(self) -> None:
        expectations = {
            "Balanced evidence": ("Supported for review", "Moderate", "5"),
            "Missing water evidence": ("Insufficient evidence", "High", "4"),
            "Ecologically sensitive slope": ("Conditional", "Moderate", "5"),
            "Regulatory restriction": ("Not supported", "Moderate", "5"),
        }

        for scenario, expected in expectations.items():
            with self.subTest(scenario=scenario):
                app = AppTest.from_file(str(ROOT / "app.py")).run()
                self.assertFalse(app.exception)
                if scenario != "Balanced evidence":
                    app.sidebar.selectbox[0].set_value(scenario).run()

                app.button[0].click().run()
                self.assertFalse(app.exception)

                metrics = {metric.label: metric.value for metric in app.metric}
                self.assertEqual(metrics["Decision-support status"], expected[0])
                self.assertEqual(metrics["Uncertainty"], expected[1])
                self.assertEqual(metrics["Evidence records"], expected[2])
