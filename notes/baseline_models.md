# CIC-IoT-2023 Baseline Models

## Objective

- **Models:** Decision Tree, Random Forest, and XGBoost
    - *why:* comparing multiple classifiers identifies which model provides the strongest binary anomaly-detection performance.
- **Task:** binary anomaly detection
    - `0` = benign
    - `1` = attack
- **Primary selection metric:** Macro F1
- **Selected baseline:** Random Forest

## Data info

- **Training file:** `data/scaled_data/CIC-IoT-2023/train.csv`
- **Testing file:** `data/scaled_data/CIC-IoT-2023/test.csv`
- **Training rows:** 4,385,910
- **Testing rows:** 1,879,676
- **Features:** 39
- **Final columns:** 40 (39 features + Label)
- **Random state:** 47
- **Training sample size:** 1,000,000
- **Cross-validation folds:** 5

### Training class distribution

| Label | Class | Rows |
|---|---|---:|
| 0 | Benign | 102,425 |
| 1 | Attack | 4,283,485 |
| **Total** |  | **4,385,910** |

## Step 1 — Load training data

- Loaded `data/scaled_data/CIC-IoT-2023/train.csv` with Pandas.
- Stored the complete training dataset in `data`.
- Printed the dataset shape and column names.
    - *why:* confirms that the expected 39 features and Label are present.
- Created the results directory with `os.makedirs("data/baseline_results", exist_ok=True)`.

## Step 2 — X / y separation

- Created the feature set with `X = data.drop(columns=["Label"])`.
- Created the target with `y = data["Label"]`.
- `X` contains the 39 scaled features.
- `y` contains the binary target.

## Step 3 — Conditional label encoding

- Checked whether `y.dtype == "object"`.
- If labels were text, `LabelEncoder` would convert them to numerical labels.
- The CIC-IoT-2023 labels were already numerical, so additional encoding was not required.
- Printed `y.value_counts()` to verify the class balance.

## Step 4 — Create the training sample

- Reduced the 4,385,910-row training set to a stratified sample of 1,000,000 rows.
- Calculated the sampling fraction with `sample_size / len(X)`.
- Grouped y by class and sampled the same fraction from each class.
- Used `random_state=47`.
    - *why:* ensures the same training sample is selected every run.
- Used stratified sampling.
    - *why:* preserves the benign/attack distribution in the smaller training sample.

### Sample class distribution

| Label | Class | Rows |
|---|---|---:|
| 0 | Benign | 23,353 |
| 1 | Attack | 976,647 |
| **Total** |  | **1,000,000** |

## Step 5 — Calculate XGBoost class weight

- Calculated `scale_pos_weight` using the sampled training labels.
- Formula: number of Label 0 rows divided by number of Label 1 rows.
- Calculated value: `0.023911402994121724`.
- The testing labels were not used to calculate this value.

## Step 6 — Decision Tree baseline

- Used `DecisionTreeClassifier`.
- **Random state:** 47
    - *why:* ensures reproducible model behaviour.
- **Class weight:** `balanced`
    - *why:* automatically adjusts class weights according to class frequency.

## Step 7 — Random Forest baseline

- Used `RandomForestClassifier`.
- **Number of trees:** 100
    - *why:* creates an ensemble of 100 decision trees.
- **Random state:** 47
    - *why:* ensures reproducible model behaviour.
- **Class weight:** `balanced`
    - *why:* accounts for the strong class imbalance.
- **CPU use:** `n_jobs=-1`
    - *why:* allows Random Forest to use all available CPU cores.

## Step 8 — XGBoost baseline

- Used `XGBClassifier`.
- **Number of estimators:** 100
- **Random state:** 47
- **Evaluation metric:** `logloss`
- **Class weight:** `scale_pos_weight=0.023911402994121724`
- **CPU use:** `n_jobs=-1`
- XGBoost on macOS required `brew install libomp`.

## Step 9 — Cross-validation

- Used `StratifiedKFold`.
- **Number of folds:** 5
- **Shuffle:** enabled
- **Random state:** 47
- Stratification preserved the benign/attack ratio inside every fold.
- All three models were evaluated using the same cross-validation configuration.
- Used `cross_validate(..., n_jobs=1)` so one cross-validation fit ran at a time.

