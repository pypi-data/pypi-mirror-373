import csv
import json
from ast import literal_eval
from collections import Counter
from contextlib import contextmanager
from os import PathLike
from pathlib import Path
from typing import Annotated, cast

import click
import joblib
import numpy as np
import sklearn
import typer
from CDPL.Chem import (
    Atom,  # pyright:ignore[reportAttributeAccessIssue]
    AtomProperty,  # pyright:ignore[reportAttributeAccessIssue]
    BasicMolecule,  # pyright:ignore[reportAttributeAccessIssue]
    FileSDFMoleculeReader,  # pyright:ignore[reportAttributeAccessIssue]
    MolecularGraph,  # pyright:ignore[reportAttributeAccessIssue]
    generateSMILES,  # pyright:ignore[reportAttributeAccessIssue]
    getStructureData,  # pyright:ignore[reportAttributeAccessIssue]
    parseSMILES,  # pyright:ignore[reportAttributeAccessIssue]
)
from rich.console import Console
from rich.json import JSON
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from scipy.stats import entropy
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    make_scorer,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    GroupKFold,
    TunedThresholdClassifierCV,
)
from sklearn.pipeline import make_pipeline

from fame3r import FAME3RScoreEstimator, FAME3RVectorizer


def extract_som_labels(mol: MolecularGraph) -> list[tuple[Atom, bool]]:
    structure_data = {
        entry.header.split("<")[1].split(">")[0]: entry.data
        for entry in getStructureData(mol)
    }
    som_indices = (
        literal_eval(structure_data["soms"]) if "soms" in structure_data else []
    )

    return [(atom, atom.index in som_indices) for atom in mol.atoms]


def read_labeled_atoms_from_sdf(path: PathLike) -> list[tuple[Atom, bool]]:
    results = []

    reader = FileSDFMoleculeReader(str(path))
    mol = BasicMolecule()
    while reader.read(mol):
        results.extend(extract_som_labels(mol))
        mol = BasicMolecule()

    return results


def read_labeled_atoms_from_smi(path: PathLike) -> list[tuple[Atom, bool]]:
    results = []

    for smiles in Path(path).read_text().splitlines():
        mol = parseSMILES(smiles)
        results.extend(
            (atom, bool(atom.getProperty(AtomProperty.ATOM_MAPPING_ID)))
            for atom in mol.atoms
        )

    return results


def read_labeled_atoms(path: PathLike) -> list[tuple[Atom, bool]]:
    ext = Path(path).suffix

    if ext == ".smi":
        return read_labeled_atoms_from_smi(path)
    elif ext in [".sdf", ".mol2", ".mol"]:
        return read_labeled_atoms_from_sdf(path)
    else:
        raise RuntimeError(f"Unknown file format extension `{ext}`.")


def top2_rate_score(y_true, y_prob, groups):
    unique_groups, _ = np.unique(groups, return_index=True)
    top2_sucesses = 0

    for current_group in unique_groups:
        mask = groups == current_group

        # Sort by predicted probability (descending) and take the top 2
        top_2_indices = np.argsort(y_prob[mask])[-2:]
        if y_true[mask][top_2_indices].sum() > 0:
            top2_sucesses += 1

    return top2_sucesses / len(unique_groups)


stdout = Console()
stderr = Console(stderr=True)


@contextmanager
def Spinner(*, title: str):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}[/]"),
        TimeElapsedColumn(),
        transient=True,
        console=stderr,
    ) as progress:
        progress.add_task(description=title, total=None)
        yield
        time_elapsed = TimeElapsedColumn().render(progress.tasks[-1])

    stderr.print(
        f"[progress.spinner]⠿[/] {title} [progress.elapsed]{time_elapsed}[/]",
        highlight=False,
    )


app = typer.Typer(add_completion=False)


