import pandas as pd
import numpy as np


our_random_state = 47
sample_size = 300000  
chunk_size = 250000
label_column = "Label"

def count_training_labels(dataset_name, dataset_info):  # Classic, Counts training labels without opening the test set.
    label_counts = {0: 0,1: 0}
    chunks = pd.read_csv(
        dataset_info["train_path"],
        usecols=[label_column],
        chunksize=chunk_size,
        low_memory=False)

    for df in chunks:
        current_counts = df[label_column].astype("int8").value_counts()
        for label, count in current_counts.items():
            if label not in label_counts:
                raise ValueError(f"{dataset_name} contains an unexpected label: {label}")
            label_counts[label] += int(count)
    total_training_rows = sum(label_counts.values())
    if total_training_rows != dataset_info["expected_train_rows"]:
        raise ValueError(
            f"{dataset_name} expected {dataset_info['expected_train_rows']} "
            f"training rows, but found {total_training_rows}."
        )
    if label_counts[0] == 0 or label_counts[1] == 0:
        raise ValueError(f"{dataset_name} does not contain both binary classes.")
    return label_counts


def calculate_sample_targets(label_counts):  # Classic, Preserves each dataset's training class ratio in its 300,000-row sample.

    total_training_rows = sum(label_counts.values())
    exact_targets = {
        label: count * sample_size / total_training_rows
        for label, count in label_counts.items()
    }
    sample_targets = {
        label: int(np.floor(target))
        for label, target in exact_targets.items()
    }
    remaining_positions = sample_size - sum(sample_targets.values())
    labels_by_remainder = sorted(
        label_counts,
        key=lambda label: exact_targets[label] - sample_targets[label],
        reverse=True
    )
    for label in labels_by_remainder[:remaining_positions]:
        sample_targets[label] += 1
    return sample_targets


def create_training_sample(dataset_name, dataset_info, label_counts, sample_targets):  #Classic, Samples training data without accessing test.csv.

    selected_features = dataset_info.get("selected_features")  # Gets selected features when final evaluation supplies them.

    required_columns = (
        selected_features + [label_column]
        if selected_features is not None
        else None
    )  # Loads all columns for RFE or only selected columns for final evaluation.
    
    random_generator = np.random.default_rng(our_random_state)
    remaining_class_rows = label_counts.copy()

    remaining_sample_rows = sample_targets.copy()

    sampled_chunks = []

    chunks = pd.read_csv(
        dataset_info["train_path"],
        usecols=required_columns,
        chunksize=chunk_size,
        low_memory=False
    )

    for df in chunks:

        df.columns = df.columns.str.strip()

        labels = df[label_column].astype("int8").to_numpy()

        selected_positions = []

        for label in sorted(label_counts):

            class_positions = np.flatnonzero(labels == label)

            current_class_rows = len(class_positions)

            if current_class_rows == 0:

                continue

            selected_count = random_generator.hypergeometric(
                ngood=remaining_sample_rows[label],
                nbad=remaining_class_rows[label] - remaining_sample_rows[label],
                nsample=current_class_rows
            )

            if selected_count > 0:

                current_positions = random_generator.choice(
                    class_positions,
                    size=selected_count,
                    replace=False
                )

                selected_positions.extend(current_positions.tolist())

            remaining_class_rows[label] -= current_class_rows

            remaining_sample_rows[label] -= int(selected_count)

        if selected_positions:

            selected_positions.sort()

            sampled_chunks.append(df.iloc[selected_positions].copy())

    if any(remaining_class_rows.values()) or any(remaining_sample_rows.values()):

        raise RuntimeError(f"{dataset_name} sampling did not allocate every required row.")

    sample = pd.concat(
        sampled_chunks,
        ignore_index=True
    )

    if len(sample) != sample_size:

        raise RuntimeError(
            f"{dataset_name} expected a {sample_size}-row sample, "
            f"but created {len(sample)} rows."
        )

    return sample
