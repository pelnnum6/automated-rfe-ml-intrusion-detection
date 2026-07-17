import pandas as pd
import numpy as np
import os
import glob # for folder traversal and file handling
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

our_random_state = 47 # the randomization set.
our_test_size = 0.3 # %30 test %70 train split. its found that this is the best split for the 2023 dataset. cite: S. B. Mallampati and S. Hari, "A Comparative Study on the Impacts of Data Leakage During Feature Selection using the CIC-IoT 2023 Intrusion Detection Dataset," 2024 10th International Conference on Electrical Energy Systems (ICEES), Chennai, India, 2024, pp. 1-6, doi: 10.1109/ICEES61253.2024.10776873. keywords: {Training;Recurrent neural networks;Intrusion detection;Training data;Artificial neural networks;Feature extraction;Boosting;Internet of Things;Security;Testing;Data Leakage;IoT networks;IDS;Overfitting;Feature Selection},


 
cleaned_dir = "data/cleaned data/CIC-IoT-2023"
scaled_dir = "data/scaled data/CIC-IoT-2023"
encoded_dir = "data/encoded data/CIC-IoT-2023"
class_mode="binary"


def label_encoding_CIC_IDS_2017():
    csv_files=glob.glob("data/cleaned data/CIC-IDS-2017/*.csv") #get all csv files in the folder and store them in a list called csv_files

    output_folder="data/encoded data/CIC-IDS-2017"
    os.makedirs(output_folder, exist_ok=True)

    for file in csv_files:
        print(f"Processing file: {file}")
        df=pd.read_csv(file,nrows=100000)

        df[' Label'] = df[' Label'].apply(lambda x: 0 if x == 'BENIGN' else 1) # encoding itself

        file_name=os.path.basename(file)
        output_path=os.path.join(output_folder,file_name)
        df.to_csv(output_path,index=False)
        print(f"Saved encoded file: {output_path}")

    return df

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

df=label_encoding_CIC_IoT_2023() 
X_train_scaled, X_test_scaled, y_train, y_test=split_scale(df) 








def clean_CIC_IDS_2017():
    with open("csv_files_2017_ml.txt", "r") as file:
        csv_files = file.read().splitlines()

    output_folder="data/cleaned data/CIC-IDS-2017"
    os.makedirs(output_folder, exist_ok=True)
    for file in csv_files:
        print(f"Processing file: {file}")
        df=pd.read_csv(file,nrows=100000)
        print("before cleaning:")
        print(df.shape)
        print(df.columns)

        nan_rows = df[df.isnull().any(axis=1)]
        print("Rows containing NaN values BEFORE cleaning:",nan_rows)

        df.replace([np.inf,-np.inf],np.nan,inplace=True)
        df.dropna(inplace=True)

        file_name=os.path.basename(file)
        output_path=os.path.join(output_folder,file_name)
        df.to_csv(output_path,index=False)

        print("after cleaning:")
        print(df.shape)
        print(df.columns)
        
        print(f"Saved cleaned file: {output_path}")

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

