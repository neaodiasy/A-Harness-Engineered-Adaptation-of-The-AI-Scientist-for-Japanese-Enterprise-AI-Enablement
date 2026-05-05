"""Deterministic tests for generated local recommendation tools."""

from __future__ import annotations

import unittest

from backend.data_store import load_product_spec
from backend.tools import run_domain_tools


class RecommendationToolTests(unittest.TestCase):
    def test_area_ranking_uses_concrete_candidates(self) -> None:
        case = {
            "budget": "55-70",
            "preferences": "学校 静か 通勤 新宿 災害 耐震",
            "max_commute_minutes": 40,
        }
        result = run_domain_tools(load_product_spec(), case)
        names = [item["name_ja"] for item in result["ranked_area_candidates"]]
        self.assertIn("国立", names)
        self.assertTrue({"武蔵小杉", "国立", "和光市", "町田"} & set(names))
        self.assertGreater(result["ranked_area_candidates"][0]["score"], 0)

    def test_property_candidates_are_ranked(self) -> None:
        case = {"budget": "50-60", "preferences": "駅 通勤 ファミリー", "max_commute_minutes": 35}
        result = run_domain_tools(load_product_spec(), case)
        self.assertTrue(result["ranked_property_candidates"])
        self.assertIn("title_ja", result["ranked_property_candidates"][0])
        self.assertTrue(result["missing_information"])


if __name__ == "__main__":
    unittest.main()
