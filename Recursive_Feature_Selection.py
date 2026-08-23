import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use("Agg") # non-interactive backend, saves straight to file instead of trying to open a window.
import matplotlib.pyplot as plt
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

our_random_state = 47
sample_size = 300000 # this is the sample size for the feature selection process. The reason for sampling is that the dataset is too large to run RFE on the whole dataset in a reasonable time frame. The sample size is chosen to be large enough to be representative of the whole dataset, but small enough to run in a reasonable time frame. The sample size can be adjusted based on the available computational resources and time constraints.
tolerance = 0.01  # %1 tolerance meaning if the accuracy of the model does not improve by more than 1% after removing a feature, we stop the feature selection process.

train_path = "data/scaled_data/CIC-IoT-2023/train.csv" 
results_dir = "data/feature_selection_results"   

def recursive_feature_selection_2023():
    os.makedirs(results_dir, exist_ok=True) # to_csv and savefig cannot create folders themselves.
    data = pd.read_csv(train_path) # read the scaled training set, only ever sees training data, so there is no leakage.
    print("Training set shape:", data.shape)
 
    label_column = "Label"
    X = data.drop(columns=[label_column]) # features
    y = data[label_column]                # target, already 0/1 from the binary encoding step.
 
    # stratified subsample down to sample_size. groupby(y).sample keeps the benign/attack ratio the same (only ~2.34% benign),
    # which matters a lot here because benign is the rare class and we do not want to lose it in the subsample.
    if sample_size is not None and len(X) > sample_size:
        fraction = sample_size / len(X)
        sample_index = y.groupby(y).sample(frac=fraction, random_state=our_random_state).index
        X = X.loc[sample_index]
        y = y.loc[sample_index]
        print("Subsampled to:", X.shape)
        print(y.value_counts())
 
    total_features = X.shape[1] # 39 for this dataset. the sweep runs from 1 feature up to this number.
    print("Total number of features:", total_features)
 
    # this is the model used BOTH inside RFE (to rank features) and to score each subset.
    # it is the exact config that won the baselines, so any change in performance is due to the features, not a different model.
    random_forest = RandomForestClassifier(n_estimators=100, random_state=our_random_state, class_weight="balanced", n_jobs=-1)
 
    # run RFE ONCE down to a single feature. this gives the full elimination order in ranker.ranking_.
    # why once instead of 39 times: RFE removes one feature at a time by importance, so the order it removes them in
    # is the same no matter where you stop. so "the top k features by this ranking" is identical to "what RFE keeps if asked for k".
    # running it once gives the same result as 39 separate RFE runs, just far faster.
    print("\nRunning RFE once to build the full feature ranking...")
    ranker = RFE(estimator=random_forest, n_features_to_select=1)
    ranker.fit(X, y)
 
    # ranking_ gives each feature a rank: rank 1 is the last feature standing (most important),
    # bigger numbers were eliminated earlier. sorting by rank gives the order features are added back into the sweep.
    ranking = ranker.ranking_
    feature_names = X.columns.tolist()
 
    # build the feature order, best first. plain loop, no generator expressions.
    order = np.argsort(ranking) # indices of features sorted from rank 1 upward (most important first)
    ordered_features = []
    for index in order:
        ordered_features.append(feature_names[index])
    print("Feature order (most to least important):")
    print(ordered_features)
 
    # cross-validation setup, same as the baselines: 5-fold stratified, shuffled, macro F1 as the score.
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=our_random_state)
 
    # the explicit sweep: for every feature count k from 1 to total_features, score the top-k features with cross-validation.
    feature_counts = []
    macro_f1_scores = []
    for k in range(1, total_features + 1):
        selected_features = ordered_features[:k] # the k most important features
        scores = cross_val_score(random_forest, X[selected_features], y, cv=cv, scoring="f1_macro", n_jobs=1)
        mean_score = scores.mean()
        feature_counts.append(k)
        macro_f1_scores.append(mean_score)
        print(f"Features: {k}  Macro F1: {round(mean_score, 4)}") # simple print, no fancy formatting.
 
    # AUTOMATED elbow selection. there is no manual feature number anywhere below.
    # best_score is the highest macro F1 reached in the whole sweep.
    # threshold is 1% below that. the winner is the SMALLEST feature count that still reaches the threshold.
    best_score = max(macro_f1_scores)
    threshold = best_score * (1 - tolerance) # relative 1%. for an absolute 0.01 cut instead, use: threshold = best_score - tolerance
 
    chosen_count = total_features # fallback: if nothing clears the threshold below the best, keep the full set.
    for i in range(len(feature_counts)):
        if macro_f1_scores[i] >= threshold:
            chosen_count = feature_counts[i]
            break # the first (smallest) k that clears the threshold is the elbow, so we stop here.
 
    chosen_features = ordered_features[:chosen_count]
    chosen_score = macro_f1_scores[chosen_count - 1] # -1 because the list is 0-indexed but counts start at 1.
 
    print("\nBest macro F1 in the sweep:", round(best_score, 4))
    print("Threshold (within 1% of best):", round(threshold, 4))
    print("Automatically chosen feature count:", chosen_count)
    print("Chosen macro F1:", round(chosen_score, 4))
    print("Chosen features:")
    print(chosen_features)
 
    # save the per-count results so the numbers behind the graphs are reproducible.
    results_table = pd.DataFrame()
    results_table["num_features"] = feature_counts
    results_table["macro_f1"] = macro_f1_scores
    results_table.to_csv(os.path.join(results_dir, "rfe_sweep_2023.csv"), index=False)
    print("\nSaved sweep table to rfe_sweep_2023.csv")
 
    # GRAPH 1: macro F1 versus number of features, with the 1% threshold and the automatically chosen elbow marked.
    plt.figure()
    plt.plot(feature_counts, macro_f1_scores, marker="o")
    plt.axhline(y=threshold, linestyle="--", label="1% tolerance threshold")
    plt.axvline(x=chosen_count, linestyle=":", label="chosen feature count")
    plt.xlabel("Number of features")
    plt.ylabel("Macro F1 (5-fold CV)")
    plt.title("RFE sweep on CIC-IoT-2023 (binary)")
    plt.legend()
    plt.savefig(os.path.join(results_dir, "rfe_macro_f1_vs_features_2023.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved graph 1: rfe_macro_f1_vs_features_2023.png")
 
    # GRAPH 2: the importances of the chosen features, so the report can show WHICH features survived selection.
    # train the same RF on just the chosen features to read off their importances.
    final_forest = RandomForestClassifier(n_estimators=100, random_state=our_random_state, class_weight="balanced", n_jobs=-1)
    final_forest.fit(X[chosen_features], y)
    importances = final_forest.feature_importances_
 
    # sort the chosen features by importance for a readable bar chart. plain loops, no generator expressions.
    importance_order = np.argsort(importances) # ascending, so the biggest bar ends up at the top of barh.
    sorted_names = []
    sorted_values = []
    for index in importance_order:
        sorted_names.append(chosen_features[index])
        sorted_values.append(importances[index])
 
    plt.figure()
    plt.barh(sorted_names, sorted_values)
    plt.xlabel("Random Forest importance")
    plt.title("Chosen feature importances - CIC-IoT-2023 (binary)")
    plt.savefig(os.path.join(results_dir, "rfe_chosen_importances_2023.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved graph 2: rfe_chosen_importances_2023.png")
 
    return chosen_features, chosen_count, chosen_score
 
 
chosen_features, chosen_count, chosen_score = recursive_feature_selection_2023()
 