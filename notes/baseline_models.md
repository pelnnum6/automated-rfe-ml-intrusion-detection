The results terminal after baseline_models_2023 run in 16/07/2026:

(.venv) pelinmete@Pelins-MacBook-Air DNS Project % cd "/Users/pelinmete/Desktop/GitHub/DNS Project"
source .venv/bin/activate
caffeinate -i python baseline_models_2023.py
Dataset shape: (4385910, 40)
Columns: ['Header_Length', 'Protocol Type', 'Time_To_Live', 'Rate', 'fin_flag_number', 'syn_flag_number', 'rst_flag_number', 'psh_flag_number', 'ack_flag_number', 'ece_flag_number', 'cwr_flag_number', 'ack_count', 'syn_count', 'fin_count', 'rst_count', 'HTTP', 'HTTPS', 'DNS', 'Telnet', 'SMTP', 'SSH', 'IRC', 'TCP', 'UDP', 'DHCP', 'ARP', 'ICMP', 'IGMP', 'IPv', 'LLC', 'Tot sum', 'Min', 'Max', 'AVG', 'Std', 'Tot size', 'IAT', 'Number', 'Variance', 'Label']
Label
1    4283485
0     102425
Name: count, dtype: int64
Subsampled to: (1000000, 39)
Label
1    976647
0     23353
Name: count, dtype: int64
scale_pos_weight for XGBoost: 0.023911402994121724

Testing Decision Tree...

Testing Random Forest...

Testing XGBoost...

Cross-validation results:
           Model  Accuracy  Weighted Precision  ...  Average Training Time  Macro Precision  Macro Recall
0  Decision Tree  0.989226            0.989112  ...               1.152482         0.884876      0.876428
1  Random Forest  0.990978            0.992461  ...               4.869272         0.871837      0.962320
2        XGBoost  0.985730            0.991073  ...               1.318901         0.810588      0.991002

[3 rows x 9 columns]

Results saved to 'baseline_model_results_2023.csv'.

Best model by Macro F1: Random Forest
Test shape: (1879676, 39)

Classification report:
              precision    recall  f1-score   support

  Benign (0)     0.7481    0.9322    0.8301     43896
  Attack (1)     0.9984    0.9925    0.9954   1835780

    accuracy                         0.9911   1879676
   macro avg     0.8733    0.9623    0.9128   1879676
weighted avg     0.9925    0.9911    0.9916   1879676

Confusion matrix:
[[  40920    2976]
 [  13776 1822004]]
False alarm rate: 0.06779661016949153
Detection rate: 0.9924958328339997
Missed attacks: 13776  Wrongly flagged benign flows: 2976
(.venv) pelinmete@Pelins-MacBook-Air DNS Project % 
