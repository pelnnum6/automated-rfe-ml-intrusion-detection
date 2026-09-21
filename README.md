# Automated RFE-Based Feature Selection for Machine Learning Intrusion Detection

This repository contains a research project exploring machine learning and feature selection for network intrusion detection using the **CIC-IoT-2023** and **CIC-IoT-DIAD 2024** datasets.

The project focuses on building and comparing machine learning-based intrusion detection models across two recent IoT cybersecurity datasets. The workflow includes data preprocessing, binary attack/benign classification, baseline model evaluation, and Recursive Feature Elimination (RFE) to investigate how progressively reducing the network traffic feature set affects intrusion detection performance.

A key part of the project is an **automated RFE-based feature selection approach** designed to determine an appropriate reduced feature set based on model performance, rather than requiring the final feature count to be manually selected from a performance graph.

## Datasets

### CIC-IoT-2023

-CIC-IoT-2023 is a large-scale IoT intrusion detection dataset containing approximately **46.7 million labeled traffic records** generated from a network of **105 IoT devices**. 
-It includes **33 attacks across seven attack categories**, including DDoS, DoS, Mirai, reconnaissance, spoofing, brute-force, and web-based attacks, alongside benign traffic. 
-The dataset provides network traffic features describing packet, protocol, timing, and flow behavior and is characterized by significant class imbalance. 
In this project, CIC-IoT-2023 is used for binary benign/attack classification and evaluation of the automated RFE-based feature-selection approach.

### CIC-IoT-DIAD 2024

-CIC-IoT-DIAD 2024 is a newer IoT device identification and anomaly detection dataset generated using **105 IoT devices** and the same broad set of **33 cyberattacks**. -This project uses its **flow-based anomaly detection data**, containing **84 fields** describing flow duration, packet statistics, inter-arrival times, TCP flags, and other network-flow characteristics. The downloaded flow-based dataset used in this project is approximately **9.7 GB**, consisting of **126 CSV files and approximately 19.5 million records**. 
-It is used to evaluate the same baseline models and automated RFE-based feature-selection approach on a newer IoT intrusion detection dataset.

> Due to their size, the original datasets are not stored in this repository.

## Methodology

The project follows the general pipeline:

**Data Cleaning → Label Encoding → Baseline Classification → Recursive Feature Elimination (RFE) → Automated Feature Selection → Model Evaluation**

Initial experiments use binary classification:

- `0` — Benign traffic
- `1` — Attack traffic

Baseline experiments use machine learning classifiers:

- Decision Tree
- Random Forest
- XGBoost

Baseline performance is first established using the complete feature set. **Recursive Feature Elimination (RFE)** is then used to progressively reduce the number of network traffic features and evaluate model performance at different feature-set sizes.

Rather than manually examining the resulting performance graph and selecting a feature count, the project implements an **automated selection approach** that uses the model's performance across the RFE process to determine an appropriate reduced feature subset.

This allows the feature-selection process to be applied more consistently across experiments without relying on manual interpretation of each performance graph.

The reduced models are then compared with the full-feature baseline models using metrics including:

- Accuracy
- Precision
- Recall
- F1-score

Given the class imbalance present in both datasets, model performance is evaluated primarily using **F1-score**, alongside accuracy, precision, and recall.

## Research Goal

The goal of this project is to determine how effectively network traffic features can be reduced while preserving machine learning-based intrusion detection performance across two large-scale IoT datasets.

The research focuses on developing a consistent, automated method for identifying a compact feature set without manually choosing a stopping point. 
By applying the same feature-selection framework to CIC-IoT-2023 and CIC-IoT-DIAD 2024, the project also examines how feature redundancy and reduction differ across datasets with different feature spaces.

## Technologies

- Python
- pandas
- NumPy
- scikit-learn
- XGBoost
- Matplotlib

## Results

The automated RFE approach substantially reduced the feature space in both datasets while maintaining strong classification performance.

- **CIC-IoT-2023:** RFE automatically selected **17 of 39 features**, reducing the feature set by **56.4%**. The selected subset achieved a **Macro F1 of 0.9038**, retaining approximately **99.4% of the best performance observed during the RFE sweep**.
  
- **CIC-IoT-DIAD 2024:** RFE automatically selected **15 of 79 modeling features**, reducing the feature set by **81.0%**. The selected subset achieved a **Macro F1 of 0.7864**, retaining approximately **99.4% of the best RFE sweep performance**.

For both datasets, **Random Forest** produced the strongest baseline Macro F1 and was therefore used as the estimator for RFE. CIC-IoT-2023 achieved a final baseline test Macro F1 of **0.9128**, while the CIC-IoT-DIAD 2024 Random Forest baseline achieved a cross-validation Macro F1 of **0.8115**. 

Overall, the results show that the automated RFE approach was able to remove a substantial portion of the original feature space while preserving most of the observed classification performance, without manually selecting the feature count from a performance graph.

## Status
Completed.

## Author

**Pelin Mete**  
Bachelor of Computing (Honours) — Cybersecurity  
Queen's University

