import pandas as pd
import numpy as np
import os
#importing classifiers
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier # to work in macOS it requires `brew install libomp`
from sklearn.preprocessing import LabelEncoder # switch to text labels to numerical labels for better training.
from sklearn.metrics import classification_report, confusion_matrix # this is for testing on the test set after cross-validation. It gives us precision, recall and f1 score for each class.


our_random_state = 47 # the randomization set.
sample_size = 1000000 # set to reduce the dataset size to 1 million rows for faster training and testing. 

#the paths were gonna use
file_path = "data/scaled_data/CIC-IoT-2023/train.csv"
test_path = "data/scaled_data/CIC-IoT-2023/test.csv"

data= pd.read_csv(file_path) #using pandas to read csv file, stores it in dataframe data.
print("Dataset shape:", data.shape)
print("Columns:", data.columns.tolist())
os.makedirs("data/baseline_results", exist_ok=True)

label_column = "Label"  # Replace with the actual label column name to label_column. 
X = data.drop(columns=[label_column]) #creating feature set X by dropping the label column from the dataframe.
y = data[label_column]  #separating the label column from the dataframe to create the target variable y.

"""This part encodes the labels if they are of object type. It uses LabelEncoder from sklearn to convert categorical labels into numerical format, which is necessary for many machine learning algorithms that require numerical input. 
After encoding, it prints out the mapping of original class names to their corresponding encoded numerical values."""

if y.dtype == "object": #checking if the target variable is of object type meaning it contains text instead of numerical vals.
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y) #converts text to nums.

print(y.value_counts()) #class balance check. should be about 2.3% benign.

#this section is for subsampling the dataset to a smaller size for faster training and testing. It randomly samples a fraction of the dataset based on the specified sample_size while maintaining the class distribution using stratified sampling for 4.4M rows.
if sample_size is not None and len(X) > sample_size:
    fraction = sample_size / len(X)
    sample_index = y.groupby(y).sample(frac=fraction, random_state=our_random_state).index # this index is calculated by grouping the target variable y by its classes and then sampling a fraction of each class based on the specified sample_size. This ensures that the class distribution is maintained in the subsampled dataset.
    X = X.loc[sample_index]
    y = y.loc[sample_index]

    #these verification for the subsampling process. It prints out the shape of the subsampled feature set X and the class distribution of the target variable y after subsampling.
    print("Subsampled to:", X.shape)
    print(y.value_counts())


# this section is for calculating the scale_pos_weight parameter for XGBoost. 
#scale_pos_weight = the ratio of negative(0) samples to positive(1) samples
scale_pos_weight = (y == 0).sum() / (y == 1).sum()
print("scale_pos_weight for XGBoost:", scale_pos_weight)


#Models 
models={
    "Decision Tree": DecisionTreeClassifier(random_state=47,class_weight="balanced"), #random state is set to 47 it implies the "recipe" of random generator making the results reproducible. class_weight is set to "balanced" to handle class imbalance by adjusting weights inversely proportional to class frequencies.
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=47, class_weight="balanced", n_jobs=-1), # n_estimators is set to 100 it implies that the model will build 100 decision trees. n_jobs=-1 means that all available CPU cores will be used for training which is for speeding up.
    "XGBoost": XGBClassifier(n_estimators=100,random_state=47,eval_metric="logloss" ,scale_pos_weight=scale_pos_weight, n_jobs=-1) # n_estimators is set to 100 is the number of boosting rounds. eval_metric is set to "logloss" which is the evaluation metric for binary classification.
}

#Cross-validation setup
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=47) #this built in function is used to split the dataset into 5 sections. shuffle is set to True to randomize the data before splitting.


#Metrics to evaluate
metrics={
    "accuracy" : "accuracy",
    "precision_weighted" : "precision_weighted",
    "recall_weighted" : "recall_weighted",
    "f1_weighted" : "f1_weighted",
    "f1_macro" : "f1_macro",
    "precision_macro" : "precision_macro",
    "recall_macro" : "recall_macro",
}

results=[] #an empty list to store the results of the cross-validation for each model.
for model_name, model in models.items(): # this loop iterates over each model in the models dictionary 
    print(f"\nTesting {model_name}...")
    scores = cross_validate(model, X, y, cv=cv, scoring=metrics, n_jobs=1) #cross_validate function is used to evaluate the model using cross-validation. It takes the model, features X, target y, cross-validation strategy cv, and scoring metrics as inputs.
    result = { # this dictionary stores the results of the cross-validation for the current model. 
        "Model": model_name,
        "Accuracy": scores["test_accuracy"].mean(),
        "Weighted Precision": scores["test_precision_weighted"].mean(),
        "Weighted Recall": scores["test_recall_weighted"].mean(),
        "Weighted F1": scores["test_f1_weighted"].mean(),
        "Macro F1": scores["test_f1_macro"].mean(),
        "Average Training Time": scores["fit_time"].mean(),
        "Macro Precision": scores["test_precision_macro"].mean(),
        "Macro Recall": scores["test_recall_macro"].mean(),
    }
    results.append(result)

results_df = pd.DataFrame(results) #turns the results list into a dataframe for better visualization and analysis.
print("\nCross-validation results:")
print(results_df)

#This part of the code saves the results into a new csv file named "baseline_model_results_2023.csv" 
results_df.to_csv("data/baseline_results/baseline_model_results_2023.csv", index=False)
print("\nResults saved to 'baseline_model_results_2023.csv'.")





"""This section is for the test set evaluation. 
Why we do this is because the cross-validation results are based on the training data, and we want to see how well the best model performs on (unseen) test data.
"""

best_model_name = results_df.loc[results_df["Macro F1"].idxmax(), "Model"] #the model with the best macro F1 wins idcmax is used to find the index of the maximum value in the "Macro F1" column, and then the corresponding model name is retrieved from the "Model" column.
print("\nBest model by Macro F1:", best_model_name)
 
test_data = pd.read_csv(test_path)
X_test = test_data.drop(columns=[label_column])
y_test = test_data[label_column]
print("Test shape:", X_test.shape)
 
best_model = models[best_model_name] #grabs the best model from the models dict to train it on the training data and evaluate it on the test data.
best_model.fit(X, y) #train the winner on the training data
y_pred = best_model.predict(X_test) #predict on the untouched test data
 
print("\nClassification report:")
print(classification_report(y_test, y_pred, target_names=["Benign (0)", "Attack (1)"], digits=4)) #per class precision, recall and f1. benign recall is the important one, (1-benign recall) is the false alarm rate meaning wrongly flagged as attack.
 
cm = confusion_matrix(y_test, y_pred) # this is the confusion matrix: TP TN FP FN.
print("Confusion matrix:")
print(cm)
 
#reading the confusion matrix: rows are the true class, columns are the predicted class.
true_negative, false_positive = cm[0][0], cm[0][1] #benign rows: correctly called benign, wrongly flagged as attack
false_negative, true_positive = cm[1][0], cm[1][1] #attack rows: missed attacks, caught attacks
 
false_alarm_rate = false_positive / (false_positive + true_negative) #proportion of benign traffic wrongly flagged as an attack
detection_rate = true_positive / (true_positive + false_negative) #proportion of attacks that were caught, this is the recall of the attack class
print("False alarm rate:", false_alarm_rate)
print("Detection rate:", detection_rate)
print("Missed attacks:", false_negative, " Wrongly flagged benign flows:", false_positive)



