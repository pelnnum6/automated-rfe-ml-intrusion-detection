# OUTPUT 2023:

(.venv) pelinmete@Mac DNS Project % caffeinate -i python Recursive_Feature_Selection.py
Matplotlib is building the font cache; this may take a moment.
Training set shape: (4385910, 40)
Subsampled to: (300000, 39)
Label
1    292994
0      7006
Name: count, dtype: int64
Total number of features: 39

Running RFE once to build the full feature ranking...
Feature order (most to least important):
['Number', 'ack_flag_number', 'HTTPS', 'AVG', 'Tot size', 'Rate', 'Header_Length', 'Tot sum', 'Time_To_Live', 'ack_count', 'IAT', 'Std', 'Max', 'psh_flag_number', 'Variance', 'TCP', 'Min', 'syn_count', 'syn_flag_number', 'UDP', 'HTTP', 'rst_count', 'LLC', 'fin_count', 'Protocol Type', 'DNS', 'rst_flag_number', 'IPv', 'ICMP', 'fin_flag_number', 'ARP', 'SSH', 'DHCP', 'IGMP', 'IRC', 'ece_flag_number', 'cwr_flag_number', 'SMTP', 'Telnet']
Features: 1  Macro F1: 0.8137
Features: 2  Macro F1: 0.8138
Features: 3  Macro F1: 0.8139
Features: 4  Macro F1: 0.8477
Features: 5  Macro F1: 0.8502
Features: 6  Macro F1: 0.8718
Features: 7  Macro F1: 0.8766
Features: 8  Macro F1: 0.877
Features: 9  Macro F1: 0.8849
Features: 10  Macro F1: 0.8853
Features: 11  Macro F1: 0.8849
Features: 12  Macro F1: 0.8887
Features: 13  Macro F1: 0.8973
Features: 14  Macro F1: 0.8985
Features: 15  Macro F1: 0.8979
Features: 16  Macro F1: 0.8982
Features: 17  Macro F1: 0.9038
Features: 18  Macro F1: 0.9051
Features: 19  Macro F1: 0.9047
Features: 20  Macro F1: 0.9045
Features: 21  Macro F1: 0.906
Features: 22  Macro F1: 0.9057
Features: 23  Macro F1: 0.9066
Features: 24  Macro F1: 0.9085
Features: 25  Macro F1: 0.9092
Features: 26  Macro F1: 0.9093
Features: 27  Macro F1: 0.909
Features: 28  Macro F1: 0.9093
Features: 29  Macro F1: 0.9094
Features: 30  Macro F1: 0.9089
Features: 31  Macro F1: 0.9095
Features: 32  Macro F1: 0.909
Features: 33  Macro F1: 0.9087
Features: 34  Macro F1: 0.9095
Features: 35  Macro F1: 0.9079
Features: 36  Macro F1: 0.9088
Features: 37  Macro F1: 0.9089
Features: 38  Macro F1: 0.9083
Features: 39  Macro F1: 0.9094

Best macro F1 in the sweep: 0.9095
Threshold (within 1% of best): 0.9004
Automatically chosen feature count: 17
Chosen macro F1: 0.9038
Chosen features:
['Number', 'ack_flag_number', 'HTTPS', 'AVG', 'Tot size', 'Rate', 'Header_Length', 'Tot sum', 'Time_To_Live', 'ack_count', 'IAT', 'Std', 'Max', 'psh_flag_number', 'Variance', 'TCP', 'Min']

Saved sweep table to rfe_sweep_2023.csv
Saved graph 1: rfe_macro_f1_vs_features_2023.png
Saved graph 2: rfe_chosen_importances_2023.png
(.venv) pelinmete@Mac DNS Project % 



# Observations:

1. Three regions. Features 1–3 flat, 4–17 climbing, 18–39 plateau. The last 22 features add 0.0056 macro F1 between them — that plateau is what justifies cutting.

2. RFE rank ≠ marginal gain. ack_flag_number and HTTPS rank 2nd/3rd but add +0.0001 each; AVG at rank 4 adds +0.0338. RFE ranks by importance in the full model; the sweep measures what a feature adds given only the ones above it.

3. Size and rate dominate. Biggest gains: AVG (+0.0338), Rate (+0.0216), Max (+0.0086) — consistent with flood-heavy traffic.

4. Extra features sometimes hurt. Score fell 11 times out of 38. Useless features aren't neutral — they give trees more columns to fit noise on.

5. The plateau is noise. Spread of 0.005, best score hit twice (31 and 34 features). Picking "31" would be reading signal into noise — this is what the 1% tolerance protects against.

