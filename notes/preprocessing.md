# CIC-IoT-2023 Preprocessing Notes

## Data info
- **Files used:** all 63 `Merged*.csv` files
    - *why:* the dataset authors (UNB) provide these merged files as the ML-ready version. the per-capture files (e.g. `DDoS-UDP_Flood7.pcap.csv`) are the same traffic before merging, so using both would duplicate flows and leak near-identical rows across train/test.
- **Total rows after combining:** 6,265,586
- **Num columns:** 40 (39 features + Label)

## Step 1 — Cleaning
*ML models cannot train properly with empty / missing / corrupted entries.*
- Replaced infinity values with NaN (`df.replace([np.inf, -np.inf], np.nan)`)
    - *why:* some flow features (like Rate) can come out as infinity when a duration is near zero. infinity breaks scaling and most classifiers.
- Removed NaN rows with `dropna()`
    - *why:* `dropna()` deletes any row with a missing value so only complete rows remain.
- Stripped column names with `df.columns.str.strip()`
    - *why:* some columns had leading spaces (" Label"), which made the label column impossible to reference consistently.
- (identify which rows were removed with `nan_rows = df[df.isnull().any(axis=1)]`)

## Step 2 — Label encoding (binary)
- Mapped labels to 0 = benign, 1 = attack, using `startswith('BENIGN')` after `.strip().upper()`
    - *why:* in CIC-IoT-2023 the benign rows are labelled **`BenignTraffic`**, not `BENIGN`. A plain `== 'BENIGN'` check never matched, so every row was wrongly encoded as an attack. `startswith('BENIGN')` + uppercasing matches both spellings.
- All 34 raw classes (33 attack types + benign) collapse to two classes.
    - *why:* this is the binary stage — attack vs benign. the category-level (8-class) and full (34-class) versions are follow-ups.
- Checked with `value_counts()` before and after encoding.
    - *why:* this is the safety check. if only one class shows up after encoding, the mapping is wrong and training should stop.

## Step 3 — Combine
- Concatenated all encoded files into one DataFrame with `pd.concat(frames, ignore_index=True)`
    - *why:* the split and the scaler must operate on the whole dataset at once. combining first means one consistent scaler across all files instead of one per file (which would make the same feature value mean different things in different files).

## Step 4 — X / y separation
- `X = df.drop('Label', axis=1)` (features), `y = df['Label']` (target)
    - *why:* the model learns from X and predicts y; they have to be separated before splitting.

## Step 5 — Train / test split (BEFORE scaling)
- `train_test_split(X, y, test_size=0.3, stratify=y, random_state=47)` → 70/30 split
    - *why (split before scale):* if you scale before splitting, the scaler's mean/std are learned from the test data too, which leaks test information into training.
    - *why (stratify=y):* keeps the benign/attack ratio equal in both sets, important because the data is only ~2.3% benign.
    - *why (random_state=47):* same split every run, so results are reproducible.
    - 70/30 split cited from: Mallampati & Hari (2024), ICEES — data leakage study on CIC-IoT 2023.

## Step 6 — Scaling
- `StandardScaler`: `fit_transform` on the training set, `transform` only on the test set
    - *why:* the scaler learns mean/std from training data only, then applies those same numbers to the test set. the test set never influences the scaler, so there is no data leakage. this also mirrors deployment, where live traffic is scaled using statistics learned during training.

## Step 7 — Save
- Wrote `train.csv` and `test.csv` to `data/scaled data/CIC-IoT-2023/`
- **Final result:** 6,265,586 flows, **2.34% benign**, 39 features
    - Train: 4,385,910 rows | Test: 1,879,676 rows

---

### Class balance (whole dataset, binary)
```
1 (attack)   6,119,265
0 (benign)     146,321     ~2.34%
```

### Raw label distribution (per-file example, before binary encoding)
```
DDOS-ICMP_FLOOD         15256      RECON-OSSCAN          197
DDOS-UDP_FLOOD          11439      RECON-PORTSCAN        154
DDOS-TCP_FLOOD           9473      DOS-HTTP_FLOOD        144
DDOS-PSHACK_FLOOD        8749      DDOS-HTTP_FLOOD        62
DDOS-RSTFINFLOOD         8749      DDOS-SLOWLORIS         50
DDOS-SYN_FLOOD           8625      DICTIONARYBRUTEFORCE   24
DDOS-SYNONYMOUSIP_FLOOD  7711      COMMANDINJECTION       16
DOS-UDP_FLOOD            7009      BROWSERHIJACKING        7
DOS-TCP_FLOOD            5631      XSS                     7
DOS-SYN_FLOOD            4409      BACKDOOR_MALWARE        7
BENIGN                   2323      RECON-PINGSWEEP         5
MIRAI-GREETH_FLOOD       2074      SQLINJECTION            4
MIRAI-UDPPLAIN           1954      UPLOADING_ATTACK        3
MIRAI-GREIP_FLOOD        1640
DDOS-ICMP_FRAGMENTATION   948      Note: some classes are tiny
VULNERABILITYSCAN         788      (UPLOADING_ATTACK = 3). This is
DDOS-ACK_FRAGMENTATION    647      why full 34-class mode would be
MITM-ARPSPOOFING          627      fragile and category-level is the
DDOS-UDP_FRAGMENTATION    610      better multiclass option.
DNS_SPOOFING              369
RECON-HOSTDISCOVERY       289
```

