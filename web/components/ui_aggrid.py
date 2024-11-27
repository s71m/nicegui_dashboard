from typing import Optional

import polars as pl

def map_polars_aggrid_schema(df: pl.DataFrame, checkbox_field: Optional[str] = None) -> list[dict]:
    """Generate AG Grid column definitions using only community features."""
    column_defs = []

    for col_name in df.columns:
        dtype = df.schema[col_name]
        col_def = {
            'field': col_name,
            'headerName': col_name.replace('_', ' ').title(),
            'floatingFilter': True
        }

        # Add checkbox if specified
        if checkbox_field and col_name == checkbox_field:
            col_def['checkboxSelection'] = True
            col_def['headerCheckboxSelection'] = True

        # Configure basic filters based on data type
        if dtype in (pl.Float32, pl.Float64, pl.Int32, pl.Int64):
            col_def['filterParams'] = {
                'filterOptions': ['equals', 'greaterThan', 'lessThan'],
                'defaultOption': 'equals',
                "defaultJoinOperator": "OR"
            }
        elif dtype == pl.Boolean:
            col_def['filter'] = 'agTextColumnFilter'  # Fall back to text filter for booleans
        elif dtype == pl.Date:
            col_def['filter'] = 'agDateColumnFilter'  # Basic date filter
        else:
            col_def['filterParams'] = {
                'filterOptions': ['contains', 'equals', 'startsWith', 'endsWith'],
                'defaultOption': 'contains',
                "defaultJoinOperator": "OR"
            }

        column_defs.append(col_def)

    return column_defs
