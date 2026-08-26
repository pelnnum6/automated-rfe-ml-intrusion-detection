import pandas as pd
import numpy as np
import os
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier  # On macOS, XGBoost requires `brew install libomp`.


our_random_state = 47  # Uses the same randomization setting as CIC-IoT-2023.
sample_size = 1000000  # Uses the same one-million-row sample size as CIC-IoT-2023.
chunk_size = 250000  # Reads the large training file in memory-safe chunks.

file_path = "data/scaled_data/CIC-IoT-2024/train.csv"
results_dir = "data/baseline_results"
results_file = os.path.join(results_dir, "baseline_model_results_2024.csv")
label_column = "Label"


def count_training_labels_2024(): #this is neeeded since the file is too large to load at once, and exact class totals are required to create a reproducible 1,000,000-row stratified sample.
    label_counts = {0: 0, 1: 0}  
    chunks = pd.read_csv(
        file_path,
        usecols=[label_column],
        chunksize=chunk_size,
        low_memory=False
    )  # Reads only Label because feature values are unnecessary during counting.

    for df in chunks:
        current_counts = df[label_column].astype("int8").value_counts()

        for label, count in current_counts.items():
            if label not in label_counts:  # Stops if anything other than binary 0 and 1 appears.
                raise ValueError(f"Unexpected label found: {label}")

            label_counts[label] += int(count)

    if label_counts[0] == 0 or label_counts[1] == 0:  # Both classes must exist before training.
        raise ValueError(f"Both binary classes were not found: {label_counts}")

    print("Training label counts:", label_counts)
    return label_counts


def calculate_sample_targets_2024(label_counts):
    total_training_rows = sum(label_counts.values())  # Calculates the complete training set size.
    exact_targets = {
        label: count * sample_size / total_training_rows
        for label, count in label_counts.items()}  # Calculates the proportional sample target for each class.

    sample_targets = {label: int(np.floor(target)) for label, target in exact_targets.items()}  # Initially rounds each class target downward.
    remaining_positions = sample_size - sum(sample_targets.values())  # Finds any sample positions still unassigned.
    labels_by_remainder = sorted(
        label_counts,
        key=lambda label: exact_targets[label] - sample_targets[label],
        reverse=True
    )  # Gives remaining positions to the classes with the largest decimal remainder.

    for label in labels_by_remainder[:remaining_positions]:
        sample_targets[label] += 1

    print("Stratified sample targets:", sample_targets)
    return sample_targets


def create_training_sample_2024(label_counts, sample_targets):

    random_generator = np.random.default_rng(our_random_state)  # Makes row selection reproducible with random state.
    remaining_class_rows = label_counts.copy()  # Tracks unread rows from each class.
    remaining_sample_rows = sample_targets.copy()  # Tracks how many sample rows each class still needs.
    sampled_chunks = []  # Stores only selected rows, not the complete training dataset.
    sampled_rows = 0
    chunk_number = 0

    print("Creating stratified 1,000,000 row training sample...")

    chunks = pd.read_csv(
        file_path,
        chunksize=chunk_size,
        low_memory=False
    )  # Reads the complete training file without loading it all into memory.

    for df in chunks:
        chunk_number += 1
        df.columns = df.columns.str.strip()  # Keeps column names consistently referenceable.

        if label_column not in df.columns:
            raise ValueError("The training data does not contain the Label column.")

        labels = df[label_column].astype("int8").to_numpy()
        selected_positions = []

        for label in sorted(label_counts):
            class_positions = np.flatnonzero(labels == label)  # Finds this class inside the current chunk.
            current_class_rows = len(class_positions)

            if current_class_rows == 0:
                continue

            selected_count = random_generator.hypergeometric(
                ngood=remaining_sample_rows[label],
                nbad=remaining_class_rows[label] - remaining_sample_rows[label],
                nsample=current_class_rows
            )  # Selects the correct proportional number of rows from this chunk.

            if selected_count > 0:
                current_positions = random_generator.choice(
                    class_positions,
                    size=selected_count,
                    replace=False
                )  # Randomly chooses rows without choosing the same row twice.

                selected_positions.extend(current_positions.tolist())

            remaining_class_rows[label] -= current_class_rows
            remaining_sample_rows[label] -= int(selected_count)

        if selected_positions:
            selected_positions.sort()
            sampled_chunk = df.iloc[selected_positions].copy()
            sampled_chunks.append(sampled_chunk)
            sampled_rows += len(sampled_chunk)

        if chunk_number % 10 == 0:  # Prints minimal progress every ten chunks.
            print(f"Sampling progress: {sampled_rows:,} rows selected")

    if any(remaining_class_rows.values()) or any(remaining_sample_rows.values()):
        raise RuntimeError("The stratified sample did not allocate every required row correctly.")

    sample = pd.concat(sampled_chunks, ignore_index=True)  # Combines only the selected training rows.

    if len(sample) != sample_size:
        raise RuntimeError(f"Expected {sample_size} sampled rows, but created {len(sample)}.")

    if len(sample.columns) != 80:
        raise ValueError(f"Expected 80 columns, but found {len(sample.columns)}.")

    print("Training sample complete:", sample.shape)
    print("Sample label counts:", sample[label_column].value_counts().sort_index().to_dict())

    return sample