### Important columns
- **Label column:** `Label` — what the model learns to predict
- **Protocol feature:** `Protocol Type`
- **Timing feature:** `IAT` (inter-arrival time)
- **Traffic rate feature:** `Rate`


---

---

# CIC-IoT-DIAD-2024 Preprocessing Notes

## Data info
- **Files used:** all 129 flow-based `.csv` files
    - *why:* the dataset authors (UNB) provide `Anomaly Detection - Flow Based features` as the ML-ready CICFlowMeter version. the packet-based dataset is also intended for device identification, so it is outside the current binary anomaly-detection comparison.
- **Total raw rows:** 19,519,167
- **Num columns:** 84 (83 features + Label) (no label assigned we need to assign since it's already seperate folders)
- **Categories:** Benign, Brute Force, DDoS, DoS, Mirai, Recon, Spoofing, Web-Based

## Step 1 — Cleaning
*ML models cannot train properly with empty / missing / corrupted entries.*
- Recovered 5 headerless DoS-TCP records using the standard 84-column header check
    - *why:* each affected file contains one data row but no header. pandas otherwise interprets the record as column names and reports zero rows.
- Replaced infinity values with NaN (`df.replace([np.inf, -np.inf], np.nan)`)
    - *why:* flow-rate features such as `Flow Bytes/s` can become infinity when duration is zero or near zero. infinity breaks scaling and most classifiers.
- Removed NaN rows with `dropna()`
    - *why:* `dropna()` deletes any row with a missing value so only complete rows remain.
- Stripped column names with `df.columns.str.strip()`
    - *why:* this removes leading/trailing spaces and makes every column consistently referenceable.
- (identify which rows were removed with `nan_rows = df[df.isnull().any(axis=1)]`)

## Step 2 — Label encoding (binary)
- Replaced the `NeedManualLabel` placeholder using the top-level folder: `Benign` = 0, every attack folder = 1
    - *why:* every raw file uses `NeedManualLabel`, including benign files. encoding that text directly would incorrectly produce only one class.
- All raw attack types collapse to two classes.
    - *why:* this is the binary stage — attack vs benign. category-level and full attack-type versions are follow-ups.
- Checked with `value_counts()` after encoding.
    - *why:* this is the safety check. if only one class appears after encoding, the mapping is wrong and training should stop.

## Step 3 — Combine
- Processed and combined all cleaned/encoded files in chunks
    - *why:* the split and scaler must use one consistent dataset and schema, but loading the complete 9.7+ GB dataset into memory at once could exhaust memory.

## Step 4 — X / y separation
- Dropped `Flow ID`, `Src IP`, `Dst IP`, and `Timestamp` before modeling (prevent overfitting)
    - *why:* these identifiers can make the model memorize endpoints or collection sessions instead of learning generalizable traffic behaviour. after removing them, 79 candidate features remain.
- `X = df.drop('Label', axis=1)` (features), `y = df['Label']` (target)
    - *why:* the model learns from X and predicts y; they must be separated before splitting, and the target must never be scaled.

## Step 5 — Train / test split (BEFORE scaling)
- `train_test_split(X, y, test_size=0.3, stratify=y, random_state=47)` → 70/30 split
    - *why (split before scale):* if you scale before splitting, the scaler's mean/std are learned from test data too, which leaks test information into training.
    - *why (`stratify=y`):* keeps the benign/attack ratio equal in both sets, important because the raw dataset is only ~2.04% benign.
    - *why (`random_state=47`):* same split every run, so results are reproducible and consistent with the 2023 comparison.
    - 70/30 split retained from the CIC-IoT-2023 comparison setup cited from Mallampati & Hari (2024), ICEES.

## Step 6 — Scaling
- `StandardScaler`: `fit_transform` on the training set, `transform` only on the test set
    - *why:* the scaler learns mean/std from training data only, then applies those same numbers to the test set. the test set never influences the scaler, so there is no data leakage.

## Step 7 — Save
- Write `train.csv` and `test.csv` to `data/scaled data/CIC-IoT-2024/`
- **Final result:** to be recorded after cleaning, splitting, scaling, and saving are completed

---

### Class balance (whole raw dataset, binary)
```
1 (attack)   19,120,837   97.96%
0 (benign)      398,330    2.04%
Total        19,519,167
```

### Raw category distribution (before binary encoding)
```
DOS            14,853,092
DDOS            3,478,814
Recon             442,158
Benign            398,330
Mirai             174,588
Spoofing          157,238
Web-Based          11,328
Brute Force         3,619
```

### Web-Based distribution
```
SQL Injection       6,603
XSS                 3,377
Uploading Attack    1,348
Total              11,328
```

### Important columns
- **Label column:** `Label` — originally `NeedManualLabel`; replaced with the folder-derived binary target
- **Identifier columns removed:** `Flow ID`, `Src IP`, `Dst IP`, `Timestamp`
- **Protocol feature:** `Protocol`
- **Timing features:** `Flow Duration`, flow/Fwd/Bwd IAT statistics, active statistics, idle statistics
- **Traffic-rate features:** `Flow Bytes/s`, `Flow Packets/s`, `Fwd Packets/s`, `Bwd Packets/s`
- **Flag features:** FIN, SYN, RST, PSH, ACK, URG, CWR, ECE counts


---
