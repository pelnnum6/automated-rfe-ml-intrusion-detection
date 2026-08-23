# CIC-IoT-2023 Recursive Feature Elimination Notes

## What this step is for
Baseline training used all 39 features. This step asks a different question: **how many of those 39 are actually needed?**

The idea is that some features carry the same information as others, or carry almost none at all. If they can be dropped without hurting detection, the model gets smaller, faster to train, and easier to explain — which matters for an IDS that has to keep up with live traffic.

The output of this step is a **reduced feature set** plus the evidence for why that particular size was chosen.

- **Script:** `Recursive_Feature_Selection.py`
- **Input:** `data/scaled_data/CIC-IoT-2023/train.csv` (the scaled train set from `data_preprocessing_2.py`)
- **Outputs:** `data/feature_selection_results/` — one CSV table and two graphs

---

## How RFE works (plain language)
Recursive Feature Elimination is a "last one standing" contest between features.

1. Train the model using every feature.
2. Ask the model which feature it relied on least.
3. Throw that one out.
4. Repeat with the features that are left.

Keep going and the features get knocked out one at a time, worst first, until only one remains. The **order they get knocked out in** is the useful part: a feature eliminated at the very end was important, a feature eliminated immediately was not.

*Why "recursive":* the model is retrained after every removal. It does not rank all 39 once and stop. Removing a feature can change how important the remaining ones look, so the ranking is rebuilt each round.

---

## Step 1 — Load the training set only
- Reads `train.csv`. The test set is never opened in this script.
    - *why:* choosing features is a decision **learned from data**. If the test set helped decide which features to keep, then the final test score would be measuring a model that had already peeked at its own exam. The test set stays sealed until after selection is finished.
- This is the same leakage rule as Step 5–6 of preprocessing, applied one level up: there it was the scaler, here it is the feature choice.

## Step 2 — Stratified subsample to 300,000 rows
- `sample_size = 300000`, sampled with `y.groupby(y).sample(frac=..., random_state=47)`
    - *why (subsample at all):* RFE retrains the model dozens of times instead of once. The baselines used 1,000,000 rows because they only fit each model once. Running that many rows through this many refits would take hours for no extra accuracy.
    - *why (stratified):* `groupby(y).sample()` takes the same fraction **from each class separately**, so the ~2.34% benign ratio survives the subsample. A plain random sample would still contain benign rows, but the ratio could drift — and since benign is the rare class, drift would move the macro F1 score for reasons that have nothing to do with features.
    - *why (random_state=47):* same subsample every run, so the sweep is reproducible.

## Step 3 — The estimator
```python
RandomForestClassifier(n_estimators=100, random_state=47, class_weight="balanced", n_jobs=-1)
```
- Random Forest, chosen because it won the baseline comparison on macro F1.
- **This is the exact same configuration as in `baseline_models_2023.py`** — same number of trees, same class weighting, same seed.
    - *why this matters:* the point of the sweep is to measure the effect of **removing features**. If the model setup also changed, there would be no way to tell whether a score dropped because features were removed or because the model was different. Holding the model fixed means every change in the results is attributable to the features.
- The same model object does two jobs: it ranks the features inside RFE, and it scores each feature subset during the sweep.

## Step 4 — Build the elimination order (RFE runs once)
- `RFE(estimator=random_forest, n_features_to_select=1)` then read `ranker.ranking_`
- `ranking_` gives every feature a number: **rank 1 = the last feature standing** (most important), and larger numbers were eliminated earlier.
- `np.argsort(ranking)` sorts those ranks into the running order, most important first.

*why RFE is called once instead of 39 times:* RFE removes exactly one feature per round, in order of importance. That elimination order does not depend on where you decide to stop. Asking RFE for 10 features gives the same 10 that survive when you run it all the way down — it just halts earlier. So running it once to a single feature produces the full ordering, and "the top k features from that ordering" is identical to "what RFE returns if asked for k". Same answer, roughly 39x less computation.

## Step 5 — The sweep (feature counts 1 to 39)
For every feature count `k` from 1 up to the total:
- take the top `k` features from the ordering,
- score them with 5-fold stratified cross-validation,
- record the mean **macro F1**.

