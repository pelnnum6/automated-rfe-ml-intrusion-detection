import numpy as np
import os
import matplotlib
matplotlib.use("Agg")  # Saves graphs directly instead of opening a window.
import matplotlib.pyplot as plt
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from rfe_sampling_for2024 import (  # Imports the shared 2024 RFE sampling logic.
    our_random_state,
    label_column,
    count_training_labels,
    calculate_sample_targets,
    create_training_sample
)

tolerance = 0.01  # Select the smallest feature count within 1% of the best Macro F1.

dataset_name = "CIC-IoT-DIAD-2024"
dataset_info = {
    "train_path": "data/scaled_data/CIC-IoT-2024/train.csv",
    "expected_train_rows": 13601431
}
results_dir = "data/feature_selection_results"

def recursive_feature_selection_2024():

    os.makedirs(results_dir, exist_ok=True)  # Creates the output folder for the CSV and graphs.
    label_counts = count_training_labels(
        dataset_name,
        dataset_info
    )  # Gets exact training-class totals using the shared sampling function.

    training_rows = sum(label_counts.values())

    print("Training set shape:", (training_rows, 80))

    sample_targets = calculate_sample_targets(
        label_counts
    )  # Calculates the stratified 300,000-row class targets.

    sample = create_training_sample(
        dataset_name,
        dataset_info,
        label_counts,
        sample_targets
    )  # Creates the memory-safe sample containing all 79 features and Label.
    
    X = sample.drop(columns=[label_column])  # Creates the feature set.
    y = sample[label_column].astype("int8")  # Separates the binary target.

    if label_column in X.columns:
        raise RuntimeError("Label leakage detected inside X.")  # Stops if Label accidentally enters the feature set.

    if X.shape[1] != 79:
        raise ValueError(f"Expected 79 features, but found {X.shape[1]}.")  # Confirms the expected feature count.

    print("Subsampled to:", X.shape)
    print(y.value_counts())

    total_features = X.shape[1]  # Sets the sweep range from 1 through 79 features.
    print("Total number of features:", total_features)

    random_forest = RandomForestClassifier(
        n_estimators=100,
        random_state=our_random_state,
        class_weight="balanced",
        n_jobs=-1
    )  # Uses the exact Random Forest configuration that won the baseline stage.

    print("\nRunning RFE once to build the full feature ranking...")

    ranker = RFE(
        estimator=random_forest,
        n_features_to_select=1,
        step=1
    )  # Removes one feature at a time to create the complete ranking.

    ranker.fit(X, y)  # Fits RFE using training data only.

    ranking = ranker.ranking_  # Gets each feature's RFE rank.
    feature_names = X.columns.tolist()  # Stores the original feature names.
    order = np.argsort(ranking)  # Sorts feature positions from strongest to weakest.

    ordered_features = []

    for index in order:
        ordered_features.append(feature_names[index])  # Builds the ordered feature-name list.

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=our_random_state
    )  # Creates the same training-only five-fold validation used in the baseline.

    feature_counts = []
    macro_f1_scores = []

    for k in range(1, total_features + 1):
        selected_features = ordered_features[:k]  # Keeps the top k ranked features.

        scores = cross_val_score(
            random_forest,
            X[selected_features],
            y,
            cv=cv,
            scoring="f1_macro",
            n_jobs=1,
            error_score="raise"
        )  # Measures the current subset using training-only Macro F1.

        mean_score = scores.mean()  # Calculates the mean Macro F1 across five folds.

        feature_counts.append(k)  # Records the tested feature count.
        macro_f1_scores.append(mean_score)  # Records its cross-validated score.

        print(f"Features: {k}  Macro F1: {round(mean_score, 4)}")

    best_score = max(macro_f1_scores)  # Finds the highest Macro F1 in the sweep.
    threshold = best_score * (1 - tolerance)  # Calculates the relative 1% tolerance threshold.

    chosen_count = total_features  # Uses all features as the fallback.

    for index in range(len(feature_counts)):
        if macro_f1_scores[index] >= threshold:
            chosen_count = feature_counts[index]  # Selects the smallest subset within 1% of the best score.
            break

    chosen_features = ordered_features[:chosen_count]  # Gets the automatically selected feature names.
    chosen_score = macro_f1_scores[chosen_count - 1]  # Gets the selected subset's Macro F1.
    print("\nFeature order (most to least important):")
    print(ordered_features)
    print("\nBest macro F1 in the sweep:", round(best_score, 4))
    print("Threshold (within 1% of best):", round(threshold, 4))
    print("Automatically chosen feature count:", chosen_count)
    print("Chosen macro F1:", round(chosen_score, 4))
    print("\nChosen features:")
    print(chosen_features)
    return chosen_features, chosen_count, chosen_score 

if __name__ == "__main__":  # Prevents RFE from running when this file is imported.

    chosen_features, chosen_count, chosen_score = recursive_feature_selection_2024()