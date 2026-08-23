# OUTPUT:

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