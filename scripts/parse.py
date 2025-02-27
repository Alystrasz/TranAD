import matplotlib.pyplot as plt
import pandas as pd
import os
import re
import sys

def parse_log_file(path):
    f = open(path, "r")
    text = f.read()
    f.close()
    result = {}

    # FN
    matches = re.findall("'FN': [0-9]+", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+", matches[0])
        result["fn"] = int(numbers[0])

    # FP
    matches = re.findall("'FP': [0-9]+", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+", matches[0])
        result["fp"] = int(numbers[0])

    # ROC/AUC
    matches = re.findall("'ROC/AUC': [0-9]+.[0-9]*", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+.[0-9]*", matches[0])
        result["auc"] = float(numbers[0])

    # TN
    matches = re.findall("'TN': [0-9]+", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+", matches[0])
        result["tn"] = int(numbers[0])

    # TP
    matches = re.findall("'TP': [0-9]+", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+", matches[0])
        result["tp"] = int(numbers[0])

    # f1
    matches = re.findall("'f1': [0-9]+.[0-9]*", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+.[0-9]*", matches[0])
        result["f1"] = float(numbers[1])

    # precision
    matches = re.findall("'precision': [0-9]+.[0-9]*", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+.[0-9]*", matches[0])
        result["precision"] = float(numbers[0])

    # recall
    matches = re.findall("'recall': [0-9]+.[0-9]*", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+.[0-9]*", matches[0])
        result["recall"] = float(numbers[0])

    # threshold
    matches = re.findall("'threshold': [0-9]+.[0-9]*", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+.[0-9]*", matches[0])
        result["threshold"] = float(numbers[0])

    # Compression ratio
    original_length = 0
    matches = re.findall("Length before compression: [0-9]+", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+", matches[0])
        original_length = int(numbers[0])
    compressed_length = 0
    matches = re.findall("Length after compression: [0-9]+", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+", matches[0])
        compressed_length = int(numbers[0])
        result["len"] = compressed_length
    ## Override length case for FLI models
    matches = re.findall("FLI model state length: [0-9]+", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+", matches[0])
        compressed_length = int(numbers[0])
        result["len"] = compressed_length
    # Override length case for AVG compression
    matches = re.findall("Windows count: [0-9]+", text)
    if len(matches) != 0:
        numbers = re.findall("[0-9]+", matches[0])
        compressed_length = int(numbers[0])
        result["len"] = compressed_length

    result["compression_ratio"] = original_length / compressed_length

    return result

def parse_directory(dir_path, print_df=True):
    results = []
    files = os.listdir(dir_path)

    if re.findall(".*\.[0-9].log", files[0]):
        print("Multiple files detected, averaging...")
        return parse_multiple_benchmarks_directory(dir_path, print_df)

    for file in files:
        file_path = os.path.join(dir_path, file)
        results.append( parse_log_file(file_path) )

    df = pd.DataFrame(results)
    df = df.sort_values('compression_ratio')

    if print_df == True:
        print(df.to_string(index=False))

    return df

def parse_multiple_benchmarks_directory(dir_path, print_df=True):
    files = os.listdir(dir_path)
    avg_results = {}

    for file in files:
        file_path = os.path.join(dir_path, file)

        # First match is the count of removed points, second match is the benchmark occurrence
        matches = re.findall("[0-9]+", file)
        count = matches[0]
        occ = matches[1]

        result = parse_log_file(file_path)
        if count not in avg_results:
            avg_results[count] = [result]
        else:
            avg_results[count].append(result)

    results = []
    # Compile all results through averaging
    for key, value in avg_results.items() :
        tmp_df = pd.DataFrame(value)

        #avg each df column
        result = {}
        for col in list(tmp_df.columns.values):
            result[col] = tmp_df.loc[:, col].mean()
        results.append(result)

    df = pd.DataFrame(results)
    df = df.sort_values('compression_ratio')

    if print_df == True:
        print(df.to_string(index=False))

    return df


def compare_benchmarks(*directories):
    """
    Creates a matplotlib chart to compare two benchmarks' results.
    
    You need to have PyQt5 installed to display the chart: `pip install PyQt5==5.9.2`.
    """
    
    # Draw chart
    plt.figure()

    for dir in directories:
        results = parse_directory(dir, False)

        # Remove trailing "/" from directory name if needed
        if dir[-1] == "/":
            dir = dir[:-1]

        x = results["compression_ratio"]
        plt.plot(x, results["precision"], label=os.path.basename(dir))

    #plt.xscale('log')

    plt.title('TranAD precision comparison between two benchmarks')
    plt.ylabel('Precision')
    plt.xlabel('Compression ratio')
    plt.legend()
    plt.show()

# Main
l = len(sys.argv)
if l < 2:
    raise Exception("Wrong format:\n\tpython scripts/parse.py path/to/log\n\tpython scripts/parse.py path/to/log/dir1 path/to/log/dir2")
path = sys.argv[1]

if os.path.isfile(path):
    result = parse_log_file(path)
    print(result)
elif l == 2 and os.path.isdir(path):
    parse_directory(path)
elif l >= 3:
    compare_benchmarks(*sys.argv[1:])
else:
    raise Exception("Input path is not a file neither a directory (?).")