@app.command(
    name="train",
    help="Train a FAME3R model and/or scorer on SOM data.",
)
def train(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to input training data (SDF, SMILES).",
        ),
    ],
    models_path: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Path to model output directory.",
        ),
    ],
    radius: Annotated[
        int,
        typer.Option(
            "--radius",
            help="Atom environment radius in bonds.",
        ),
    ] = 5,
    model_kinds: Annotated[
        list[str],
        typer.Option(
            "--kind",
            help="Models to train.",
            click_type=click.Choice(["random-forest", "fame-scorer"]),
        ),
    ] = ["random-forest", "fame-scorer"],
    hyperparameter_path: Annotated[
        Path | None,
        typer.Option(
            "--hyperparameters",
            help="Path to JSON file containing model hyperparameters.",
        ),
    ] = None,
    n_neighbors: Annotated[
        int, typer.Option(help="Number of neighbors for FAME score estimator.")
    ] = 3,
):
    atoms = read_labeled_atoms(input_path)

    atom_count = len(atoms)
    mol_count = len({atom.molecule.getObjectID() for atom, _ in atoms})

    # Required because CDPKit atom defines __getitem__
    atom_array = np.empty((atom_count, 1), dtype=object)
    atom_array[:, 0] = [atom for atom, _ in atoms]

    if "random-forest" in model_kinds:
        hyperparameters = (
            json.loads(hyperparameter_path.read_text())
            if hyperparameter_path
            else {
                "n_estimators": 250,
                "max_depth": None,
                "min_samples_split": 2,
                "min_samples_leaf": 1,
                "max_features": "sqrt",
                "class_weight": "balanced_subsample",
            }
        )

        with Spinner(
            title=f"Training random forest on {atom_count} atoms ({mol_count} molecules)"
        ):
            score_pipeline = make_pipeline(
                FAME3RVectorizer(radius=radius, input="cdpkit"),
                RandomForestClassifier(random_state=42, **hyperparameters),
            ).fit(
                atom_array,
                [label for _, label in atoms],
            )

        models_path.mkdir(exist_ok=True, parents=True)
        joblib.dump(
            score_pipeline.named_steps["randomforestclassifier"],
            models_path / "random_forest_classifier.joblib",
            compress=3,
        )

    if "fame-scorer" in model_kinds:
        with Spinner(
            title=f"Training FAME score estimator on {atom_count} atoms ({mol_count} molecules)"
        ):
            score_pipeline = make_pipeline(
                FAME3RVectorizer(radius=radius, input="cdpkit", output=["fingerprint"]),
                FAME3RScoreEstimator(n_neighbors=n_neighbors),
            ).fit(
                atom_array,
                [label for _, label in atoms],
            )

        models_path.mkdir(exist_ok=True, parents=True)
        joblib.dump(
            score_pipeline.named_steps["fame3rscoreestimator"],
            models_path / "fame3r_score_estimator.joblib",
            compress=3,
        )


