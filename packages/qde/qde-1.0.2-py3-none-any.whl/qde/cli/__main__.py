# qde/cli/__main__.py
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional
import json

import typer
from rich.console import Console
from rich.table import Table

import numpy as np
import pandas as pd

from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression

# your package public API exposes QDE via qde/__init__.py
from qde import QDE

app = typer.Typer(add_completion=False, help="Quality Data Extractor (QDE) CLI")
console = Console()


# ---------- Estimator shortcuts ----------
def get_estimator(name: str):
    n = name.lower()
    if n in {"gaussiannb", "gnb", "nb"}:
        return GaussianNB()
    if n in {"logreg", "logistic", "logisticregression"}:
        return LogisticRegression(max_iter=200)
    raise typer.BadParameter(f"Unknown estimator '{name}'. Try 'gaussiannb' or 'logreg'.")


# ---------- Distance choice via Enum (works with Typer on Py 3.13) ----------
class DistanceMode(str, Enum):
    euclidean = "euclidean"
    cosine = "cosine"


# ---------- I/O helpers ----------
def load_xy(path: Path, target: str):
    ext = path.suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(path)
        if target not in df.columns:
            raise typer.BadParameter(f"Target '{target}' not found in {path}")
        return df.drop(columns=[target]), df[target]
    if ext in {".parquet", ".pq"}:
        df = pd.read_parquet(path)
        if target not in df.columns:
            raise typer.BadParameter(f"Target '{target}' not found in {path}")
        return df.drop(columns=[target]), df[target]
    if ext == ".npz":
        data = np.load(path)
        if "X" not in data or "y" not in data:
            raise typer.BadParameter(f"{path} must contain arrays 'X' and 'y'")
        return data["X"], data["y"]
    raise typer.BadParameter(f"Unsupported file type: {ext}. Use .csv/.parquet/.npz")


def save_selected(path: Optional[Path], X, y):
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(X, pd.DataFrame):
        df = X.copy()
        df["__target__"] = y.values if isinstance(y, pd.Series) else y
        if path.suffix.lower() in {".parquet", ".pq"}:
            df.to_parquet(path, index=False)
        else:
            df.to_csv(path, index=False)
    else:
        np.savez_compressed(path, X=X, y=y)


# ---------- Commands ----------
@app.command()
def strategies():
    """List strategies registered by QDE (e.g., ces, oes)."""
    qde = QDE()
    tbl = Table(title="Available Strategies", width=80)
    tbl.add_column("name")
    for name in qde._registry.list():
        tbl.add_row(name)
    console.print(tbl)


@app.command()
def run(
    # data
    train: Path = typer.Option(..., exists=True, help="Train file (.csv/.parquet/.npz)"),
    synth: Path = typer.Option(..., exists=True, help="Synthetic file (.csv/.parquet/.npz)"),
    test: Path = typer.Option(..., exists=True, help="Test file (.csv/.parquet/.npz)"),
    target: str = typer.Option("target", help="Target column name for table formats"),
    # algorithm
    strategy: str = typer.Option("ces", help="Strategy: ces | oes"),
    estimator: str = typer.Option("gaussiannb", help="Estimator: gaussiannb | logreg"),
    # OES extras (ignored by CES)
    k_neighbors: int = typer.Option(7, help="OES: number of neighbors"),
    distance_mode: DistanceMode = typer.Option(DistanceMode.euclidean, help="OES: distance"),
    # behavior
    encode_labels: bool = typer.Option(True, help="Encode labels internally during fit"),
    compute_filtered_accuracy: bool = typer.Option(True, help="Compute accuracy on train+synth after selection"),
    # outputs
    out_indices: Optional[Path] = typer.Option(None, help="Save selected indices (.json)"),
    out_selected: Optional[Path] = typer.Option(None, help="Save selected rows (.parquet/.csv/.npz)"),
    out_metrics: Optional[Path] = typer.Option(None, help="Save meta/metrics (.json)"),
):
    """Run QDE on your datasets and write outputs."""
    # load data
    X_tr, y_tr = load_xy(train, target)
    X_sy, y_sy = load_xy(synth, target)
    X_te, y_te = load_xy(test, target)

    # estimator
    est = get_estimator(estimator)

    # orchestrate
    qde = QDE(default_strategy=strategy)
    qde.fit(
        train_X=X_tr, train_y=y_tr,
        syn_X=X_sy,  syn_y=y_sy,
        test_X=X_te, test_y=y_te,
        strategy=strategy,
        encode_labels=encode_labels,
    )

    # strategy extras
    extra = {}
    if strategy.lower() == "oes":
        extra.update(dict(k_neighbors=k_neighbors, distance_mode=distance_mode.value))

    result, X_sel, y_sel = qde.extract(
        estimator=est,
        compute_filtered_accuracy=compute_filtered_accuracy,
        **extra,
    )

    # summary
    console.print(f"[green]Selected[/]: {len(result.indices)} / {len(X_sy)}")
    if result.meta:
        for k, v in result.meta.items():
            console.print(f"  {k}: {v}")

    # save outputs
    if out_indices:
        out_indices.parent.mkdir(parents=True, exist_ok=True)
        out_indices.write_text(json.dumps(result.indices.tolist()))
        console.print(f"Saved indices -> {out_indices}")
    if out_selected:
        save_selected(out_selected, X_sel, y_sel)
        console.print(f"Saved selected rows -> {out_selected}")
    if out_metrics and result.meta:
        out_metrics.parent.mkdir(parents=True, exist_ok=True)
        out_metrics.write_text(json.dumps(result.meta, indent=2))
        console.print(f"Saved metrics -> {out_metrics}")


@app.command()
def version():
    """Print version (if you expose __version__)."""
    try:
        from qde import __version__
        console.print(__version__)
    except Exception:
        console.print("qde (version unknown)")


if __name__ == "__main__":
    app()
