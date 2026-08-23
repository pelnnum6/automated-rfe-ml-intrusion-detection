import pandas as pd
import numpy as np
import os
import glob # for folder traversal and file handling
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib  # Saves the training-fitted scaler for reproducibility.

our_random_state = 47 # the randomization set.
our_test_size = 0.3 # %30 test %70 train split. its found that this is the best split for the 2023 dataset. cite: S. B. Mallampati and S. Hari, "A Comparative Study on the Impacts of Data Leakage During Feature Selection using the CIC-IoT 2023 Intrusion Detection Dataset," 2024 10th International Conference on Electrical Energy Systems (ICEES), Chennai, India, 2024, pp. 1-6, doi: 10.1109/ICEES61253.2024.10776873. keywords: {Training;Recurrent neural networks;Intrusion detection;Training data;Artificial neural networks;Feature extraction;Boosting;Internet of Things;Security;Testing;Data Leakage;IoT networks;IDS;Overfitting;Feature Selection},


 
#cleaned_dir = "data/cleaned data/CIC-IoT-2023"
#scaled_dir = "data/scaled_data/CIC-IoT-2023"
#encoded_dir = "data/encoded_data/CIC-IoT-2023"
#class_mode="binary"



def label_encoding_CIC_IoT_2023():
    csv_files=glob.glob(cleaned_dir + "/Merged*.csv") #gets all the csv files in cleaned data. Based on UNB merged files are ML ready so were handling only merged files to prevent inflated data.
    os.makedirs(encoded_dir, exist_ok=True)
    if not csv_files: #error handling
        print("No CSV files found in the cleaned data directory.")
        return
    frames=[]
    for file in csv_files:
        print(f"Processing file: {file}")
        df=pd.read_csv(file,nrows=100000)
        df.columns=df.columns.str.strip() # Remove leading and trailing whitespace from column names
        print(df['Label'].value_counts()) #gets us the each unique value with its counts for label column.

        if class_mode=="binary":
            df['Label'] = df['Label'].apply(lambda x: 0 if str(x).strip().upper().startswith('BENIGN') else 1) # encoding 
        
        print(df['Label'].value_counts()) #checking the list to see if binary encoding worked correctly.
        frames.append(df) #appending the dataframe to the list of dataframes.

        file_name=os.path.basename(file)
        output_path=os.path.join(encoded_dir,file_name)
        df.to_csv(output_path,index=False)
        print(f"Saved encoded file: {output_path}")
    
    #this section is for combining all the encoded dataframes into one dataframe and checking the class balance of the whole dataset. 
    #this approach is used to ensure that scaling process can be done on the whole dataset instead of induvidual dataframes keeping scaling parameters consistent.
    combined=pd.concat(frames,ignore_index=True) #combine all 
    print("Combined shape:",combined.shape)
    print(combined['Label'].value_counts()) #class balance of the whole dataset. if only one class shows up here the encoding is wrong, do not continue to training
    return combined # combined is a dataframe. class type: pandas.core.frame.DataFrame



def split_scale(df): #df=combined 

    #splitting the data into train and test sets. 
    X=df.drop('Label',axis=1) #features
    y=df['Label'] #target variable
    os.makedirs(scaled_dir, exist_ok=True) #create the output folder if it doesn't exist, to_csv can't create folders itself
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=our_test_size, random_state=our_random_state,stratify=y) #stratify=y ensures benign and attack ratio equal in both train and test sets.
    print("Train shape:",X_train.shape,"Test shape:",X_test.shape) # this is the shape of the train and test sets such as (row, column) nums.
    
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train),columns=X_train.columns) # this is the scaled version of the train set. fit_transform is used to fit the scaler to the train set and then transform it.
    X_test_scaled = pd.DataFrame(scaler.transform(X_test),columns=X_test.columns) # this is the scaled version of the test set. transform is used to transform the test set using the scaler fitted to the train set.

    X_train_scaled["Label"]=y_train.values #putting label column back
    X_test_scaled["Label"] =y_test.values

    #this is the part where we save the scaled train and test sets to csv files.
    X_train_scaled.to_csv(os.path.join(scaled_dir,"train.csv"),index=False)
    X_test_scaled.to_csv(os.path.join(scaled_dir,"test.csv"),index=False)
    print(f"Saved: {scaled_dir}/train.csv")
    print(f"Saved: {scaled_dir}/test.csv")
 
    return X_train_scaled, X_test_scaled, y_train, y_test #theyre all pandas dataframes. class type: pandas.core.frame.DataFrame