6. What was cut makes sense. Removed features are mostly rare protocol flags (Telnet, SMTP, IRC, SSH, ARP); survivors are mostly flow statistics. In flood traffic "is this Telnet?" is almost always 0, so it can't separate classes. Attack vs benign here is about how much, how fast, how big — not which protocol.

7. Consistency check. Sweep at 39 features: 0.9094. Baseline test-set macro avg: 0.9128. Different measurements, within 0.004 — neither run looks wrong.

8. Binary only. Telnet may be useless here but decisive for separating attack types. Don't reuse these 17 for the category-level task.

Carrying forward to IoT-DIAD 2024
	CIC-IoT-2023	IoT-DIAD (flow)
Features available	39	84
Features chosen	17	to fill
Reduction	56.41%	to fill
Macro F1 at chosen count	0.9038	to fill
Performance retained	99.37%	to fill

Same estimator, same tolerance, same CV — so any difference comes from the data. The question: does a higher-dimensional set hold proportionally more redundancy?








### OUTPUT 2024:
Training set shape: (13601431, 80)
Subsampled to: (300000, 79)
Label
1    293852
0      6148
Name: count, dtype: int64
Total number of features: 79

Running RFE once to build the full feature ranking...
Features: 1  Macro F1: 0.5375
Features: 2  Macro F1: 0.5958
Features: 3  Macro F1: 0.6869
Features: 4  Macro F1: 0.696
Features: 5  Macro F1: 0.7344
Features: 6  Macro F1: 0.7418
Features: 7  Macro F1: 0.7446
Features: 8  Macro F1: 0.7462
Features: 9  Macro F1: 0.7538
Features: 10  Macro F1: 0.7529
Features: 11  Macro F1: 0.7587
Features: 12  Macro F1: 0.7596
Features: 13  Macro F1: 0.7781
Features: 14  Macro F1: 0.7783
Features: 15  Macro F1: 0.7864
Features: 16  Macro F1: 0.7874
Features: 17  Macro F1: 0.7855
Features: 18  Macro F1: 0.7856
Features: 19  Macro F1: 0.787
Features: 20  Macro F1: 0.7867
Features: 21  Macro F1: 0.7858
Features: 22  Macro F1: 0.7866
Features: 23  Macro F1: 0.7882
Features: 24  Macro F1: 0.7871
Features: 25  Macro F1: 0.7875
Features: 26  Macro F1: 0.789
Features: 27  Macro F1: 0.7873
Features: 28  Macro F1: 0.7873
Features: 29  Macro F1: 0.7878
Features: 30  Macro F1: 0.7866
Features: 31  Macro F1: 0.7866
Features: 32  Macro F1: 0.7867
Features: 33  Macro F1: 0.7866
Features: 34  Macro F1: 0.786
Features: 35  Macro F1: 0.7872
Features: 36  Macro F1: 0.7868
Features: 37  Macro F1: 0.7874
Features: 38  Macro F1: 0.7869
Features: 39  Macro F1: 0.7872
Features: 40  Macro F1: 0.787
Features: 41  Macro F1: 0.7881
Features: 42  Macro F1: 0.7883
Features: 43  Macro F1: 0.7875
Features: 44  Macro F1: 0.7876
Features: 45  Macro F1: 0.7886
Features: 46  Macro F1: 0.786
Features: 47  Macro F1: 0.7876
Features: 48  Macro F1: 0.7865
Features: 49  Macro F1: 0.7866
Features: 50  Macro F1: 0.7882
Features: 51  Macro F1: 0.7864
Features: 52  Macro F1: 0.788
Features: 53  Macro F1: 0.7887
Features: 54  Macro F1: 0.7908
Features: 55  Macro F1: 0.7893
Features: 56  Macro F1: 0.7875
Features: 57  Macro F1: 0.7894
Features: 58  Macro F1: 0.7887
Features: 59  Macro F1: 0.7911
Features: 60  Macro F1: 0.7885
Features: 61  Macro F1: 0.7902
Features: 62  Macro F1: 0.7892
Features: 63  Macro F1: 0.7895
Features: 64  Macro F1: 0.7904
Features: 65  Macro F1: 0.7895
Features: 66  Macro F1: 0.7896
Features: 67  Macro F1: 0.7898
Features: 68  Macro F1: 0.7889
Features: 69  Macro F1: 0.791
Features: 70  Macro F1: 0.7894
Features: 71  Macro F1: 0.79
Features: 72  Macro F1: 0.7896
Features: 73  Macro F1: 0.7907
Features: 74  Macro F1: 0.7905
Features: 75  Macro F1: 0.7896
Features: 76  Macro F1: 0.791
Features: 77  Macro F1: 0.79
Features: 78  Macro F1: 0.7897
Features: 79  Macro F1: 0.79

