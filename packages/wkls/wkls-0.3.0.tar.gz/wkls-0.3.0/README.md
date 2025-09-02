# 🌐 `wkls`: Well-Known Locations

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

`wkls` makes it easy to explore global administrative boundaries — from countries to cities — using clean, chainable Python syntax. It reads directly from [Overture Maps Foundation](https://overturemaps.org/) GeoParquet data (version 2025-05-21.0) hosted on the AWS Open Data Registry.

You can instantly get geometries in formats like WKT, WKB, HexWKB, GeoJSON, and SVG:

```python
import wkls
print(wkls.us.ca.sanfrancisco.wkt()) # => "MULTIPOLYGON (((-122.9915659 37.7672733...)))"
print(wkls.overture_version())       # => "2025-05-21.0"
```

## Installation

```bash
pip install wkls
```

> Requires DuckDB with the spatial extension (loaded automatically). The package is self-contained and lightweight.

## Quick Start

```python
import wkls

# Get country geometry
usa_wkt = wkls.us.wkt()
print(f"USA geometry: {usa_wkt[:50]}...")

# Get state/region geometry  
california_geojson = wkls.us.ca.geojson()

# Get city geometry
sf_svg = wkls.us.ca.sanfrancisco.svg()

# Check dataset version
print(f"Using Overture Maps data: {wkls.overture_version()}")

# Explore available data
print(f"Countries: {len(wkls.countries())}")
print(f"US regions: {len(wkls.us.regions())}")
print(f"CA counties: {len(wkls.us.ca.counties())}")
```

## Usage

### Accessing geometry

WKLS supports **up to 3 chained attributes**:
1. **Country** (required) – must be a 2-letter ISO 3166-1 alpha-2 code (e.g. `us`, `de`, `fr`)
2. **Region** (optional) – must be a valid region ISO code suffix (e.g. `ca` for `US-CA`, `ny` for `US-NY`)
3. **Place** (optional) – a **name** match against subtypes: `county`, `locality`, or `neighborhood`

Examples:
```python
wkls.us.wkt()                          # country: United States
wkls.us.ca.wkt()                       # region: California
wkls.us.ca.sanfrancisco.wkt()          # city/county: San Francisco
wkls["us"]["ca"]["sanfrancisco"].wkt() # dictionary-style access
```

Supported formats:
- `.wkt()` – Well-Known Text
- `.wkb()` – Raw binary WKB
- `.hexwkb()` – Hex-encoded WKB
- `.geojson()` – GeoJSON string
- `.svg()` – SVG path string

### What does `wkls.us.ca.sanfrancisco` return?

Chained expressions like wkls.us.ca.sanfrancisco return a Wkl object. Internally, this holds a Pandas DataFrame containing one or more rows that match the given chain.

```python
        id           country    region   subtype       name           division_id
0  085718963fffff...   US       US-CA    county    San Francisco  085718963fffff...
```

In most cases, it resolves to a single administrative boundary. But if there are name collisions (e.g., both a county and a locality called “San Francisco”), multiple rows may be returned.

By default, geometry methods like `.wkt()` will use the first matching row.

### Helper methods

The following methods return Pandas DataFrames for easy exploration:

| Method                     | Description                        |
|----------------------------|------------------------------------|
| `wkls.countries()`         | List all countries                 |
| `wkls.us.regions()`        | List regions in the US             |
| `wkls.us.ca.counties()`    | List counties in California        |
| `wkls.us.ca.cities()`      | List cities in California          |
| `wkls.subtypes()`          | Show all distinct division subtypes |

### Dataset information

You can check which version of the Overture Maps dataset is being used:

```python
print(wkls.overture_version())  # => "2025-05-21.0"
```

> **Note**: The `overture_version()` method is only available at the root level, not on chained objects like `wkls.us.overture_version()`.

## How It Works

WKLS works in two stages:

### 1. In-memory GERS ID resolution

Your chained attributes — up to 3 levels — are parsed in this order:

1. `country` → matched by ISO 2-letter code (e.g. `"us"`)
2. `region` → matched using region ISO code suffix (e.g. `"ca"` → `"US-CA"`)
3. `place` → fuzzy-matched against names in subtypes: `county`, `locality`, or `neighborhood`

This resolves to a Pandas DataFrame containing one or more rows from the in-memory wkls metadata table. At this stage, no geometry is loaded yet — only metadata (like id, name, region, subtype, etc.).

### 2. 📡 Geometry lookup using DuckDB

The geometry lookup is triggered only when you call one of the geometry methods:
- `.wkt()`
- `.wkb()`
- `.hexwkb()`
- `.geojson()`
- `.svg()`

At that point, WKLS uses the previously resolved **GERS ID** to query the Overture **division_area** GeoParquet directly from S3.

The current Overture Maps dataset version can be checked with `wkls.overture_version()`.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started, development setup, and submission guidelines.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENCE) file for details.

## Acknowledgments

- [Overture Maps Foundation](https://overturemaps.org/) for providing high-quality, open geospatial data
- [DuckDB](https://duckdb.org/) for fast analytical queries with spatial support
- [AWS Open Data Registry](https://registry.opendata.aws/) for hosting the dataset