@app.command(
    name="predict",
    help="Predict SOMs using an existing FAME3R model.",
)
def predict(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to input data for which to predict SOMs (SDF, SMILES).",
        ),
    ],
    models_path: Annotated[
        Path,
        typer.Option(
            "--models",
            "-m",
            help="Path to existing model directory.",
        ),
    ],
    output_path: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Path to output prediction CSV file.",
        ),
    ],
    radius: Annotated[
        int,
        typer.Option(
            "--radius",
            help="Atom environment radius in bonds.",
        ),
    ] = 5,
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            help="Prediction probability threshold.",
        ),
    ] = 0.3,
    uncertainty_kinds: Annotated[
        list[str],
        typer.Option(
            "--uncertainty",
            help="Uncertainty quantification scores to compute.",
            click_type=click.Choice(["fame-score", "shannon-entropy"]),
        ),
    ] = [],
):
    atoms = read_labeled_atoms(input_path)
    containing_mol_indices = {
        object_id: index
        for index, object_id in enumerate(
            {atom.molecule.getObjectID(): None for atom, _ in atoms}
        )
    }

    atom_count = len(atoms)
    mol_count = len(containing_mol_indices)

    # Required because CDPKit atom defines __getitem__
    atom_array = np.empty((atom_count, 1), dtype=object)
    atom_array[:, 0] = [atom for atom, _ in atoms]

    classifier = joblib.load(models_path / "random_forest_classifier.joblib")
    clf_pipeline = make_pipeline(
        FAME3RVectorizer(radius=radius, input="cdpkit").fit(), classifier
    )

    with Spinner(
        title=f"Predicting SOM probabilities for {atom_count} atoms ({mol_count} molecules)"
    ):
        prediction_probabilities = clf_pipeline.predict_proba(atom_array)[:, 1]
        predictions_binary = prediction_probabilities > threshold

    if "fame-score" in uncertainty_kinds:
        score_estimator = joblib.load(models_path / "fame3r_score_estimator.joblib")
        score_pipeline = make_pipeline(
            FAME3RVectorizer(
                radius=radius, input="cdpkit", output=["fingerprint"]
            ).fit(),
            score_estimator,
        )

        with Spinner(
            title=f"Predicting FAME scores for {atom_count} atoms ({mol_count} molecules)"
        ):
            fame_scores = score_pipeline.predict(atom_array)
    else:
        fame_scores = np.full_like(prediction_probabilities, np.nan)

    if "shannon-entropy" in uncertainty_kinds:
        with Spinner(
            title=f"Predicting Shannon entropy for {atom_count} atoms ({mol_count} molecules)"
        ):
            shannon_entropies = cast(
                np.ndarray,
                entropy(
                    [prediction_probabilities, 1 - prediction_probabilities],
                    base=2,
                ),
            )
    else:
        shannon_entropies = np.full_like(prediction_probabilities, np.nan)

    with output_path.open("w", encoding="UTF-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "smiles",
                "mol_id",
                "atom_id",
                "y_true",
                "y_pred",
                "y_prob",
                "fame_score",
                "shannon_entropy",
            ],
        )
        writer.writeheader()

        for i in range(len(atoms)):
            writer.writerow(
                {
                    "smiles": generateSMILES(atoms[i][0].molecule),
                    "mol_id": containing_mol_indices[
                        atoms[i][0].molecule.getObjectID()
                    ],
                    "atom_id": atoms[i][0].index,
                    "y_true": int(atoms[i][1]),
                    "y_pred": int(predictions_binary[i]),
                    "y_prob": np.round(prediction_probabilities[i], 2),
                    "fame_score": np.round(fame_scores[i], 2),
                    "shannon_entropy": np.round(shannon_entropies[i], 2),
                }
            )


@app.command(
    name="metrics",
    help="Calculate metrics for existing SOM predictions.",
)
def metrics(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to input prediction CSV file.",
        ),
    ],
    output_path: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Path to output metrics JSON file.",
        ),
    ] = None,
    n_bootstrap_samples: Annotated[
        int | None,
        typer.Option(
            "--bootstrap",
            help="Number of bootstrapping samples to perform.",
        ),
    ] = None,
):
    rows = [row for row in csv.DictReader(input_path.open())]

    smiles_full = np.array([row["smiles"] for row in rows], dtype=str)
    y_true_full = np.array([int(row["y_true"]) for row in rows], dtype=bool)
    y_pred_full = np.array([int(row["y_pred"]) for row in rows], dtype=bool)
    y_prob_full = np.array([row["y_prob"] for row in rows], dtype=float)

    computed_metrics_samples = []
    unique_smiles = np.unique(smiles_full)
    rng = np.random.default_rng(0)

    if n_bootstrap_samples:
        with Spinner(title=f"Performing {n_bootstrap_samples} bootstraps"):
            for _ in range(n_bootstrap_samples):
                counter = Counter(
                    rng.choice(unique_smiles, size=len(unique_smiles), replace=True)
                )
                repeats = [counter[it] for it in smiles_full]

                smiles = np.repeat(smiles_full, repeats)
                y_true = np.repeat(y_true_full, repeats)
                y_pred = np.repeat(y_pred_full, repeats)
                y_prob = np.repeat(y_prob_full, repeats)

                computed_metrics_samples.append(
                    {
                        "roc_auc": roc_auc_score(y_true, y_prob),
                        "average_precision": average_precision_score(y_true, y_prob),
                        "f1": f1_score(y_true, y_pred),
                        "matthews_corrcoef": matthews_corrcoef(y_true, y_pred),
                        "precision": precision_score(y_true, y_pred),
                        "recall": recall_score(y_true, y_pred),
                        "top2_rate": top2_rate_score(y_true, y_prob, smiles),
                    }
                )
    else:
        computed_metrics_samples.append(
            {
                "roc_auc": roc_auc_score(y_true_full, y_prob_full),
                "average_precision": average_precision_score(y_true_full, y_prob_full),
                "f1": f1_score(y_true_full, y_pred_full),
                "matthews_corrcoef": matthews_corrcoef(y_true_full, y_pred_full),
                "precision": precision_score(y_true_full, y_pred_full),
                "recall": recall_score(y_true_full, y_pred_full),
                "top2_rate": top2_rate_score(y_true_full, y_prob_full, smiles_full),
            }
        )

    computed_metrics = {
        key: {
            "mean": np.round(np.mean(values), 4),
            "std": np.round(np.std(values), 4),
        }
        for key, values in {
            key: [sample[key] for sample in computed_metrics_samples]
            for key in computed_metrics_samples[0].keys()
        }.items()
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(computed_metrics, indent=4))
    else:
        stderr.print(JSON.from_data(computed_metrics))