#df=label_encoding_CIC_IoT_2023() 
#X_train_scaled, X_test_scaled, y_train, y_test=split_scale(df) 


"""
df=pd.read_csv('./TrafficLabelling /Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv',nrows=100000)
print(df.columns)
print(df.shape)
df.columns = df.columns.str.strip() # Remove leading and trailing whitespace from column names
print(df["Label"].value_counts()) #after removing the leading and trailing whitespace, we can see that the value counts for the "Label" column are now correct, with 6768 Benign and 6789 Infiltration samples. This indicates that the issue was indeed caused by the leading and trailing whitespace in the column names, which prevented us from accurately counting the values in the "Label" column.
"""

def clean_CIC_IoT_2023():
    with open("csv_files_2023.txt", "r") as file:
        csv_files = file.read().splitlines() #now we hav ecsv_files as a list of csv file names. 372 csv files in total

    output_folder="data/cleaned data/CIC-IoT-2023"
    os.makedirs(output_folder, exist_ok=True) #create the output folder if it doesn't existing already

    for file in csv_files:
        print(f"Processing file: {file}")
        df=pd.read_csv(file,nrows=100000)

        #before cleaning part:
        print("before cleaning:")
        print(df.shape)
        print(df.columns)
        #print(df['Label'].value_counts())
        nan_rows = df[df.isnull().any(axis=1)]
        print("Rows containing NaN values BEFORE cleaning:",nan_rows)

        #cleaning part:
        df.replace([np.inf,-np.inf],np.nan,inplace=True)
        df.dropna(inplace=True)

        file_name=os.path.basename(file) #get the file name from the file path
        output_path=os.path.join(output_folder,file_name) #create the output file path
        df.to_csv(output_path,index=False) #save the cleaned dataframe to the output path

        #after cleaning part:
        print("after cleaning:")
        print(df.shape)
        print(df.columns)

        print(f"Saved cleaned file: {output_path}")
    
""" 
for testing the code on one csv file:
df=pd.read_csv('data/CIC-IoT-2023/MERGED_CSV/Merged44.csv',nrows=100000)
print("before cleaning:")
print(df.shape)
print(df.columns)
print(df['Label'].value_counts())
nan_rows = df[df.isnull().any(axis=1)]

print("Rows containing NaN values BEFORE cleaning:")
print(nan_rows)

df.replace([np.inf,-np.inf],np.nan,inplace=True)
df.dropna(inplace=True)

print("after cleaning:")
print(df.shape)
print(df.columns)
print(df['Label'].value_counts())
"""


raw_dir = "data/CIC-IoT-2024"
cleaned_dir = "data/encoded_data/CIC-IoT-2024"
#scaled_dir = "data/scaled_data/CIC-IoT-2023"
class_mode="binary"
chunk_size = 250000 #instead if loading entire file on RAM reads 250000 at a time.

def clean_encode_CIC_IoT_2024():
    csv_files = glob.glob(
        raw_dir + "/**/*.csv",
        recursive=True
    )
    csv_files.sort()
    os.makedirs(
        cleaned_dir,
        exist_ok=True
    )

#error handling sceniors 

    if not csv_files: #error prompting
        print(
            "No CSV files found in the CIC-IoT-2024 directory."
        )
        return
    if len(csv_files) != 129: #imcomplete prompting
        print(
            f"Expected 129 files, but found {len(csv_files)}."
        )
        return

    benign_files = glob.glob(raw_dir + "/Benign/*.csv")