## Step 10 — Evaluation metrics

The following metrics were calculated for every model:

- Accuracy
- Weighted precision
- Weighted recall
- Weighted F1
- Macro precision
- Macro recall
- Macro F1
- Average training time

### Primary metric

- **Primary model-selection metric:** Macro F1
    - *why:* Macro F1 gives the benign and attack classes equal importance.
- Accuracy was recorded but was not used to select the winner.
    - *why:* the training data was approximately 97.66% attack, so accuracy could hide weak benign detection.
- Weighted metrics were recorded for completeness but were influenced strongly by the majority attack class.

## Step 11 — Baseline cross-validation results

| Model | Accuracy | Macro Precision | Macro Recall | Average Training Time |
|---|---:|---:|---:|---:|
| Decision Tree | 0.989226 | 0.884876 | 0.876428 | 1.152482 s |
| Random Forest | 0.990978 | 0.871837 | 0.962320 | 4.869272 s |
| XGBoost | 0.985730 | 0.810588 | 0.991002 | 1.318901 s |

- Random Forest produced the strongest Macro F1.
- Random Forest was selected as the winning baseline model.
- Cross-validation results were saved to `data/baseline_results/baseline_model_results_2023.csv`.

## Step 12 — Select the best model

- Selected the model with the highest value in the `Macro F1` column.
- Used `results_df["Macro F1"].idxmax()` to find the winning model.
- Selected model: Random Forest.
- Fitted the selected Random Forest on the 1,000,000-row sampled training set.

## Step 13 — Final test evaluation

- Loaded `data/scaled_data/CIC-IoT-2023/test.csv`.
- Separated the test features and labels.
- Test shape: 1,879,676 rows and 39 features.
- Used the fitted Random Forest to predict the complete test set.
- Generated:
    - Classification report
    - Confusion matrix
    - False-alarm rate
    - Detection rate
    - Missed-attack count
    - Wrongly flagged benign-flow count

## Final Random Forest test results

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Benign (0) | 0.7481 | 0.9322 | 0.8301 | 43,896 |
| Attack (1) | 0.9984 | 0.9925 | 0.9954 | 1,835,780 |
| **Macro average** | **0.8733** | **0.9623** | **0.9128** | **1,879,676** |
| **Weighted average** | **0.9925** | **0.9911** | **0.9916** | **1,879,676** |

- **Final accuracy:** 0.9911
- **Final Macro F1:** 0.9128
- **Benign F1:** 0.8301
- **Attack F1:** 0.9954

## Confusion matrix

| Actual / Predicted | Benign | Attack |
|---|---:|---:|
| Benign | 40,920 | 2,976 |
| Attack | 13,776 | 1,822,004 |

- **True negatives:** 40,920
- **False positives:** 2,976
- **False negatives:** 13,776
- **True positives:** 1,822,004

## Network-security metrics

- **False-alarm rate:** 0.0677966
    - Approximately 6.78% of benign flows were incorrectly classified as attacks.
- **Detection rate:** 0.9924958
    - Approximately 99.25% of attacks were detected.
- **Missed attacks:** 13,776
- **Wrongly flagged benign flows:** 2,976

## Reproducibility settings

| Setting | Value |
|---|---|
| Dataset | CIC-IoT-2023 |
| Classification mode | Binary |
| Training sample size | 1,000,000 |
| Features | 39 |
| Cross-validation folds | 5 |
| Random state | 47 |
| Primary selection metric | Macro F1 |
| Decision Tree class weight | Balanced |
| Random Forest estimators | 100 |
| Random Forest class weight | Balanced |
| XGBoost estimators | 100 |
| Selected model | Random Forest |

## Final result

- Random Forest produced the strongest cross-validated Macro F1 and was selected as the CIC-IoT-2023 baseline model.
- The final test evaluation achieved 99.11% accuracy and a Macro F1 of 0.9128.
- The difference between weighted F1 and Macro F1 demonstrates the effect of class imbalance.
- The baseline results provide the full-feature reference used to evaluate whether RFE can reduce the 39-feature space while preserving detection performance.