Feature order (most to least important):
['Flow IAT Min', 'Flow IAT Max', 'Packet Length Variance', 'Packet Length Std', 'Fwd Segment Size Avg', 'Total Length of Bwd Packet', 'Flow IAT Mean', 'Total Length of Fwd Packet', 'Fwd IAT Min', 'Average Packet Size', 'FWD Init Win Bytes', 'Bwd Segment Size Avg', 'Src Port', 'Packet Length Max', 'Dst Port', 'RST Flag Count', 'Idle Std', 'Fwd Packet Length Mean', 'Flow Duration', 'Bwd Packet Length Max', 'Fwd Packet Length Max', 'Fwd Header Length', 'Fwd IAT Std', 'Flow IAT Std', 'Packet Length Mean', 'Idle Max', 'Bwd Packets/s', 'Fwd IAT Max', 'ACK Flag Count', 'Idle Mean', 'Bwd Packet Length Mean', 'SYN Flag Count', 'Fwd IAT Mean', 'Idle Min', 'Fwd Packets/s', 'Fwd Seg Size Min', 'Fwd Packet Length Min', 'Flow Packets/s', 'Fwd IAT Total', 'Fwd Act Data Pkts', 'Flow Bytes/s', 'Total Fwd Packet', 'Packet Length Min', 'Bwd Header Length', 'Protocol', 'Bwd Packet Length Min', 'Fwd Packet Length Std', 'Bwd IAT Total', 'Subflow Fwd Bytes', 'Bwd IAT Max', 'Total Bwd packets', 'Bwd Init Win Bytes', 'Bwd IAT Mean', 'Active Mean', 'Bwd IAT Std', 'Subflow Fwd Packets', 'Bwd IAT Min', 'Active Min', 'Bwd Bytes/Bulk Avg', 'Active Max', 'PSH Flag Count', 'Subflow Bwd Bytes', 'Subflow Bwd Packets', 'Bwd Packet/Bulk Avg', 'FIN Flag Count', 'Bwd Packet Length Std', 'Down/Up Ratio', 'Bwd Bulk Rate Avg', 'Active Std', 'CWR Flag Count', 'ECE Flag Count', 'Fwd PSH Flags', 'Fwd Bulk Rate Avg', 'Fwd Packet/Bulk Avg', 'Fwd Bytes/Bulk Avg', 'URG Flag Count', 'Bwd URG Flags', 'Fwd URG Flags', 'Bwd PSH Flags']

Best macro F1 in the sweep: 0.7911
Threshold (within 1% of best): 0.7832
Automatically chosen feature count: 15
Chosen macro F1: 0.7864

Chosen features:
['Flow IAT Min', 'Flow IAT Max', 'Packet Length Variance', 'Packet Length Std', 'Fwd Segment Size Avg', 'Total Length of Bwd Packet', 'Flow IAT Mean', 'Total Length of Fwd Packet', 'Fwd IAT Min', 'Average Packet Size', 'FWD Init Win Bytes', 'Bwd Segment Size Avg', 'Src Port', 'Packet Length Max', 'Dst Port']
(.venv) pelinmete@Pelins-MacBook-Air DNS Project % 


# Observations:

1. Three regions. Features 1–5 rise sharply, 6–15 continue improving, and 15–79 form a plateau. Adding the final 64 features increases Macro F1 by only 0.0036, which supports reducing the model to 15 features.

2. RFE rank ≠ marginal gain. `Flow IAT Max` adds +0.0583 and `Packet Length Variance` adds +0.0911, while some later highly ranked features add very little or temporarily reduce performance. RFE determines an elimination-based ranking; the sweep measures the performance obtained from each accumulated subset.

3. Timing and packet-size statistics dominate. The selected features mainly measure inter-arrival times, packet-length distributions, traffic volume, segment size, and window size. This suggests that attack and benign flows differ mainly in their timing and traffic-shape behaviour.

4. The largest gains occur early. The biggest improvements are produced by `Packet Length Variance` (+0.0911), `Flow IAT Max` (+0.0583), `Fwd Segment Size Avg` (+0.0384), and `Src Port` (+0.0185 at feature 13). Most useful information is therefore captured before the plateau.

