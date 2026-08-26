import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from rfe_sampling_for2024 import ( #we call our rfe sampling function
    our_random_state,
    sample_size,
    chunk_size,
    label_column,
    count_training_labels,
    calculate_sample_targets,
    create_training_sample
) 

#our classic configurations
results_dir = "data/feature_selection_final_results"
comparison_path = os.path.join(
    results_dir,
    "rfe_final_evaluation_comparison.csv"
)

datasets = { 

    "CIC-IoT-2023": {

        "train_path": "data/scaled_data/CIC-IoT-2023/train.csv",

        "test_path": "data/scaled_data/CIC-IoT-2023/test.csv",

        "expected_train_rows": 4385910,

        "expected_test_rows": 1879676,

        "selected_features": [
            "Number",
            "ack_flag_number",
            "HTTPS",
            "AVG",
            "Tot size",
            "Rate",
            "Header_Length",
            "Tot sum",
            "Time_To_Live",
            "ack_count",
            "IAT",
            "Std",
            "Max",
            "psh_flag_number",
            "Variance",
            "TCP",
            "Min"
        ]
    },

    "CIC-IoT-DIAD-2024": {

        "train_path": "data/scaled_data/CIC-IoT-2024/train.csv",

        "test_path": "data/scaled_data/CIC-IoT-2024/test.csv",

        "expected_train_rows": 13601431,

        "expected_test_rows": 5829185,

        "selected_features": [
            "Flow IAT Min",
            "Flow IAT Max",
            "Packet Length Variance",
            "Packet Length Std",
            "Fwd Segment Size Avg",
            "Total Length of Bwd Packet",
            "Flow IAT Mean",
            "Total Length of Fwd Packet",
            "Fwd IAT Min",
            "Average Packet Size",
            "FWD Init Win Bytes",
            "Bwd Segment Size Avg",
            "Src Port",
            "Packet Length Max",
            "Dst Port"
        ]
    }
}

  

def train_selected_feature_model(dataset_name, dataset_info, training_sample):  # Trains Random Forest using only the fixed RFE-selected features.

    selected_features = dataset_info["selected_features"]

    X_train = training_sample[selected_features]

    y_train = training_sample[label_column].astype("int8")

    if label_column in X_train.columns:

        raise RuntimeError(f"Label leakage detected inside {dataset_name} X_train.")

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=our_random_state,
        class_weight="balanced",
        n_jobs=-1
    )

    print(f"Training {dataset_name} with {len(selected_features)} selected features...")

    model.fit(
        X_train,
        y_train
    )

    print(f"{dataset_name} training complete.")

    return model


def evaluate_test_set(dataset_name, dataset_info, model):  # Opens the dataset's test set only after its final model is trained.

    selected_features = dataset_info["selected_features"]

    required_columns = selected_features + [label_column]

    true_label_chunks = []

    predicted_label_chunks = []

    processed_rows = 0

    print(f"Evaluating {dataset_name} test set...")

    chunks = pd.read_csv(
        dataset_info["test_path"],
        usecols=required_columns,
        chunksize=chunk_size,
        low_memory=False
    )

    for df in chunks:

        df.columns = df.columns.str.strip()

        X_test_chunk = df[selected_features]

        y_test_chunk = df[label_column].astype("int8").to_numpy()

        if label_column in X_test_chunk.columns:

            raise RuntimeError(f"Label leakage detected inside {dataset_name} X_test.")

        predictions = model.predict(X_test_chunk).astype("int8")

        true_label_chunks.append(y_test_chunk)

        predicted_label_chunks.append(predictions)

        processed_rows += len(df)

        if processed_rows % 2500000 < chunk_size:

            print(f"{dataset_name} testing progress: {processed_rows:,} rows")

    if processed_rows != dataset_info["expected_test_rows"]:

        raise ValueError(
            f"{dataset_name} expected {dataset_info['expected_test_rows']} "
            f"test rows, but found {processed_rows}."
        )

    y_test = np.concatenate(true_label_chunks)

    y_pred = np.concatenate(predicted_label_chunks)

    return y_test, y_pred


def calculate_final_results(dataset_name, dataset_info, y_test, y_pred):  # Calculates the same final measurements for both datasets.

    matrix = confusion_matrix(
        y_test,
        y_pred,
        labels=[0, 1]
    )

    true_negative, false_positive, false_negative, true_positive = matrix.ravel()

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    macro_f1 = f1_score(
        y_test,
        y_pred,
        average="macro"
    )

    false_alarm_rate = false_positive / (false_positive + true_negative)

    detection_rate = true_positive / (true_positive + false_negative)

    report = classification_report(
        y_test,
        y_pred,
        labels=[0, 1],
        target_names=["Benign (0)", "Attack (1)"],
        digits=4
    )

    print(f"\n{dataset_name} RFE FINAL EVALUATION")
    print("Selected features:", len(dataset_info["selected_features"]))
    print("Test rows:", len(y_test))
    print("Accuracy:", accuracy)
    print("Macro F1:", macro_f1)
    print("\nClassification report:")
    print(report)
    print("Confusion matrix:")
    print(matrix)
    print("False alarm rate:", false_alarm_rate)
    print("Detection rate:", detection_rate)
    print("Missed attacks:", false_negative)
    print("Wrongly flagged benign flows:", false_positive)

    return {
        "Dataset": dataset_name,
        "Model": "Random Forest",
        "Training Sample Rows": sample_size,
        "Selected Features": len(dataset_info["selected_features"]),
        "Test Rows": len(y_test),
        "Accuracy": accuracy,
        "Macro F1": macro_f1,
        "False Alarm Rate": false_alarm_rate,
        "Detection Rate": detection_rate,
        "Missed Attacks": int(false_negative),
        "Wrongly Flagged Benign Flows": int(false_positive)
    }


def evaluate_dataset(dataset_name, dataset_info):  # Runs one dataset from training-label counting through final test evaluation.

    label_counts = count_training_labels( #from our rfe sampling function
        dataset_name,
        dataset_info
    )

    sample_targets = calculate_sample_targets( #from our rfe sampling function
        label_counts
    )   
    print(f"\nPreparing {dataset_name}...")
    print("Training label counts:", label_counts)
    print("Stratified sample targets:", sample_targets)

    training_sample = create_training_sample( #from our rfe sampling function
        dataset_name,
        dataset_info,
        label_counts,
        sample_targets
    )

    print("Training sample shape:", training_sample.shape)
    print("Training sample labels:", training_sample[label_column].value_counts().to_dict())

    model = train_selected_feature_model(
        dataset_name,
        dataset_info,
        training_sample
    )

    y_test, y_pred = evaluate_test_set(
        dataset_name,
        dataset_info,
        model
    )

    return calculate_final_results(
        dataset_name,
        dataset_info,
        y_test,
        y_pred
    )


def run_rfe_final_evaluation():  # Evaluates both fixed RFE models and saves one comparison table.

    os.makedirs(
        results_dir,
        exist_ok=True
    )

    final_results = []

    for dataset_name, dataset_info in datasets.items():

        result = evaluate_dataset(
            dataset_name,
            dataset_info
        )

        final_results.append(result)

    comparison = pd.DataFrame(final_results)

    comparison.to_csv(
        comparison_path,
        index=False
    )

    print("\nRFE FINAL EVALUATION COMPLETE")
    print(comparison)
    print("Results saved:", comparison_path)


if __name__ == "__main__":  # Prevents the full evaluation from running if this file is imported elsewhere.

    run_rfe_final_evaluation()