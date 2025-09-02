import duckdb
import importlib.resources
from . import data
import pandas as pd

# Overture Maps dataset version
OVERTURE_VERSION = "2025-05-21.0"
S3_PARQUET_PATH = f"s3://overturemaps-us-west-2/release/{OVERTURE_VERSION}/theme=divisions/type=division_area/*"

COUNTRY_QUERY = """
    SELECT * FROM wkls
    WHERE country = ?
      AND subtype = 'country'
"""

REGION_QUERY = """
    SELECT * FROM wkls
    WHERE country = ?
      AND region = ?
      AND subtype = 'region'
"""

CITY_QUERY = """
    SELECT * FROM wkls
    WHERE country = ?
      AND region = ?
      AND subtype IN ('county', 'locality', 'localadmin')
      AND REPLACE(name, ' ', '') ILIKE REPLACE(?, ' ', '')
"""


def _initialize_table():
    """Initialize the wkls table if it doesn't exist. Called once per module import."""
    # Install and load the spatial extension
    duckdb.sql("INSTALL spatial")
    duckdb.load_extension("spatial")
    duckdb.sql(f"""
        CREATE TABLE IF NOT EXISTS wkls AS
        SELECT id, country, region, subtype, name, division_id
        FROM '{importlib.resources.files(data)}/overture_zstd22.parquet'
    """)


# Initialize the table when the module is imported
_initialize_table()


class ChainableDataFrame(pd.DataFrame):
    """A DataFrame that maintains chaining capability for the wkls library."""

    _metadata = ["_chain"]

    def __init__(self, data, chain=None):
        super().__init__(data)
        object.__setattr__(self, "_chain", chain or [])

    def __getattr__(self, attr):
        # Avoid infinite recursion for pandas internal attributes
        if attr.startswith("_") or attr in ["_chain"]:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{attr}'"
            )

        # Block root-level only methods
        if attr == "overture_version":
            raise AttributeError(
                f"'{attr}' is only available at the root level. Use wkls.{attr}(), not on chained objects."
            )

        # Continue chaining
        new_wkl = Wkl(self._chain + [attr.lower()])
        # Validate chain length immediately
        if len(new_wkl.chain) > 3:
            raise ValueError("Too many chained attributes (max = 3)")
        if len(new_wkl.chain) <= 3:
            df = new_wkl.resolve()
            return ChainableDataFrame(df, new_wkl.chain)
        return new_wkl

    def __getitem__(self, key):
        # If it's a regular pandas indexing operation, use parent class
        if isinstance(key, (str, list, slice)) and not (
            isinstance(key, str) and "%" in key
        ):
            return super().__getitem__(key)

        # Otherwise, handle chaining with search patterns
        new_wkl = Wkl(self._chain + [key.lower()])
        # Validate chain length immediately
        if len(new_wkl.chain) > 3 and "%" not in str(key):
            raise ValueError("Too many chained attributes (max = 3)")
        if "%" in str(key):
            return new_wkl.resolve()
        return new_wkl

    def wkt(self):
        """Get WKT geometry for the first result."""
        wkl = Wkl(self._chain)
        return wkl.wkt()

    def wkb(self):
        """Get WKB geometry for the first result."""
        wkl = Wkl(self._chain)
        return wkl.wkb()

    def hexwkb(self):
        """Get HEX WKB geometry for the first result."""
        wkl = Wkl(self._chain)
        return wkl.hexwkb()

    def geojson(self):
        """Get GeoJSON geometry for the first result."""
        wkl = Wkl(self._chain)
        return wkl.geojson()

    def svg(self):
        """Get SVG geometry for the first result."""
        wkl = Wkl(self._chain)
        return wkl.svg()

    def countries(self):
        """Get all countries."""
        wkl = Wkl(self._chain)
        return wkl.countries()

    def regions(self):
        """Get regions for the current chain."""
        wkl = Wkl(self._chain)
        return wkl.regions()

    def counties(self):
        """Get counties for the current chain."""
        wkl = Wkl(self._chain)
        return wkl.counties()

    def cities(self):
        """Get cities for the current chain."""
        wkl = Wkl(self._chain)
        return wkl.cities()

    def subtypes(self):
        """Get all subtypes."""
        wkl = Wkl(self._chain)
        return wkl.subtypes()

    @property
    def _constructor(self):
        return ChainableDataFrame


