Using Poetry for local development

This project includes a `pyproject.toml` configured for Poetry. Use Poetry to create a reproducible virtual environment, install dependencies, run the Streamlit app, and run tests.

1. Install Poetry

Follow the official instructions: https://python-poetry.org/docs/

2. Install dependencies and create the virtual environment

```bash
poetry install
```

3. Run the Streamlit app

```bash
poetry run streamlit run app.py --server.address=0.0.0.0
```

4. Run unit tests

```bash
poetry run pytest -q
```

5. Run shopping carts CLI

```bash
poetry run shopping-carts --file data/shopping_carts.json --out data/report.json
```

Notes

- `pyproject.toml` contains a console script entrypoint `shopping-carts` which maps to `dsa.hash.shopping_carts:main`.
- If you prefer `pip` and `venv`, `requirements.txt` is available but Poetry is recommended for reproducible installs.