5. Extra features frequently hurt. Macro F1 decreased 29 times across the 78 feature additions and remained unchanged twice. Additional features are not automatically helpful because they can introduce redundant information or give the Random Forest more opportunities to fit sample-specific noise.

6. The plateau is narrow and noisy. From 15 through 79 features, scores remain within a range of approximately 0.0056. The best score occurs at 59 features, but nearby counts repeatedly rise and fall by very small amounts. Choosing exactly 59 would treat minor cross-validation variation as a meaningful improvement; the 1% tolerance prevents that.

7. The reduction is substantial. RFE selected 15 of the 79 model features, removing 64 features, or 81.01%. The selected subset retains approximately 99.41% of the best RFE sweep performance.

8. Port features survived. `Src Port` and `Dst Port` were selected alongside statistical flow features. They may contain useful attack-pattern information in this dataset, but ports can also be specific to the collection environment. Their generalization should therefore be examined during final test evaluation and discussed as a limitation.

9. The baseline and RFE scores use different samples. The baseline Random Forest produced 0.8115 Macro F1 using a stratified 1,000,000-row sample, while the 79-feature RFE sweep produced 0.7900 using a stratified 300,000-row sample. This difference does not indicate an error because the measurements were produced from different training samples. The valid feature-selection comparison is between subsets within the same RFE sweep.

10. Binary only. These 15 features were selected for benign-versus-attack classification. Features removed here may still be important for distinguishing individual attack categories, so this subset should not automatically be reused for an 8-class or full multiclass experiment.

## **CIC-IoT-2023 vs. CIC-IoT-DIAD-2024**

| Measurement | CIC-IoT-2023 | CIC-IoT-DIAD-2024 |
|---|---:|---:|
| Raw dataset columns | 40 | 84 |
| Features evaluated by RFE | 39 | 79 |
| Features selected | 17 | 15 |
| Features removed | 22 | 64 |
| Feature reduction | 56.41% | 81.01% |
| Best RFE Macro F1 | 0.9095 | 0.7911 |
| Macro F1 at chosen count | 0.9038 | 0.7864 |
| Performance retained | 99.37% | 99.41% |

The 2024 flow dataset contains more than twice as many candidate model features as the 2023 dataset but requires two fewer features after RFE. It therefore exhibits substantially greater proportional redundancy: 81.01% of its model features can be removed while retaining 99.41% of the best sweep performance.

Both experiments use the same Random Forest estimator, 300,000-row stratified sample size, five-fold stratified cross-validation, random state 47, Macro F1 metric, and relative 1% tolerance. This makes the feature-reduction comparison consistent, although the absolute Macro F1 scores also reflect differences in dataset composition, feature definitions, and class distributions.





### From rfe_final_evaluation.py FINAL OBSERVATIONS:

## **Evaluation setup**

- **Model:** Random Forest

- **Training sample:** 300,000 stratified training rows from each dataset

- **Random state:** 47

- **Class weighting:** `balanced`

- **Number of trees:** 100

- **CIC-IoT-2023 features:** the 17 features selected by its RFE experiment

- **CIC-IoT-DIAD-2024 features:** the 15 features selected by its RFE experiment

- **Test procedure:** each model was fully trained before its corresponding test file was opened.

- **Leakage prevention:** the test sets were not used for feature ranking, feature-count selection, model fitting, scaling, or hyperparameter tuning.

- **Important:** the final test results are reported without changing the selected features or model configuration afterward.

## **Final comparison**

| Dataset | Training sample | Selected features | Test rows | Accuracy | Macro F1 | False-alarm rate | Detection rate | Missed attacks | Wrongly flagged benign |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CIC-IoT-2023 | 300,000 | 17 | 1,879,676 | 0.9902 | 0.9052 | 7.10% | 99.16% | 15,351 | 3,115 |
| CIC-IoT-DIAD-2024 | 300,000 | 15 | 5,829,185 | 0.9796 | 0.7929 | 26.68% | 98.48% | 86,759 | 31,874 |

## **CIC-IoT-2023 final results**

Selected features: 17
Training sample rows: 300,000
Test rows: 1,879,676
Accuracy: 0.9901759665
Macro F1: 0.9051727015

              precision    recall  f1-score   support

  Benign (0)     0.7265    0.9290    0.8154     43,896
  Attack (1)     0.9983    0.9916    0.9950  1,835,780

    accuracy                         0.9902  1,879,676
   macro avg     0.8624    0.9603    0.9052  1,879,676
weighted avg     0.9919    0.9902    0.9908  1,879,676

Confusion matrix:

[[  40,781    3,115]
 [  15,351 1,820,429]]