- *why macro F1 as the signal:* macro F1 averages the two classes **equally**. Accuracy cannot be used here — a model that labels every single flow as "attack" scores about 97.7% accuracy while catching zero benign traffic. Macro F1 refuses to hide that, because the benign class counts just as much as the attack class in the average.
- *why 5-fold stratified CV:* same validation setup as the baselines, so the numbers sit on the same footing. Stratified keeps the benign ratio steady inside every fold.
- *why the loop reads the count from the data:* `total_features = X.shape[1]` is not hardcoded to 39. The same script will sweep 1 to 84 on the IoT-DIAD flow features without editing anything.

## Step 6 — Automatic feature count selection (the elbow)
This is the part that decides the answer. **No feature number is written anywhere in the code** — the number comes out of the results.

```python
best_score = max(macro_f1_scores)
threshold = best_score * (1 - tolerance)
# then: the first (smallest) k whose score reaches the threshold wins
```

In plain language:
1. Look at every score in the sweep and find the **best** one.
2. Draw a line 1% below that best score. This is the "close enough" line.
3. Walk up from 1 feature and stop at the **first** count that reaches the line.

The result is the **smallest feature set that is still essentially as good as the best one found**. Extra features that only buy a fraction of a percent are not worth keeping.

- *why "smallest that clears the line" rather than "the highest score":* the highest score is often reached with nearly all features, and the last few features usually add almost nothing. Taking the smallest set within tolerance is what makes this a **reduction** result instead of just a ranking.
- *why tolerance = 0.01:* 1% of macro F1 is a small enough drop to be an acceptable trade for a much smaller feature set.
- **Note:** the threshold is *relative* — 1% of the best score, not a flat 0.01 subtracted from it.
- **Note:** the `chosen_count = total_features` line before the loop is a fallback that can never actually trigger, because the best score always clears its own threshold. It is left in as a safety net.

## Step 7 — Outputs
- **`rfe_sweep_2023.csv`** — every (feature count, macro F1) pair from the sweep.
    - *why save it:* the graphs can be redrawn and the elbow recalculated later without re-running the whole sweep. It is also the raw evidence behind the reported result.
- **Graph 1 — `rfe_macro_f1_vs_features_2023.png`:** macro F1 against number of features, with a dashed line at the tolerance threshold and a dotted line at the chosen count. Answers **how many features**.
- **Graph 2 — `rfe_chosen_importances_2023.png`:** a horizontal bar chart of the surviving features' importances, from a forest retrained on just those features. Answers **which features**.

---

## Design choices, summarised

| Choice | Value | Reason |
|---|---|---|
| Estimator | Random Forest (baseline config) | won the baseline comparison; keeping it identical isolates the feature effect |
| Degradation signal | macro F1 | treats the rare benign class equally; accuracy would hide total benign failure |
| Sample size | 300,000 | RFE refits many times; 1,000,000 (baseline size) would be unnecessarily slow |
| Tolerance | 0.01 (relative) | 1% macro F1 is an acceptable trade for a smaller feature set |
| Feature count | **automatic** | chosen by the elbow rule, never set by hand |
| Validation | 5-fold stratified CV | matches the baseline setup so results are comparable |
| Seed | 47 | same as the rest of the project, reproducible |

---

## Practical notes
- `matplotlib.use("Agg")` is set **before** `import matplotlib.pyplot`, because the backend locks in as soon as pyplot loads. "Agg" writes images straight to file instead of trying to open a window — necessary for a long unattended run.
- Run it the same way as the baselines:
```bash
cd "/Users/pelinmete/Desktop/GitHub/DNS Project"
source .venv/bin/activate
caffeinate -i python Recursive_Feature_Selection.py
```
- Expected runtime is roughly 10–20 minutes, estimated from the baseline log (Random Forest averaged 4.87s per fit on 1,000,000 rows, so about 1.5s at 300,000).

---

## Results
*(fill in after the first real run)*

- **Best macro F1 in sweep:**
- **Threshold (1% below best):**
- **Automatically chosen feature count:**
- **Macro F1 at chosen count:**
- **Chosen features:**

### Reduction summary
- Started with: 39 features
- Reduced to:
- Reduction: % of features removed
- Macro F1 change vs. full feature set:

---

## Next step
The same script, with the same tolerance and the same estimator, gets applied to the IoT-DIAD 2024 flow-based feature set (84 features). Keeping the method identical on both datasets is the whole point — it means any difference in the results comes from the **data**, not from the method.