# CIC-IoT-DIAD-2024 Baseline Models

## Objective
- **Models:** Decision Tree, Random Forest, and XGBoost
- **Task:** binary anomaly detection
- **Primary goal:** determine which baseline model produces the strongest Macro F1 and should be used as the estimator for Recursive Feature Elimination (RFE).

## Data info
- **Training file:** `data/scaled_data/CIC-IoT-2024/train.csv`
- **Testing file:** `data/scaled_data/CIC-IoT-2024/test.csv`
- **Training rows:** 13,601,431
- **Testing rows:** 5,829,185
- **Features:** 79
- **Final columns:** 80 (79 features + Label)
- **Random state:** 47
- **Training sample size:** 1,000,000
- **Cross-validation folds:** 5

### Training class distribution
0 (benign)       278,738
1 (attack)    13,322,693
Total         13,601,431

### Testing class distribution
0 (benign)      119,460
1 (attack)    5,709,725
Total          5,829,185


## Leakage prevention rule
- Baseline development uses `train.csv` only.
- `test.csv` remains locked during:
    - Training-sample creation
    - Cross-validation
    - Baseline-model comparison
    - Model selection
    - RFE
    - Feature-count selection
- The test set is opened only after the baseline and RFE decisions are finalized.
- No model is fitted using test rows.
- No feature is selected using test rows.
- No parameter or model is selected using test results.

## Step 1 — Load training data
- Load only `data/scaled_data/CIC-IoT-2024/train.csv`.
    - the test set must remain untouched during model development.
- Read the training file in chunks.
    - *why:* the complete training set contains more than 13.6 million rows and should not be loaded into memory at once.
- Confirm that the training data contains 80 columns: 79 features and Label.
- Confirm that Label contains both binary classes.

## Step 2 — Create the training sample
- Create a stratified 1,000,000 row sample from `train.csv`.
- Use `random_state=47`.
- Preserve the benign/attack ratio.
- Create the sample from training data only.

### Expected sample distribution
0 (benign)       approximately 20,493
1 (attack)       approximately 979,507
Total                        1,000,000

- *why (1,000,000 rows):* this matches the CIC-IoT-2023 baseline sample size, keeps the dataset comparison consistent, and makes five-fold cross-validation manageable on the available computer.
- *why (stratified):* the dataset is strongly imbalanced, so random sampling without stratification could underrepresent the benign class.
- *why (`random_state=47`):* the same sample is produced every run.

## Step 3 — X / y separation

- Separate the sampled training data into:

```python
X = sample.drop("Label", axis=1)
y = sample["Label"]
```

- `X` contains the 79 scaled flow features.
- `y` contains the binary target.
- Confirm that X does not contain Label.
- Confirm that y contains both 0 and 1.
- The target column is never scaled or included as a model feature.

## Step 4 — Cross-validation

- Use five-fold stratified cross-validation:

```python
StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=47
)
```

- *why (`n_splits=5`):* evaluates every model across five validation folds instead of relying on one internal split.
- *why (`shuffle=True`):* randomizes the sampled training rows before creating folds.
- *why (`stratified`):* preserves the benign/attack ratio in every fold.
- *why (`random_state=47`):* produces the same folds every run.
- All three models use the same sample and folds for a fair comparison.

## Step 5 — Decision Tree baseline

```python
DecisionTreeClassifier(
    class_weight="balanced",
    random_state=47
)
```

- **Class weighting:** `balanced`
    - *why:* gives more influence to the minority benign class instead of allowing the majority attack class to dominate the model.
- **Random state:** 47
    - *why:* ensures reproducible model behaviour.

## Step 6 — Random Forest baseline

```python
RandomForestClassifier(
    n_estimators=100,
    class_weight="balanced",
    random_state=47,
    n_jobs=-1
)
```

- **Number of trees:** 100
    - *why:* matches the CIC-IoT-2023 baseline configuration.
- **Class weighting:** `balanced`
    - *why:* accounts for the strong class imbalance.
- **Random state:** 47
    - *why:* ensures reproducible model behaviour.
