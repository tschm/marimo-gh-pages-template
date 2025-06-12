import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import pandas as pd
    import polars as pl


@app.cell
def _():
    _file = mo.notebook_location() / "public" / "penguins.csv"
    file_str = str(_file)
    return (file_str,)


@app.cell
def _(file_str):
    pd.read_csv(file_str)
    return


@app.cell
def _(file_str):
    pl.read_csv(file_str)
    return


if __name__ == "__main__":
    app.run()
