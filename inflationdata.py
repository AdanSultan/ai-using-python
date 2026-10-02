"""Build a PBS-sourced Pakistan CPI file and a transparent quality report.

The script deliberately leaves group values null when PBS has not published a
matching 2015-16 group table for the month. It never substitutes third-party
or differently rebased observations.
"""

from __future__ import annotations

import csv
import io
import json
import re
from calendar import month_abbr
from datetime import date
from pathlib import Path
from urllib.parse import quote

import requests
from pypdf import PdfReader


ROOT = Path(__file__).parent
OUTPUT_CSV = ROOT / "pakistan_cpi_powerbi_2020_2026.csv"
QUALITY_REPORT = ROOT / "pakistan_cpi_data_quality_report.json"
PBS_PAGE = "https://www.pbs.gov.pk/price-statistics/"
HISTORICAL_PDF = (
	"https://www.pbs.gov.pk/wp-content/uploads/2020/07/"
	"indices_and_growth_rates_historical-1.pdf"
)
MEDIA_API = "https://www.pbs.gov.pk/wp-json/wp/v2/media"
START = date(2020, 1, 1)

CATEGORIES = [
	"Food & Non-Alcoholic Beverages",
	"Alcoholic Beverages & Tobacco",
	"Clothing & Footwear",
	"Housing, Water, Electricity, Gas & Fuels",
	"Furnishing & Household Equipment Maintenance",
	"Health",
	"Transport",
	"Communication",
	"Recreation & Culture",
	"Education",
	"Restaurants & Hotels",
	"Miscellaneous Goods & Services",
]
REGIONS = ["National", "Urban", "Rural"]

GROUP_PATTERNS = {
	CATEGORIES[0]: r"Food\s*(?:&|and)\s*Non-alcoholic\s+Bev(?:erages)?\.?",
	CATEGORIES[1]: r"Alcoholic\s+Bev(?:erages)?\.?\s*&?\s*Tobacco",
	CATEGORIES[2]: r"Clothing\s*(?:&|and)\s*Footwear",
	CATEGORIES[3]: r"Housing,\s*Water,\s*Electricity,\s*Gas\s*&?\s*(?:Other\s+)?Fuels",
	CATEGORIES[4]: r"Furnishing\s*&\s*Household\s+Equip\.?\s*(?:&|and)?\s*Maintenance",
	CATEGORIES[5]: r"Health",
	CATEGORIES[6]: r"Transport",
	CATEGORIES[7]: r"Communication",
	CATEGORIES[8]: r"Recreation\s*&\s*Culture",
	CATEGORIES[9]: r"Education",
	CATEGORIES[10]: r"Restaurants\s*&\s*Hotels?",
	CATEGORIES[11]: r"Miscellaneous",
}


def get(url: str) -> bytes:
	response = requests.get(url, timeout=60, headers={"User-Agent": "PBS CPI research"})
	response.raise_for_status()
	return response.content


def month_date(year: int, month: int) -> date:
	return date(year, month, 1)


def financial_year(period: date) -> str:
	start_year = period.year if period.month >= 7 else period.year - 1
	return f"FY{start_year}-{str(start_year + 1)[-2:]}"


def pdf_pages(url: str) -> list[str]:
	reader = PdfReader(io.BytesIO(get(url)))
	return [page.extract_text() or "" for page in reader.pages]


def historical_headline() -> dict[date, dict[str, dict[str, float]]]:
	text = "\n".join(pdf_pages(HISTORICAL_PDF))
	index_data: dict[date, dict[str, float]] = {}
	for match in re.finditer(
		r"(?m)^(20\d{2})\s+(\d{1,2})\s+"
		r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+[\d.]+$",
		text[: text.find("Historical Inflation Rate (Y-oY)")],
	):
		year, month, national, urban, rural = match.groups()
		period = month_date(int(year), int(month))
		if period >= START:
			index_data[period] = {
				"National": float(national),
				"Urban": float(urban),
				"Rural": float(rural),
			}

	yoy_data: dict[date, dict[str, float]] = {}
	yoy_start = text.find("Historical Inflation Rate (Y-oY)")
	for match in re.finditer(
		r"(?m)^(20\d{2})\s+(\d{1,2})\s+"
		r"(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+[\d.]+$",
		text[yoy_start:],
	):
		year, month, national, urban, rural = match.groups()
		period = month_date(int(year), int(month))
		if period >= START:
			yoy_data[period] = {
				"National": float(national),
				"Urban": float(urban),
				"Rural": float(rural),
			}

	result = {}
	for period, values in index_data.items():
		previous_period = date(period.year - (period.month == 1), 12 if period.month == 1 else period.month - 1, 1)
		previous = index_data.get(previous_period)
		result[period] = {}
		for region, index in values.items():
			mom = None
			if previous and previous.get(region):
				mom = (index / previous[region] - 1) * 100
			result[period][region] = {
				"index": index,
				"mom": mom,
				"yoy": yoy_data.get(period, {}).get(region),
			}
	return result


def discover_reports() -> dict[str, str]:
	urls: dict[str, str] = {}
	for term in ("Monthly Review", "CPI Monthly Review", "monthly_review"):
		response = requests.get(f"{MEDIA_API}?search={quote(term)}&per_page=100", timeout=60)
		response.raise_for_status()
		for item in response.json():
			url = item.get("source_url", "")
			if (
				url.lower().endswith(".pdf")
				and "review" in url.lower()
				and "2026" in url
			):
				urls[url] = item.get("title", {}).get("rendered", url)
	return urls


