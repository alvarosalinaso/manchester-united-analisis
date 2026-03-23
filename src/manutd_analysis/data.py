import pandas as pd
from pathlib import Path
from typing import Optional

MANAGERS = {
    2014: "David Moyes",
    2015: "Louis van Gaal",
    2016: "Louis van Gaal",
    2017: "José Mourinho",
    2018: "José Mourinho",
    2019: "Mourinho / Solskjær",
    2020: "Ole Gunnar Solskjær",
    2021: "Ole Gunnar Solskjær",
    2022: "Solskjær / Rangnick",
    2023: "Erik ten Hag",
    2024: "Erik ten Hag",
}

REQ_COLS = {"team", "season_end_year", "points", "position", "gf", "ga", "played"}

def _find_file(path_str: str) -> Path:
    cands = [Path(path_str), Path.cwd() / path_str, Path(__file__).parent.parent.parent / path_str]
    for c in cands:
        if c.exists(): return c.resolve()
    raise FileNotFoundError(f"Missing '{path_str}'. Drop it in the root folder.")

def load_raw_data(f_path: str = "pl-tables-1993-2024.csv") -> Optional[pd.DataFrame]:
    try:
        real_path = _find_file(f_path)
        raw_df = pd.read_csv(real_path)

        if REQ_COLS - set(raw_df.columns):
            raise ValueError(f"CSV is missing columns: {REQ_COLS - set(raw_df.columns)}")

        # get utd
        m_utd = (raw_df["team"] == "Manchester Utd") & (raw_df["season_end_year"] >= 2014)
        utd = raw_df.loc[m_utd, ["season_end_year", "points", "position", "gf", "ga", "played"]].copy()
        utd = utd.rename(columns={"season_end_year": "año", "points": "pts_utd", "position": "pos_utd", "gf": "gf_utd", "ga": "ga_utd"})
        utd["entrenador"] = utd["año"].map(MANAGERS)

        # get champs
        champs = raw_df.loc[raw_df["position"] == 1, ["season_end_year", "points", "gf", "ga"]].rename(
            columns={"season_end_year": "año", "points": "pts_champ", "gf": "gf_champ", "ga": "ga_champ"}
        )

        merged = pd.merge(utd, champs, on="año", how="inner")
        merged["brecha_puntos"]  = merged["pts_champ"] - merged["pts_utd"]
        merged["brecha_ataque"]  = merged["gf_champ"] - merged["gf_utd"]
        merged["brecha_defensa"] = merged["ga_utd"] - merged["ga_champ"]
        merged["pts_por_gol"]    = (merged["pts_utd"] / merged["gf_utd"]).round(2)
        merged["ppg"]            = (merged["pts_utd"] / merged["played"]).round(3)

        return merged.reset_index(drop=True)

    except FileNotFoundError as e:
        print(f"File crash: {e}")
    except Exception as e:
        print(f"Data load error: {e}")
    return None