#this header check is only needed for DoS-TCP_Flood.pcap_Flow csv files (there is 5) to 


    benign_files.sort()  # Sort the benign files so the same reference file is selected every run.
    
    if not benign_files:
        print("No benign CSV files were found in:",raw_dir + "/Benign")
        return


    reference_file = benign_files[0]  # We use its header as the correct 84 column schema.
    reference_header = pd.read_csv( 
        reference_file,
        nrows=0
    )

    canonical_columns = ( # Remove leading and trailing spaces from the reference column names.
        reference_header.columns
        .str.strip()
        .tolist()
    )

    if len(canonical_columns) != 84: # Print an error if the reference file has the wrong structure.
        print(
            f"Expected 84 columns, but found "
            f"{len(canonical_columns)}."
        )
        return

    if "Label" not in canonical_columns: # Verifying that the final target column (Label)is present.
        print(
            "The reference file does not contain the Label column."
        )
        return

    

    total_rows_before = 0
    total_rows_after = 0
    total_rows_removed = 0
    headerless_files = 0

    # Processes each of the 129 CSV files one at a time.
    for file_number, file in enumerate(
        csv_files,
        start=1
    ):
        print(     #to track better 
            f"\nProcessing file "
            f"{file_number}/{len(csv_files)}: {file}"
        )

        current_header = pd.read_csv(file,nrows=0)

        # Strip spaces and convert the column names into a list to make it easier to compare and identify if the header is right order with reference header.
        file_columns = (current_header.columns.str.strip().tolist())

        if file_columns == canonical_columns:   # The check of whether this file has the correct official header or not.
            chunks = pd.read_csv(file,chunksize=chunk_size,low_memory=False)

        elif (   #for the DoS-TCP files  this elif is basically if headers don't match it means there's either no header or were missing a column with the statement of checking column num and label column this means its def a TCP file.
            os.path.basename(file).startswith("DoS-TCP_Flood"),
            len(file_columns) == 84
            and file_columns[-1] == "NeedManualLabel"
        ):
            print("Headerless TCP file detected.")
            headerless_files += 1 
            chunks = pd.read_csv( # Reading the file without treating the first row as a header.
                file,
                header=None,  # Telling pandas that the file does not contain a header row.
                names=canonical_columns,  # Applying the correct 84 official column names.
                chunksize=chunk_size, # Continue using memory safe chunks.
                low_memory=False # Prevents pandas from changing its type inference middle of the file.
            )

        else: # Handle any file that does not match either expected structure stop the process.
            raise ValueError(
                f"Unexpected columns in file: {file}"
            )

        relative_path = os.path.relpath(file,raw_dir) #gets the relative path from CIC-IoT-2024/DoS/file to recreate in cleaned_2024 folder
        category = relative_path.split(os.sep)[0] # get the name Benign, DDOS, DOS, Mirai, etc. for encoding
        binary_label = 0 if category == "Benign" else 1 #encoding itself

        output_path = os.path.join(cleaned_dir,relative_path)
        os.makedirs(os.path.dirname(output_path),exist_ok=True)
        first_chunk = True # Track whether we are saving the first chunk of this file.
        file_rows_before = 0 # Count the current file's original rows.
        file_rows_after = 0  # Count the current file's cleaned rows.


        for df in chunks:# Processing every chunk from the current file.
            df.columns = canonical_columns
            file_rows_before += len(df) # Adding to the current chunk size to the before cleaning count.

            # Replace positive and negative infinity with NaN.
            df.replace(
                [np.inf, -np.inf],
                np.nan,
                inplace=True
            )
            # Find rows containing at least one NaN value.
            # This is done before removing them so we can record the count.
            nan_rows = df[
                df.isnull().any(axis=1)
            ]
            if not nan_rows.empty:
                print("Rows containing NaN or infinity "
                    "before cleaning:",
                    len(nan_rows))

            df.dropna( # Remove every row containing NaN values.
                inplace=True)
            df["Label"] = binary_label #encoding acc changing part
            file_rows_after += len(df) # Adding the remaining chunk size to the cleaned row count. 
            df.to_csv(
                output_path,

            # Overwrite the file for the first chunk.
                # Append every later chunk to the same file.
                mode="w" if first_chunk else "a",
                header=first_chunk,
                index=False #for pandas do not add row nums.
            )
            first_chunk = False# rest of the chunks must append without rewriting the header.
        rows_removed = ( # Calc how many rows were removed from this file.
            file_rows_before - file_rows_after
        )
        total_rows_before += file_rows_before
        total_rows_after += file_rows_after
        total_rows_removed += rows_removed
        print("Before cleaning:",file_rows_before)
        print("After cleaning:",file_rows_after)
        print("Rows removed:",rows_removed)
        print(f"Saved cleaned file: {output_path}")
    print("\nCIC-IoT-2024 CLEANING AND ENCODING COMPLETE")  
    print("Files processed:", len(csv_files))  # This should print 129.
    print("Headerless files repaired:", headerless_files)  # This should print 5.
    print("Total rows before cleaning:", total_rows_before)  # This should initially equal 19,519,167.
    print("Total rows after cleaning:", total_rows_after)  # The num of valid rows 
    print("Total rows removed:", total_rows_removed)  # The total num of invalid rows removed 

#clean_encode_CIC_IoT_2024()


combined_dir = "data/combined_data/CIC-IoT-2024"
combined_file = os.path.join(combined_dir, "CIC-IoT-2024_combined.csv")