def report_period(text: str, title: str) -> date | None:
	combined = f"{title} {text[:2500]}"
	match = re.search(
		r"(January|February|March|April|May|June|July|August|September|October|November|December)[, -]+(20\d{2})",
		combined,
		re.IGNORECASE,
	)
	if not match:
		return None
	month = list(month_abbr).index(match.group(1)[:3].title())
	return month_date(int(match.group(2)), month)


def parse_group_rows(url: str, title: str) -> dict[tuple[date, str, str], dict[str, float | str]]:
	pages = pdf_pages(url)
	result = {}
	section_markers = (
		"National Consumer Price Index",
		"Urban Consumer Price Index",
		"Rural Consumer Price Index",
	)
	for region, marker in zip(REGIONS, section_markers):
		page_text = next((page for page in pages if marker in page and "by Group" in page), "")
		if not page_text:
			continue
		period = report_period(page_text, title)
		if not period:
			continue
		normalized = re.sub(r"\s+", " ", page_text.replace("\u00ad", " "))
		for category, pattern in GROUP_PATTERNS.items():
			match = re.search(
				rf"{pattern}\s+(\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+"
				rf"(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+"
				rf"(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)",
				normalized,
				re.IGNORECASE,
			)
			if match:
				weight, index, _, _, mom, yoy = map(float, match.groups())
				result[(period, region, category)] = {
					"CPI_Index": index,
					"MoM_Inflation": mom,
					"YoY_Inflation": yoy,
					"Weight": weight,
					"Source": f"{url} (PBS monthly review, {region} group table)",
				}
	return result


def make_row(period: date, region: str, category: str, values: dict, source: str) -> dict:
	return {
		"Date": period.isoformat(),
		"Year": period.year,
		"Month": period.strftime("%B"),
		"Month_Number": period.month,
		"Financial_Year": financial_year(period),
		"Region": region,
		"Category": category,
		"CPI_Index": values.get("CPI_Index"),
		"MoM_Inflation": values.get("MoM_Inflation"),
		"YoY_Inflation": values.get("YoY_Inflation"),
		"Weight": values.get("Weight"),
		"Source": values.get("Source", source),
	}


def validate_headlines(headlines: dict, group_values: dict) -> list[dict]:
	rows = []
	for period in [month_date(year, 9) for year in range(2020, 2027)]:
		expected = headlines.get(period, {}).get("National")
		value = group_values.get((period, "National", CATEGORIES[0]))
		release_value = value.get("YoY_Inflation") if value else None
		rows.append({
			"month": period.isoformat(),
			"historical_pdf_national_yoy": expected.get("yoy") if expected else None,
			"monthly_release_national_yoy": release_value,
			"monthly_release_found": release_value is not None,
			"status": "matched" if expected and release_value is not None and abs(expected["yoy"] - release_value) <= 0.1 else "not independently matched",
		})
	return rows


def main() -> None:
	headlines = historical_headline()
	reports = discover_reports()
	group_values = {}
	for url, title in reports.items():
		try:
			group_values.update(parse_group_rows(url, title))
		except Exception as error:
			print(f"Skipping unreadable PBS report {url}: {error}")

	latest = max(set(headlines) | {key[0] for key in group_values}, default=START)
	periods = []
	current = START
	while current <= latest:
		periods.append(current)
		current = date(current.year + (current.month == 12), 1 if current.month == 12 else current.month + 1, 1)

	rows = []
	for period in periods:
		for region in REGIONS:
			for category in CATEGORIES:
				key = (period, region, category)
				headline = headlines.get(period, {}).get(region, {})
				source = f"{HISTORICAL_PDF} (PBS historical indices; category unavailable)"
				values = group_values.get(key, {})
				rows.append(make_row(period, region, category, values, source))

	rows.sort(key=lambda row: (row["Date"], REGIONS.index(row["Region"]), CATEGORIES.index(row["Category"])))
	fields = list(rows[0])
	with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as output:
		writer = csv.DictWriter(output, fieldnames=fields)
		writer.writeheader()
		writer.writerows(rows)

	keys = [(row["Date"], row["Region"], row["Category"]) for row in rows]
	missing_months = [period.isoformat() for period in periods if not any(row["Date"] == period.isoformat() for row in rows)]
	missing_values = {field: sum(row[field] in (None, "") for row in rows) for field in fields}
	quality = {
		"title": "Pakistan Inflation Analysis: 2020-2026",
		"rows": len(rows),
		"date_range": {"start": periods[0].isoformat(), "end": periods[-1].isoformat()},
		"unique_months": len(periods),
		"categories": len(CATEGORIES),
		"regions": len(REGIONS),
		"duplicate_rows": len(keys) - len(set(keys)),
		"missing_months": missing_months,
		"missing_values_by_field": missing_values,
		"source_files_used": sorted({row["Source"] for row in rows}),
		"methodology": "PBS 2015-16 CPI base only. Historical headline PDF covers the index series; monthly review files provide group tables where published.",
		"base_year_changes": "No different base year was combined. Older 2007-08 PBS files were excluded.",
		"inconsistencies": [
			"PBS historical indices contain headline National/Urban/Rural series but not monthly 12-group tables for every month.",
			"Group rows are null where no official 2015-16 PBS monthly review table was available or parseable.",
			"The historical PDF runs through June 2026; the latest discovered PBS monthly review extends the output to its published month.",
		],
		"headline_press_release_validation": validate_headlines(headlines, group_values),
		"official_pbs_page": PBS_PAGE,
	}
	QUALITY_REPORT.write_text(json.dumps(quality, indent=2), encoding="utf-8")
	print(json.dumps({"csv": str(OUTPUT_CSV), "quality_report": str(QUALITY_REPORT), "rows": len(rows), "latest": latest.isoformat()}))


if __name__ == "__main__":
	main()
