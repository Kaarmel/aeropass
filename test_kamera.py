"""Najważniejsza reguła kamery: wykryte zalanie ma pierwszeństwo przed suchą drogą."""

from ai.kamera import decyzja


assert decyzja([{"name": "flooded_road", "conf": 0.4},
                {"name": "road_non_flooded", "conf": 0.9}]) == "zalany"
assert decyzja([{"name": "flooded_road", "conf": 0.39},
                {"name": "road_non_flooded", "conf": 0.5}]) == "przejezdny"
assert decyzja([{"name": "flooded_building", "conf": 0.99}]) == "nieznany"
print("OK: progi i pierwszeństwo zalania")
