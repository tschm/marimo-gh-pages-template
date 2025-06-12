# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.13.15",
#     "pandas==2.3.0",
#     "polars==1.30.0"
# ]
# ///
import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import pandas as pd
    import polars as pl

    file = mo.notebook_location() / "public" / "penguins.csv"


@app.cell
def _():
    pd.read_csv(str(file))
    return


@app.cell
def _():
    pl.read_csv(str(file))
    return


if __name__ == "__main__":
    app.run()