- **CPU use:** `n_jobs=-1`
    - *why:* allows Random Forest to use all available CPU cores.

## Step 7 — XGBoost baseline

```python
XGBClassifier(
    n_estimators=100,
    eval_metric="logloss",
    random_state=47,
    n_jobs=-1,
    scale_pos_weight=negative_count / positive_count
)
```

- **Number of estimators:** 100
    - *why:* matches the CIC-IoT-2023 baseline configuration.
- **Evaluation metric:** `logloss`
    - *why:* explicitly defines the binary training evaluation metric.
- **Random state:** 47
    - *why:* ensures reproducible model behaviour.
- **CPU use:** `n_jobs=-1`
    - *why:* allows XGBoost to use all available CPU cores.
- **Class weighting:** calculated from the sampled training labels only.
    - *why:* test-label counts must not influence model training.
- Because Label 1 represents the majority attack class, `scale_pos_weight` must be calculated carefully from the sampled training labels.

## Step 8 — Evaluation metrics

- Use `cross_validate()` to calculate:
    - Accuracy
    - Weighted precision
    - Weighted recall
    - Weighted F1
    - Macro precision
    - Macro recall
    - Macro F1
    - Training time

### Primary metric

- **Primary model-selection metric:** Macro F1
    - *why:* Macro F1 calculates performance for benign and attack separately and then gives both classes equal importance.
- Accuracy is recorded but is not used to select the winning model.
    - *why:* approximately 97.95% of the training dataset is attack traffic, so high accuracy can hide weak benign detection.
- Weighted metrics are recorded for completeness but are strongly influenced by the majority attack class.

## Step 9 — Compare baseline models

- Calculate the mean and standard deviation of every five-fold cross-validation metric.
- Record the mean training time.
- Compare Decision Tree, Random Forest, and XGBoost using the same training sample.
- Rank the models using mean Macro F1.
- Do not use `test.csv` to select the winning model.
- No hyperparameter search is performed during the baseline stage.
    - *why:* the purpose of this stage is to establish comparable full-feature baseline performance.

## Step 10 — Select the RFE estimator

- Select the model with the strongest training cross-validation Macro F1.
- Use that model type as the estimator for RFE.
- Run RFE using training data only.
- Select the RFE feature count using training-only validation.
- Record:
    - Selected feature count
    - Selected feature names
    - Feature ranking
    - Feature-reduction percentage
    - Cross-validated Macro F1

## Step 11 — Final test evaluation

- Keep `test.csv` locked until:
    - Baseline configurations are finalized
    - The RFE estimator is finalized
    - The RFE feature count is finalized
    - The selected feature names are finalized
- Apply the predetermined selected features to the test set.
- Evaluate the finalized full-feature and RFE models on the untouched test set.
- The test set is used for final reporting only and never for model development.

## Results to save

- Save baseline cross-validation results to:

```text
results/CIC-IoT-2024/baseline_results.csv
```

- Record:
    - Model name
    - Dataset
    - Sample size
    - Feature count
    - Cross-validation folds
    - Accuracy mean and standard deviation
    - Weighted precision mean and standard deviation
    - Weighted recall mean and standard deviation
    - Weighted F1 mean and standard deviation
    - Macro precision mean and standard deviation
    - Macro recall mean and standard deviation
    - Macro F1 mean and standard deviation
    - Mean training time
    - Random state
    - Class-weighting method
    - Selected baseline model

## Reproducibility settings

```text
Dataset: CIC-IoT-DIAD-2024
Classification mode: Binary
Training sample size: 1,000,000
Model features: 79
Cross-validation folds: 5
Random state: 47
Primary selection metric: Macro F1
Decision Tree class weight: balanced
Random Forest estimators: 100
Random Forest class weight: balanced
XGBoost estimators: 100
Test access during development: prohibited
```

## Final comparison goal

Compare:

```text
CIC-IoT-2023 full-feature baseline
CIC-IoT-2023 RFE-reduced model
CIC-IoT-DIAD-2024 full-feature baseline
CIC-IoT-DIAD-2024 RFE-reduced model
```

The final analysis will determine whether RFE reduces the feature space while preserving binary anomaly-detection performance across both datasets.