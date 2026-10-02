"""Collect clean Pakistan inflation observations from public source pages."""

from datetime import datetime, timezone
from pathlib import Path
import json
import re

import pandas as pd
import requests


START_YEAR = 2020
END_YEAR = 2026
OUTPUT_DIR = Path(__file__).parent
OBSERVATIONS_FILE = OUTPUT_DIR / "pakistan_inflation_2020_2026.csv"
SOURCES_FILE = OUTPUT_DIR / "pakistan_inflation_sources.csv"
PBS_PRICES_FILE = OUTPUT_DIR / "pakistan_pbs_monthly_prices_2026.csv"

WORLD_BANK_URL = (
    "https://api.worldbank.org/v2/country/PAK/indicator/FP.CPI.TOTL.ZG"
    f"?date={START_YEAR}:{END_YEAR}&format=json&per_page=100"
)
TRADING_ECONOMICS_URL = "https://tradingeconomics.com/pakistan/inflation-cpi"
PBS_MONTHLY_PRICES_URL = (
    "https://www.pbs.gov.pk/wp-content/uploads/2020/07/"
    "SPI-Monthly-Prices-Annex-9.xlsx"
)


def fetch_world_bank(retrieved_at: str) -> list[dict]:
    response = requests.get(WORLD_BANK_URL, timeout=30)
    response.raise_for_status()
    payload = response.json()
    return [
        {
            "source": "World Bank",
            "indicator": "Inflation, consumer prices",
            "frequency": "annual",
            "period": f"{row['date']}-12-31",
            "value": round(row["value"], 4),
            "unit": "percent",
            "geography": "Pakistan",
            "source_url": WORLD_BANK_URL,
            "retrieved_at": retrieved_at,
            "notes": "World Bank indicator FP.CPI.TOTL.ZG; annual percent change.",
        }
        for row in payload[1]
        if row["value"] is not None
    ]


def fetch_trading_economics_latest(retrieved_at: str) -> list[dict]:
    response = requests.get(
        TRADING_ECONOMICS_URL,
        headers={"User-Agent": "Mozilla/5.0 (educational data research)"},
        timeout=30,
    )
    response.raise_for_status()
    description = re.search(
        r"Inflation Rate in Pakistan decreased to ([0-9.]+) percent in "
        r"([A-Za-z]+) from ([0-9.]+) percent in ([A-Za-z]+) of (20[0-9]{2})",
        response.text,
    )
    if not description:
        return []

    value, month, previous_value, previous_month, year = description.groups()
    period = pd.to_datetime(f"{month} {year}").date().isoformat()
    return [
        {
            "source": "Trading Economics",
            "indicator": "Inflation rate (CPI)",
            "frequency": "monthly",
            "period": period,
            "value": float(value),
            "unit": "percent",
            "geography": "Pakistan",
            "source_url": TRADING_ECONOMICS_URL,
            "retrieved_at": retrieved_at,
            "notes": (
                f"Latest page metadata; previous month {previous_month} {year}: "
                f"{previous_value} percent. Historical API requires credentials."
            ),
        }
    ]


def fetch_pbs_monthly_prices(retrieved_at: str) -> list[dict]:
    workbook = pd.ExcelFile(PBS_MONTHLY_PRICES_URL)
    rows = []
    for sheet_name in workbook.sheet_names:
        frame = pd.read_excel(workbook, sheet_name=sheet_name, header=None)
        if frame.empty or len(frame.columns) < 5:
            continue
        title = str(frame.iloc[0, 0])
        period_match = re.search(r"month of ([A-Za-z]+) (20[0-9]{2})", title)
        if not period_match:
            continue
        month, year = period_match.groups()
        period = pd.to_datetime(f"{month} {year}").date().isoformat()
        headers = frame.iloc[1].astype(str).str.strip().tolist()
        item_column = 1
        unit_column = 2
        city_columns = [
            column
            for column in range(3, len(headers))
            if str(headers[column]) != "nan"
            and "Average" not in str(headers[column])
            and "%change" not in str(headers[column])
        ]
        for _, row in frame.iloc[2:].iterrows():
            item = row.iloc[item_column]
            if pd.isna(item):
                continue
            for column in city_columns:
                value = pd.to_numeric(row.iloc[column], errors="coerce")
                if pd.isna(value):
                    continue
                rows.append(
                    {
                        "source": "Pakistan Bureau of Statistics",
                        "indicator": "Monthly price",
                        "frequency": "monthly",
                        "period": period,
                        "value": round(float(value), 4),
                        "unit": str(row.iloc[unit_column]).strip(),
                        "geography": headers[column],
                        "source_url": PBS_MONTHLY_PRICES_URL,
                        "retrieved_at": retrieved_at,
                        "notes": str(item).strip(),
                    }
                )
    return rows


def source_catalog(retrieved_at: str) -> list[dict]:
    return [
        {
            "source": "Pakistan Bureau of Statistics",
            "source_url": "https://www.pbs.gov.pk/price-statistics",
            "coverage": "Monthly CPI, urban/rural inflation, commodity prices",
            "status": "manual_download_required",
            "notes": "The page is dynamic and its downloadable report URL changes by release.",
            "retrieved_at": retrieved_at,
        },
        {
            "source": "State Bank of Pakistan",
            "source_url": "https://easydata.sbp.org.pk/",
            "coverage": "Inflation Monitor, core inflation, monetary policy publications",
            "status": "portal_or_download_required",
            "notes": "The public portal exposes datasets; its API requires an account.",
            "retrieved_at": retrieved_at,
        },
        {
            "source": "Trading Economics",
            "source_url": TRADING_ECONOMICS_URL,
            "coverage": "Monthly CPI inflation, historical charts and forecasts",
            "status": "latest_page_observation",
            "notes": "Public HTML was used for the latest observation; historical API requires credentials.",
            "retrieved_at": retrieved_at,
        },
        {
            "source": "World Bank",
            "source_url": WORLD_BANK_URL,
            "coverage": "Annual CPI inflation",
            "status": "collected",
            "notes": "Indicator FP.CPI.TOTL.ZG; data are annual percent changes.",
            "retrieved_at": retrieved_at,
        },
        {
            "source": "MacroTrends",
            "source_url": "https://www.macrotrends.net/global-metrics/countries/PAK/pakistan/inflation-rate-cpi",
            "coverage": "Annual historical CPI inflation table",
            "status": "blocked",
            "notes": "The site did not provide machine-readable content to this low-volume request.",
            "retrieved_at": retrieved_at,
        },
    ]


def main() -> None:
    retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    observations = fetch_world_bank(retrieved_at)
    observations.extend(fetch_trading_economics_latest(retrieved_at))
    pbs_prices = fetch_pbs_monthly_prices(retrieved_at)
    observations_frame = pd.DataFrame(observations).sort_values(
        ["period", "source"]
    )
    observations_frame.to_csv(OBSERVATIONS_FILE, index=False)
    pd.DataFrame(pbs_prices).sort_values(
        ["period", "geography", "notes"]
    ).to_csv(PBS_PRICES_FILE, index=False)
    pd.DataFrame(source_catalog(retrieved_at)).to_csv(SOURCES_FILE, index=False)
    print(
        json.dumps(
            {
                "inflation_observations": len(observations),
                "pbs_price_observations": len(pbs_prices),
                "file": str(PBS_PRICES_FILE),
            }
        )
    )


if __name__ == "__main__":
    main()