def combine_CIC_IoT_2024():
    csv_files = glob.glob(cleaned_dir + "/**/*.csv", recursive=True) 
    csv_files.sort()
    if len(csv_files) != 129:
        print(f"Expected 129 encoded files, but found {len(csv_files)}.")
        return
    os.makedirs(combined_dir,exist_ok=True)
    if os.path.exists(combined_file):
        print("Combined file already exists:")
        print(combined_file)
        print("Delete or rename it before running this function again.")
        return

    first_chunk = True
    total_rows = 0
    for file_number, file in enumerate(csv_files,start=1): # Process each encoded CSV file individually.
        print(f"\nCombining file "f"{file_number}/{len(csv_files)}: {file}")
        chunks = pd.read_csv( # Process each encoded CSV file individually.
            file,
            chunksize=chunk_size,
            low_memory=False)

        for df in chunks:
            total_rows += len(df)
            # Write the first chunk with column names.
            # Append later chunks without repeating the column names.
            df.to_csv(combined_file,mode="w" if first_chunk else "a",header=first_chunk,index=False)
            first_chunk = False

    print("\nCIC-IoT-2024 COMBINATION COMPLETE")
    print("Files combined:", len(csv_files))
    print("Total combined rows:", total_rows)
    print("Combined file:", combined_file)

# combine_CIC_IoT_2024()


import joblib  # Saves the training-fitted scaler for reproducibility.


combined_file = "data/combined_data/CIC-IoT-2024/CIC-IoT-2024_combined.csv"
scaled_dir = "data/scaled_data/CIC-IoT-2024"
temporary_dir = os.path.join(scaled_dir, "temporary_unscaled")  # Stores the x and y split before scaling.

temporary_train_file = os.path.join(temporary_dir, "train_unscaled.csv")
temporary_test_file = os.path.join(temporary_dir, "test_unscaled.csv")

train_file = os.path.join(scaled_dir, "train.csv")
test_file = os.path.join(scaled_dir, "test.csv")
scaler_file = os.path.join(scaled_dir, "standard_scaler.joblib")

our_random_state = 47  # Uses the same reproducible randomization as CIC-IoT-2023.
our_test_size = 0.3  # Creates a 70% training and 30% testing split.
chunk_size = 250000 

columns_to_remove = ["Flow ID", "Src IP", "Dst IP", "Timestamp"]  # Removes identifiers that could cause memorization and leakage.


def count_labels_CIC_IoT_2024():

    label_counts = {0: 0, 1: 0}  # Stores the benign and attack counts.
    chunks = pd.read_csv(
        combined_file,
        usecols=["Label"],
        chunksize=chunk_size,
        low_memory=False
    )  # Reads only Label because no features are needed during counting.

    for df in chunks:
        current_counts = df["Label"].astype("int8").value_counts()  # Counts binary labels in the current chunk.

        for label, count in current_counts.items():
            if label not in label_counts:  # Stops if a label other than 0 or 1 appears.
                raise ValueError(f"Unexpected label found: {label}")

            label_counts[label] += int(count)  # Adds the current chunk count to the complete count.

    if label_counts[0] == 0 or label_counts[1] == 0:  # Both classes must exist before splitting.
        raise ValueError(f"Both binary classes were not found: {label_counts}")

    print("Label count complete:", label_counts)

    return label_counts


def calculate_test_targets_CIC_IoT_2024(label_counts):

    total_rows = sum(label_counts.values())  # Calculates the complete cleaned dataset size.
    total_test_rows = int(np.ceil(total_rows * our_test_size))  # Matches sklearn by rounding the test size upward.

    exact_targets = {
        label: count * our_test_size
        for label, count in label_counts.items()
    }  # Calculates each class's exact decimal test target.

    test_targets = {
        label: int(np.floor(target))
        for label, target in exact_targets.items()
    }  # Initially rounds each class target downward.

    remaining_positions = total_test_rows - sum(test_targets.values())  # Finds any test positions still unassigned.

    labels_by_remainder = sorted(
        label_counts,
        key=lambda label: exact_targets[label] - test_targets[label],
        reverse=True
    )  # Gives extra positions to classes with the largest decimal remainder.

    for label in labels_by_remainder[:remaining_positions]:
        test_targets[label] += 1  # Ensures the test set has exactly 30% of the complete dataset.

    print("Exact stratified test targets:", test_targets)

    return test_targets