@app.command(
    name="hyperparameters",
    help="Perform CV hyperparameter search for a FAME3R model.",
)
def hyperparameters(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to input training data (SDF, SMILES).",
        ),
    ],
    output_path: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Path to output hyperparameter JSON file.",
        ),
    ] = None,
    radius: Annotated[
        int,
        typer.Option(
            "--radius",
            help="Atom environment radius in bonds.",
        ),
    ] = 5,
    num_folds: Annotated[
        int,
        typer.Option(
            "--num-folds",
            help="Number of cross-validation folds to perform.",
        ),
    ] = 10,
):
    # Required for passing KFold groups to cross-validation
    sklearn.set_config(enable_metadata_routing=True)

    atoms = read_labeled_atoms(input_path)

    labels = [label for _, label in atoms]
    containing_mol_ids = [atom.molecule.getObjectID() for atom, _ in atoms]

    atom_count = len(atoms)
    mol_count = len(set(containing_mol_ids))

    # Required because CDPKit atom defines __getitem__
    atom_array = np.empty((atom_count, 1), dtype=object)
    atom_array[:, 0] = [atom for atom, _ in atoms]

    with Spinner(
        title=f"Computing descriptors for {atom_count} atoms ({mol_count} molecules)"
    ):
        descriptors = FAME3RVectorizer(radius=radius, input="cdpkit").fit_transform(
            atom_array
        )

    k_fold = GroupKFold(n_splits=num_folds, random_state=42, shuffle=True)

    with Spinner(title=f"Performing CV on {atom_count} atoms ({mol_count} molecules)"):
        grid_search = GridSearchCV(
            RandomForestClassifier(random_state=42),
            {
                "n_estimators": [100, 250, 500, 750],
                "max_depth": [None, 10, 20, 30],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2"],
                "class_weight": ["balanced", "balanced_subsample"],
            },
            cv=k_fold,
            scoring=make_scorer(average_precision_score, greater_is_better=True),
            n_jobs=4,
        ).fit(descriptors, labels, groups=containing_mol_ids)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(grid_search.best_params_, indent=4))
    else:
        stdout.print(JSON.from_data(grid_search.best_params_))


