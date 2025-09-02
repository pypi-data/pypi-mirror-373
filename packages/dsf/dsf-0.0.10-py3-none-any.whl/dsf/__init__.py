import pandas as pd
import importlib.resources

datasets = {
    "adult": "Adult census income dataset.",
    "advertising": "The dataset from an organization’s social media ad campaign.",
    "bank": "Bank marketing dataset.",
    "caravan": "Caravan insurance dataset.",
    "cereal": "Cereal nutrition dataset.",
    "churn": "Telecom customer churn dataset.",
    "churncredit": "Credit card churn dataset.",
    "churntel": "Telecom churn dataset (alternative).",
    "corona": "COVID-19 related dataset.",
    "diamonds": "Diamonds dataset from ggplot2.",
    "fertilizer": "Fertilizer use dataset.",
    "house": "House sales dataset.",
    "houseprice": "House price dataset.",
    "insurance": "Insurance dataset.",
    "marketing": "Marketing campaigns dataset.",
    "mpg": "Auto MPG dataset.",
    "redwines": "Red wine quality dataset.",
    "risk": "Risk analysis dataset.",
    "whitewines": "White wine quality dataset."
}

def load(name: str) -> pd.DataFrame:
    """Load a dataset by name as a pandas DataFrame."""
    if name in datasets:
        try:
            with importlib.resources.files("dsf.data").joinpath(f"{name}.pkl").open("rb") as f:
                return pd.read_pickle(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load dataset '{name}': {e}")
    else:
        raise ValueError(f"Dataset '{name}' does not exist.")

# Generate dynamic-width table for __doc__
name_width = max(len(name) for name in datasets) + 2
desc_width = max(len(desc) for desc in datasets) + 2

table_lines = [f"{'Dataset':<{name_width}} {'Description':<{desc_width}}",
               "-" * (name_width + desc_width)]

for name, desc in datasets.items():
    table_lines.append(f"{name:<{name_width}} {desc:<{desc_width}}")

table_text = "\n".join(table_lines)

__doc__ = f"""
DSF package: Example datasets for Python users

Available datasets:
{table_text}

Usage:
>>> import dsf
>>> df = dsf.load('<dataset_name>')  # Load a dataset as a pandas DataFrame
"""