def prepare_X_y_2024(sample):

    X = sample.drop(columns=[label_column])  # Creates X using only the 79 scaled flow features.
    y = sample[label_column].astype("int8")  # Creates y using the numeric binary target.

    if label_column in X.columns:
        raise RuntimeError("Label leakage detected inside X.")

    if X.shape[1] != 79:
        raise ValueError(f"Expected 79 model features, but found {X.shape[1]}.")

    if set(y.unique()) != {0, 1}:
        raise ValueError(f"Expected labels 0 and 1, but found {set(y.unique())}.")

    print("Model data ready:", f"{len(X):,} rows | {X.shape[1]} features")

    return X, y


def create_models_2024(y):

    negative_count = int((y == 0).sum())  # Counts benign rows using training data only.
    positive_count = int((y == 1).sum())  # Counts attack rows using training data only.
    scale_pos_weight = negative_count / positive_count  # Matches the CIC-IoT-2023 XGBoost weighting method.

    print("XGBoost scale_pos_weight:", scale_pos_weight)

    models = {
        "Decision Tree": DecisionTreeClassifier(
            random_state=our_random_state,
            class_weight="balanced"
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            random_state=our_random_state,
            class_weight="balanced",
            n_jobs=-1
        ),

        "XGBoost": XGBClassifier(
            n_estimators=100,
            random_state=our_random_state,
            eval_metric="logloss",
            scale_pos_weight=scale_pos_weight,
            n_jobs=-1
        )
    }  # Uses the same three model configurations as CIC-IoT-2023.

    return models, scale_pos_weight


def evaluate_baseline_models_2024(X, y):

    models, scale_pos_weight = create_models_2024(y)

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=our_random_state
    )  # Creates the same five reproducible stratified folds for every model.

    metrics = {
        "accuracy": "accuracy",
        "precision_weighted": "precision_weighted",
        "recall_weighted": "recall_weighted",
        "f1_weighted": "f1_weighted",
        "precision_macro": "precision_macro",
        "recall_macro": "recall_macro",
        "f1_macro": "f1_macro"
    }  # Records both majority-sensitive weighted metrics and class-balanced macro metrics.

    results = []

    for model_name, model in models.items():
        print(f"\nEvaluating {model_name}...")

        scores = cross_validate(
            model,
            X,
            y,
            cv=cv,
            scoring=metrics,
            n_jobs=1,
            return_train_score=False,
            error_score="raise"
        )  # Runs one fold at a time to prevent excessive memory use.

        result = {
            "Model": model_name,
            "Dataset": "CIC-IoT-DIAD-2024",
            "Sample Size": len(X),
            "Feature Count": X.shape[1],
            "CV Folds": 5,
            "Accuracy Mean": scores["test_accuracy"].mean(),
            "Accuracy Std": scores["test_accuracy"].std(),
            "Weighted Precision Mean": scores["test_precision_weighted"].mean(),
            "Weighted Precision Std": scores["test_precision_weighted"].std(),
            "Weighted Recall Mean": scores["test_recall_weighted"].mean(),
            "Weighted Recall Std": scores["test_recall_weighted"].std(),
            "Weighted F1 Mean": scores["test_f1_weighted"].mean(),
            "Weighted F1 Std": scores["test_f1_weighted"].std(),
            "Macro Precision Mean": scores["test_precision_macro"].mean(),
            "Macro Precision Std": scores["test_precision_macro"].std(),
            "Macro Recall Mean": scores["test_recall_macro"].mean(),
            "Macro Recall Std": scores["test_recall_macro"].std(),
            "Macro F1 Mean": scores["test_f1_macro"].mean(),
            "Macro F1 Std": scores["test_f1_macro"].std(),
            "Average Training Time": scores["fit_time"].mean(),
            "Random State": our_random_state,
            "XGBoost scale_pos_weight": scale_pos_weight if model_name == "XGBoost" else np.nan
        }

        results.append(result)
        print(f"{model_name} complete | Macro F1: {result['Macro F1 Mean']:.6f}")

    results_df = pd.DataFrame(results)
    best_model_name = results_df.loc[results_df["Macro F1 Mean"].idxmax(), "Model"]

    results_df["Selected for RFE"] = results_df["Model"] == best_model_name  # Marks the training-CV winner without accessing test.csv.

    os.makedirs(results_dir, exist_ok=True)
    results_df.to_csv(results_file, index=False)

    print("\nCIC-IoT-DIAD-2024 BASELINE CROSS-VALIDATION COMPLETE")
    print(results_df[["Model", "Accuracy Mean", "Macro F1 Mean", "Average Training Time"]])
    print("Selected RFE estimator:", best_model_name)
    print("Test data accessed: False")
    print("Results saved:", results_file)

    return results_df, best_model_name


def run_baseline_models_2024(): #main function

    if not os.path.exists(file_path):
        print("Training file was not found:", file_path)
        return

    os.makedirs(results_dir, exist_ok=True)

    label_counts = count_training_labels_2024()
    sample_targets = calculate_sample_targets_2024(label_counts)
    sample = create_training_sample_2024(label_counts, sample_targets)
    X, y = prepare_X_y_2024(sample)
    results_df, best_model_name = evaluate_baseline_models_2024(X, y)

    print("\nBASELINE PIPELINE FINISHED")
    print("Models evaluated:", len(results_df))
    print("Best training-CV model:", best_model_name)
    print("Untouched test set remains locked: True")


run_baseline_models_2024()