False-alarm rate: 0.0709631857
Detection rate: 0.9916378869
Missed attacks: 15,351
Wrongly flagged benign flows: 3,115



Selected features: 15
Training sample rows: 300,000
Test rows: 5,829,185
Accuracy: 0.9796484414
Macro F1: 0.7928898647

              precision    recall  f1-score   support

  Benign (0)     0.5024    0.7332    0.5962    119,460
  Attack (1)     0.9944    0.9848    0.9896  5,709,725

    accuracy                         0.9796  5,829,185
   macro avg     0.7484    0.8590    0.7929  5,829,185
weighted avg     0.9843    0.9796    0.9815  5,829,185

Confusion matrix:

[[   87,586    31,874]
 [   86,759 5,622,966]]

False-alarm rate: 0.2668173447
Detection rate: 0.9848050475
Missed attacks: 86,759
Wrongly flagged benign flows: 31,874



## Final Observations

1. The final test results closely match the training-only RFE cross-validation results. CIC-IoT-2023 increased from 0.9038 RFE Macro F1 to 0.9052 test Macro F1, a difference of approximately +0.0014. CIC-IoT-DIAD-2024 increased from 0.7864 to 0.7929, a difference of approximately +0.0065. This supports that both selected subsets generalize beyond their RFE validation folds.

2. CIC-IoT-2023 produced stronger balanced classification. Its final Macro F1 was 0.9052, compared with 0.7929 for CIC-IoT-DIAD-2024. The difference between the datasets was approximately 0.1123 Macro F1.

3. Both selected-feature models maintained strong attack detection. CIC-IoT-2023 detected 99.16% of attacks, while CIC-IoT-DIAD-2024 detected 98.48%. Feature reduction therefore preserved high attack recall in both datasets.

4. Benign recognition is the main weakness of the 2024 model. Its benign recall was 0.7332, meaning approximately 26.68% of benign flows were incorrectly classified as attacks. The 2023 model achieved 0.9290 benign recall and a much lower false-alarm rate of 7.10%.

5. Accuracy hides the benign-class weakness. The 2024 model achieved 97.96% accuracy despite a 26.68% false-alarm rate because attacks represent the overwhelming majority of its test set. Macro F1 and the class-specific measurements therefore provide a more informative evaluation than accuracy alone.

6. The 2024 dataset contains proportionally more feature redundancy. CIC-IoT-2023 was reduced from 39 to 17 features, removing 56.41%. CIC-IoT-DIAD-2024 was reduced from 79 to 15 features, removing 81.01%.

7. The 2024 model used fewer features but faced a more difficult classification problem. Its 15-feature subset retained 99.41% of the best RFE sweep performance, but its final benign F1 was only 0.5962. High performance retention within an RFE sweep does not necessarily mean that the dataset itself is easy to classify.

8. The selected 2023 model missed 15,351 attacks and incorrectly flagged 3,115 benign flows. The selected 2024 model missed 86,759 attacks and incorrectly flagged 31,874 benign flows. Raw error counts are influenced by the different test-set sizes, so rates should be used for the main comparison.

9. CIC-IoT-DIAD-2024 has a test set approximately 3.10 times larger than CIC-IoT-2023. Its larger raw number of errors should not be interpreted independently of its false-alarm and detection rates.

10. The experiment supports the higher-dimensional redundancy hypothesis. The 2024 flow dataset began with more than twice as many model features as 2023 but required two fewer selected features while retaining a similar proportion of its maximum RFE performance.

11. The selected subsets are specific to binary benign-versus-attack classification. Features removed by binary RFE may still be important for separating individual attack categories, so these subsets should not automatically be reused for category-level or full multiclass classification.

# Final conclusion

Under the same Random Forest configuration, stratified 300,000-row training sample, and RFE selection rule, CIC-IoT-DIAD-2024 showed substantially greater feature redundancy than CIC-IoT-2023. The 2024 feature space was reduced by 81.01%, compared with 56.41% for 2023, while both subsets retained more than 99% of their respective best RFE sweep performance.

However, greater dimensionality reduction did not produce stronger classification. CIC-IoT-2023 achieved a final test Macro F1 of 0.9052, while CIC-IoT-DIAD-2024 achieved 0.7929. The primary difference was benign classification: the 2024 model generated a 26.68% false-alarm rate compared with 7.10% for 2023.

The results indicate that CIC-IoT-DIAD-2024 contains proportionally more redundant flow features but presents a more difficult binary classification problem, particularly when distinguishing benign traffic from attacks.