@app.command(
    name="threshold",
    help="Perform CV threshold post-tuning for a FAME3R model.",
)
def threshold(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to input training data (SDF, SMILES).",
        ),
    ],
    model_path: Annotated[
        Path,
        typer.Option(
            "--models",
            "-m",
            help="Path to existing FAME3R classifier model file.",
        ),
    ],
    output_path: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Path to output threshold JSON file.",
        ),
    ] = None,
    radius: Annotated[
        int,
        typer.Option(
            "--radius",
            help="Atom environment radius in bonds.",
        ),
    ] = 5,
    num_folds: Annotated[
        int,
        typer.Option(
            "--num-folds",
            help="Number of cross-validation folds to perform.",
        ),
    ] = 10,
):
    # Required for passing KFold groups to cross-validation
    sklearn.set_config(enable_metadata_routing=True)

    atoms = read_labeled_atoms(input_path)

    labels = [label for _, label in atoms]
    containing_mol_ids = [atom.molecule.getObjectID() for atom, _ in atoms]

    atom_count = len(atoms)
    mol_count = len(set(containing_mol_ids))

    # Required because CDPKit atom defines __getitem__
    atom_array = np.empty((atom_count, 1), dtype=object)
    atom_array[:, 0] = [atom for atom, _ in atoms]

    with Spinner(
        title=f"Computing descriptors for {atom_count} atoms ({mol_count} molecules)"
    ):
        descriptors = FAME3RVectorizer(radius=radius, input="cdpkit").fit_transform(
            atom_array
        )

    k_fold = GroupKFold(n_splits=num_folds, random_state=42, shuffle=True)

    classifier = joblib.load(model_path)

    with Spinner(
        title=f"Tuning threshold on {atom_count} atoms ({mol_count} molecules)"
    ):
        tuner = TunedThresholdClassifierCV(
            classifier,
            scoring="matthews_corrcoef",
            cv=k_fold,
            # Multiple jobs with TunedThresholdClassifierCV are buggy
            n_jobs=1,
            random_state=42,
        ).fit(descriptors, labels, groups=containing_mol_ids)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(tuner.best_threshold_, indent=4))
    else:
        stdout.print(JSON.from_data({"best_threshold": tuner.best_threshold_}))


@app.command(
    name="descriptors",
    help="Compute FAME3R descriptors for external use.",
)
def descriptors(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to input data (SDF, SMILES).",
        ),
    ],
    output_path: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Path to output descriptors CSV file.",
        ),
    ],
    radius: Annotated[
        int,
        typer.Option(
            "--radius",
            help="Atom environment radius in bonds.",
        ),
    ] = 5,
    included_descriptors: Annotated[
        list[str],
        typer.Option(
            "--subset",
            help="Subsets of FAME3R descriptors to generate.",
            click_type=click.Choice(
                ["fingerprint", "counts", "physicochemical", "topological"]
            ),
        ),
    ] = ["fingerprint", "physicochemical", "topological"],
):
    atoms = read_labeled_atoms(input_path)
    containing_mol_indices = {
        object_id: index
        for index, object_id in enumerate(
            {atom.molecule.getObjectID(): None for atom, _ in atoms}
        )
    }

    atom_count = len(atoms)
    mol_count = len(containing_mol_indices)

    # Required because CDPKit atom defines __getitem__
    atom_array = np.empty((atom_count, 1), dtype=object)
    atom_array[:, 0] = [atom for atom, _ in atoms]

    vectorizer = FAME3RVectorizer(
        radius=radius,
        input="cdpkit",
        output=included_descriptors,  # pyright:ignore[reportArgumentType]
    )

    with Spinner(
        title=f"Computing descriptors for {atom_count} atoms ({mol_count} molecules)"
    ):
        descriptors = vectorizer.fit_transform(atom_array)

    output_path.parent.mkdir(exist_ok=True, parents=True)
    with (
        Spinner(title=f"Writing descriptors for {atom_count} atoms to output file"),
        output_path.open("w", encoding="UTF-8", newline="") as f,
    ):
        writer = csv.writer(f)
        writer.writerow(
            ["smiles", "mol_id", "atom_id"] + vectorizer.get_feature_names_out()
        )

        for i in range(len(atoms)):
            writer.writerow(
                [
                    generateSMILES(atoms[i][0].molecule),
                    containing_mol_indices[atoms[i][0].molecule.getObjectID()],
                    atoms[i][0].index,
                ]
                + list(descriptors[i])
            )


if __name__ == "__main__":
    app()