def create_stratified_split_CIC_IoT_2024(label_counts, test_targets):

    os.makedirs(temporary_dir, exist_ok=True) 
    if os.path.exists(temporary_train_file) or os.path.exists(temporary_test_file):  # Prevents appending to an incomplete previous split.
        raise FileExistsError("Temporary split files already exist. Remove them before rerunning.")

    combined_columns = pd.read_csv(combined_file, nrows=0).columns.str.strip().tolist()  # Reads only the combined header.
    feature_columns = [
        column
        for column in combined_columns
        if column not in columns_to_remove + ["Label"]
    ]  # Keeps Label separate and removes the four identifier columns from X.

    if len(feature_columns) != 79:  # The 84-column dataset should produce exactly 79 model features after removal.
        raise ValueError(f"Expected 79 model features, but found {len(feature_columns)}.")

    random_generator = np.random.default_rng(our_random_state)  # Creates reproducible random test row selection for seperation .

    remaining_class_rows = label_counts.copy()  # Tracks how many rows from each class remain unread.
    remaining_test_rows = test_targets.copy()  # Tracks how many rows each class still needs in test.

    first_train_chunk = True  # Ensures the train header is written only once.
    first_test_chunk = True  # Ensures the test header is written only once.

    train_rows = 0
    test_rows = 0
    chunk_number = 0

    print("Starting the split...")

    chunks = pd.read_csv(
        combined_file,
        chunksize=chunk_size,
        low_memory=False
    )  # Reads the complete dataset without loading it all into memory.

    for df in chunks:
        chunk_number += 1
        df.columns = df.columns.str.strip()  # Keeps all column names consistent.

        labels = df["Label"].astype("int8").to_numpy()  # Separates 
        X = df.drop(columns=columns_to_remove + ["Label"])  # Removes Label and the four identifier columns.

        test_mask = np.zeros(len(df), dtype=bool)  # Starts with every row assigned to training.
        for label in sorted(label_counts):
            class_positions = np.flatnonzero(labels == label)  # Finds the current class rows inside this chunk.
            current_class_rows = len(class_positions)
            if current_class_rows == 0:
                continue

            selected_test_count = random_generator.hypergeometric(
                ngood=remaining_test_rows[label],
                nbad=remaining_class_rows[label] - remaining_test_rows[label],
                nsample=current_class_rows
            )  # Selects the correct stratified number of test rows from this chunk.

            if selected_test_count > 0:
                selected_positions = random_generator.choice(
                    class_positions,
                    size=selected_test_count,
                    replace=False
                )  # Randomly selects the test rows without selecting the same row twice.
                test_mask[selected_positions] = True  # Marks the selected positions as testing rows.

            remaining_class_rows[label] -= current_class_rows  # Updates the unread class-row count.
            remaining_test_rows[label] -= int(selected_test_count)  # Updates the remaining test target.

        train_mask = ~test_mask  # Every row not selected for testing becomes a training row.

        train_chunk = X.loc[train_mask].copy()
        test_chunk = X.loc[test_mask].copy()
        train_chunk["Label"] = labels[train_mask]  # Adds the correct training labels back without scaling.
        test_chunk["Label"] = labels[test_mask]  # Adds the correct testing labels back without scaling.

        train_chunk.to_csv(
            temporary_train_file,
            mode="w" if first_train_chunk else "a",
            header=first_train_chunk,
            index=False
        )  # Writes the first train header and appends all later chunks.

        test_chunk.to_csv(
            temporary_test_file,
            mode="w" if first_test_chunk else "a",
            header=first_test_chunk,
            index=False
        )  # Writes the first test header and appends all later chunks.

        train_rows += len(train_chunk)
        test_rows += len(test_chunk)

        first_train_chunk = False
        first_test_chunk = False

        if chunk_number % 10 == 0:  # Provides minimal progress information every ten chunks.
            print(f"Split progress: {train_rows + test_rows:,} rows processed")

    if any(remaining_class_rows.values()) or any(remaining_test_rows.values()):  # Every row and test target must be fully allocated.
        raise RuntimeError("The stratified split did not allocate every row correctly.")

    print("Split complete:", f"{train_rows:,} train | {test_rows:,} test")

    return feature_columns, train_rows, test_rows


