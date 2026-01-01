"""Download and plot Rio Negro water level data from Porto de Manaus."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

import matplotlib.pyplot as plt
import pandas as pd
import requests

BASE_URL = "https://portodemanaus.com.br/nivel-do-rio"

MONTHS = [
    (1, "janeiro"),
    (2, "fevereiro"),
    (3, "marco"),
    (4, "abril"),
    (5, "maio"),
    (6, "junho"),
    (7, "julho"),
    (8, "agosto"),
    (9, "setembro"),
    (10, "outubro"),
    (11, "novembro"),
    (12, "dezembro"),
]


class RioNegroDownloadError(RuntimeError):
    """Raised when no data tables can be extracted."""


def _parse_level(value: object) -> float:
    raw = re.sub(r"[^0-9,.-]", "", str(value)).strip()
    if raw.count(",") == 1 and raw.count(".") == 0:
        raw = raw.replace(",", ".")
    return float(raw)


def _find_level_table(tables: Iterable[pd.DataFrame]) -> Optional[pd.DataFrame]:
    for table in tables:
        columns = [str(col).strip().lower() for col in table.columns]
        has_day = any(col.startswith("dia") for col in columns)
        has_level = any("cota" in col for col in columns)
        if has_day and has_level:
            return table
    return None


def fetch_month(year: int, month_num: int, month_slug: str) -> Optional[pd.DataFrame]:
    """Fetch a single month table from Porto de Manaus."""
    url = f"{BASE_URL}/{month_slug}-{year}/"
    print(f"Fetching {year}-{month_num:02d} from {url}")
    response = requests.get(url, timeout=25)
    if response.status_code != 200 or not response.text:
        print(f"No data found for {year}-{month_num:02d} (status={response.status_code}).")
        return None

    try:
        tables = pd.read_html(response.text)
    except ValueError:
        print(f"No tables parsed for {year}-{month_num:02d}.")
        return None

    table = _find_level_table(tables)
    if table is None:
        print(f"No matching level table found for {year}-{month_num:02d}.")
        return None

    column_map = {}
    for col in table.columns:
        column = str(col).strip().lower()
        if column.startswith("dia"):
            column_map[col] = "day"
        elif "cota" in column:
            column_map[col] = "level"

    table = table.rename(columns=column_map)
    if "day" not in table.columns or "level" not in table.columns:
        return None

    data = table[["day", "level"]].copy()
    data["day"] = pd.to_numeric(data["day"], errors="coerce").astype("Int64")
    data["level_m"] = data["level"].apply(
        lambda value: _parse_level(value) if pd.notna(value) else None
    )
    data = data.dropna(subset=["day", "level_m"])
    data["date"] = data["day"].apply(lambda day: pd.Timestamp(date(year, month_num, int(day))))
    data = data[["date", "level_m"]].sort_values("date")
    print(f"Parsed {len(data)} rows for {year}-{month_num:02d}.")
    return data


def download_series(year_start: int, year_end: int) -> pd.DataFrame:
    """Download a daily series of water levels."""
    chunks = []
    print(f"Downloading Rio Negro levels from {year_start} to {year_end}.")
    for year in range(year_start, year_end + 1):
        print(f"Starting year {year}.")
        for month_num, month_slug in MONTHS:
            month_data = fetch_month(year, month_num, month_slug)
            if month_data is not None and not month_data.empty:
                chunks.append(month_data)

    if not chunks:
        raise RioNegroDownloadError(
            "No tables could be extracted. The site layout might have changed."
        )

    data = pd.concat(chunks, ignore_index=True)
    data = data.drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)
    print(f"Download complete: {len(data)} total rows.")
    return data


def save_csv(data: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)
    print(f"CSV saved to {path}.")


def plot_series(data: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Generating plots in {output_path.parent}.")

    plot_data = data.copy()
    plot_data["year"] = plot_data["date"].dt.year

    plt.figure(figsize=(12, 4))
    plt.plot(plot_data["date"], plot_data["level_m"], linewidth=1)
    plt.title("Rio Negro (Porto de Manaus) — Nível diário")
    plt.xlabel("Data")
    plt.ylabel("Cota (m)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    yearly = plot_data.groupby("year")["level_m"].agg(["min", "max"]).reset_index()
    plt.figure(figsize=(10, 4))
    plt.plot(yearly["year"], yearly["min"], label="Mínima anual")
    plt.plot(yearly["year"], yearly["max"], label="Máxima anual")
    plt.title("Rio Negro — Mínimas e máximas anuais")
    plt.xlabel("Ano")
    plt.ylabel("Cota (m)")
    plt.legend()
    plt.tight_layout()
    yearly_path = output_path.with_name(f"{output_path.stem}_min_max{output_path.suffix}")
    plt.savefig(yearly_path, dpi=150)
    plt.close()
    print(f"Plots saved to {output_path} and {yearly_path}.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download and plot Rio Negro water levels from Porto de Manaus."
    )
    parser.add_argument("--start", type=int, default=2000, help="Start year")
    parser.add_argument("--end", type=int, default=date.today().year, help="End year")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/rio_negro"),
        help="Directory to write CSV and plots",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    data = download_series(args.start, args.end)
    csv_path = args.output_dir / f"rio_negro_levels_{args.start}_{args.end}.csv"
    plot_path = args.output_dir / f"rio_negro_levels_{args.start}_{args.end}.png"

    save_csv(data, csv_path)
    plot_series(data, plot_path)

    print(f"Saved CSV to {csv_path}")
    print(f"Saved plots to {plot_path} and {plot_path.with_name(plot_path.stem + '_min_max.png')}")


if __name__ == "__main__":
    main()