class Wkl:
    def __init__(self, chain=None):
        self.chain = chain or []

    def overture_version(self):
        """Return the version of the Overture Maps dataset being used.

        This method is only available at the root level (wkls.overture_version()),
        not on chained objects.
        """
        if self.chain:
            raise ValueError(
                "overture_version() is only available at the root level. Use wkls.overture_version(), not wkls.us.overture_version()."
            )
        return OVERTURE_VERSION

    def __getattr__(self, attr):
        new_wkl = Wkl(self.chain + [attr.lower()])
        # Validate chain length immediately
        if len(new_wkl.chain) > 3:
            raise ValueError("Too many chained attributes (max = 3)")

        if len(new_wkl.chain) <= 3:
            df = new_wkl.resolve()
            return ChainableDataFrame(df, new_wkl.chain)
        return new_wkl

    def __getitem__(self, key):
        new_wkl = Wkl(self.chain + [key.lower()])
        # Validate chain length immediately
        if len(new_wkl.chain) > 3 and "%" not in key:
            raise ValueError("Too many chained attributes (max = 3)")
        # If this looks like a search pattern (contains %), return DataFrame directly
        if "%" in key:
            return new_wkl.resolve()
        return new_wkl

    def __repr__(self):
        return repr(self.resolve())

    def resolve(self):
        if not self.chain:
            raise ValueError(
                "No attributes in the chain. Use wkls.country or wkls.country.region, etc."
            )
        elif len(self.chain) == 1:
            country_iso = self.chain[0].upper()
            query = COUNTRY_QUERY
            params = (country_iso,)
        elif len(self.chain) == 2:
            country_iso = self.chain[0].upper()
            region_iso = country_iso + "-" + self.chain[1].upper()
            query = REGION_QUERY
            params = (country_iso, region_iso)
        elif len(self.chain) == 3:
            country_iso = self.chain[0].upper()
            region_iso = country_iso + "-" + self.chain[1].upper()
            query = CITY_QUERY
            params = (country_iso, region_iso, self.chain[2])
        return duckdb.sql(query, params=params).df()

    def _get_geom_expr(self, expr: str):
        df = self.resolve()
        if df.empty:
            raise ValueError(f"No result found for: {'.'.join(self.chain)}")

        geom_id = df.iloc[0]["id"]
        query = f"""
            SELECT {expr}
            FROM parquet_scan('{S3_PARQUET_PATH}')
            WHERE id = '{geom_id}'
        """
        result_df = duckdb.sql(query).df()
        if result_df.empty:
            raise ValueError(f"No geometry found for ID: {geom_id}")
        return result_df.iloc[0, 0]

    def wkt(self):
        return self._get_geom_expr("ST_AsText(geometry)")

    def wkb(self):
        return self._get_geom_expr("ST_AsWKB(geometry)")

    def hexwkb(self):
        return self._get_geom_expr("ST_AsHEXWKB(geometry)")

    def geojson(self):
        return self._get_geom_expr("ST_AsGeoJSON(geometry)")

    def svg(self):
        return self._get_geom_expr("ST_AsSVG(geometry)")

    def countries(self):
        if self.chain:
            raise ValueError(
                "countries() can only be called on the root object. Use wkls.countries() instead of chaining."
            )

        query = """
            SELECT DISTINCT id, country, subtype, name, division_id
            FROM wkls
            WHERE subtype = 'country'
        """
        df = duckdb.sql(query).df()
        return df

    def regions(self):
        if not self.chain or len(self.chain) > 1:
            raise ValueError(
                "regions() requires exactly one level of chaining. Use wkls.country.regions() to get regions for a country."
            )
        if len(self.chain) == 1:
            country_iso = self.chain[0].upper()
            query = f"""
                SELECT * FROM wkls
                WHERE country = '{country_iso}'
                    AND subtype = 'region'
            """
            df = duckdb.sql(query).df()
            return df

    def counties(self):
        if not self.chain or len(self.chain) > 2:
            raise ValueError(
                "counties() requires exactly two levels of chaining. Use wkls.country.region.counties() to get counties for a region."
            )
        if len(self.chain) == 1:
            raise ValueError(
                "counties() cannot be called on a country alone. Use wkls.country.region.counties() to get counties for a region."
            )
        if len(self.chain) == 2:
            country_iso = self.chain[0].upper()
            region_iso = country_iso + "-" + self.chain[1].upper()
            query = f"""
                SELECT * FROM wkls
                WHERE country = '{country_iso}'
                  AND region = '{region_iso}'
                  AND subtype = 'county'
            """
            df = duckdb.sql(query).df()
            return df

    def cities(self):
        if not self.chain:
            raise ValueError(
                "cities() requires exactly two levels of chaining. Use wkls.country.region.cities() to get cities for a region."
            )
        if len(self.chain) == 1:
            raise ValueError(
                "cities() cannot be called on a country alone. Use wkls.country.region.cities() to get cities for a region."
            )
        if len(self.chain) == 3:
            raise ValueError(
                "cities() cannot be called on a specific city. Use wkls.country.region.cities() to get cities for a region."
            )
        if len(self.chain) > 3:
            raise ValueError(
                "cities() requires exactly two levels of chaining. Use wkls.country.region.cities() to get cities for a region."
            )
        if len(self.chain) == 2:
            country_iso = self.chain[0].upper()
            region_iso = country_iso + "-" + self.chain[1].upper()
            query = f"""
                SELECT * FROM wkls
                WHERE country = '{country_iso}'
                  AND region = '{region_iso}'
                  AND subtype IN ('locality', 'localadmin')
            """
            df = duckdb.sql(query).df()
            return df

    def subtypes(self):
        if self.chain:
            raise ValueError(
                "subtypes() can only be called on the root object. Use wkls.subtypes() instead of chaining."
            )

        query = """
            SELECT DISTINCT subtype FROM wkls
        """
        df = duckdb.sql(query).df()
        return df