def fit_training_scaler_CIC_IoT_2024(feature_columns, expected_train_rows):
    scaler = StandardScaler()  # Creates a new scaler that has never seen testing data for leakage safe scalign.
    fitted_rows = 0
    chunk_number = 0
    print("Fitting scaler on training data only...")

    chunks = pd.read_csv(
        temporary_train_file,
        chunksize=chunk_size,
        low_memory=False
    )  # Reads only the ttraining dataset.

    for df in chunks:
        chunk_number += 1
        X_train_chunk = df[feature_columns]  # Excludes Label because the target must never be scaled.
        scaler.partial_fit(X_train_chunk)  # Learns statistics incrementally from training features only.
        fitted_rows += len(X_train_chunk)

        if chunk_number % 10 == 0:  # Provides minimal scaler progress every ten chunks.
            print(f"Scaler progress: {fitted_rows:,} training rows")

    if fitted_rows != expected_train_rows:  # Verifies that every training row influenced the scaler.
        raise RuntimeError(
            f"Scaler expected {expected_train_rows} training rows, "
            f"but received {fitted_rows}."
        )
    joblib.dump(scaler, scaler_file)  # Saves the training-fitted scaler for reproducibility.
    print("Scaler fitted successfully on:", f"{fitted_rows:,} training rows")
    return scaler


def scale_dataset_CIC_IoT_2024(input_file,output_file,scaler,feature_columns,dataset_name,expected_rows):
    first_chunk = True  # Ensures the output header is written only once.
    scaled_rows = 0
    chunk_number = 0

    print(f"Scaling and saving {dataset_name} data...")
    chunks = pd.read_csv(
        input_file,
        chunksize=chunk_size,
        low_memory=False
    )  # Reads the selected train or test dataset in memory safe chunks.

    for df in chunks:
        chunk_number += 1
        labels = df["Label"].astype("int8").to_numpy()  # Keeps labels separate and unscaled.
        scaled_values = scaler.transform(df[feature_columns])  # Uses only training statistics for both datasets.
        scaled_chunk = pd.DataFrame(
            scaled_values,
            columns=feature_columns
        )  # Restores the original feature names after StandardScaler returns an array.

        scaled_chunk["Label"] = labels  # Adds the original binary labels back after scaling.
        scaled_chunk.to_csv(
            output_file,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False
        )  # Writes the first header and appends every later scaled chunk.

        scaled_rows += len(scaled_chunk)
        first_chunk = False

        if chunk_number % 10 == 0:  # Provides minimal progress every ten chunks.
            print(f"{dataset_name} progress: {scaled_rows:,} rows")

    if scaled_rows != expected_rows:  # Verifies that no rows disappeared during scaling.
        raise RuntimeError(
            f"{dataset_name} expected {expected_rows} rows, "
            f"but saved {scaled_rows}."
        )

    print(f"{dataset_name} complete:", f"{scaled_rows:,} rows")
    return scaled_rows


def preprocess_split_scale_CIC_IoT_2024():

    if not os.path.exists(combined_file):  # Stops if the completed combined dataset cannot be found.
        print("Combined dataset was not found:", combined_file)
        return

    os.makedirs(scaled_dir, exist_ok=True)  # Creates the final scaled-data directory.
    if os.path.exists(train_file) or os.path.exists(test_file):  # Prevents overwriting completed or partial final files.
        print("A final train.csv or test.csv already exists.")
        print("Remove incomplete output files before rerunning.")
        return

    label_counts = count_labels_CIC_IoT_2024()
    test_targets = calculate_test_targets_CIC_IoT_2024(label_counts)
    feature_columns, train_rows, test_rows = create_stratified_split_CIC_IoT_2024(label_counts,test_targets)
    scaler = fit_training_scaler_CIC_IoT_2024(feature_columns,train_rows)
    saved_train_rows = scale_dataset_CIC_IoT_2024(temporary_train_file,train_file,scaler,feature_columns,"Training",train_rows)
    saved_test_rows = scale_dataset_CIC_IoT_2024(temporary_test_file,test_file,scaler,feature_columns,"Testing",test_rows)

    os.remove(temporary_train_file)  # Deletes temporary training data only after final scaling succeeds.
    os.remove(temporary_test_file)  # Deletes temporary testing data only after final scaling succeeds.
    os.rmdir(temporary_dir)  # Removes the now-empty temporary folder.

    print("\nCIC-IoT-2024 PREPROCESSING COMPLETE")
    print("Training rows:", saved_train_rows)
    print("Testing rows:", saved_test_rows)
    print("Model features:", len(feature_columns))
    print("Final columns:", len(feature_columns) + 1)
    print("Scaler fitted on testing data: False")
    print("Leakage prevention checks: PASSED")
    print("Saved:", train_file)
    print("Saved:", test_file)
    print("Saved scaler:", scaler_file)


preprocess_split_scale_CIC_IoT_2024()