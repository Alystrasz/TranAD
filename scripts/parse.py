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

    # Dataset name
    matches = re.findall("Training TranAD on (.+)\x1b\[0m", text)
    if len(matches) != 0:
        result["dataset"] = matches[0]

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
            # Don't mean the column containing the dataset name
            if col == "dataset":
                continue
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
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5), gridspec_kw={'wspace': 0.1, 'hspace': 0.2})
    plt.subplots_adjust(left=0.04, right=0.98)
    ax1.set_title("f1")
    ax1.set_xlabel('Compression ratio')
    ax1.set_xscale('log')

    ax2.set_title("AUC/ROC")
    ax2.set_xlabel('Compression ratio')
    ax2.set_xscale('log')

    ax3.set_title("Precision / recall")
    ax3.set_xlabel('Compression ratio')
    ax3.set_xscale('log')

    # Dataset name
    dataset = None

    for i, dir in enumerate(directories):
        results = parse_directory(dir, False)

        # Remove trailing "/" from directory name if needed
        if dir[-1] == "/":
            dir = dir[:-1]

        x = results["compression_ratio"]
        ax1.plot(x, results["f1"], label=os.path.basename(dir), marker=".")
        ax2.plot(x, results["auc"], marker=".")
        ax3.plot(x, results["precision"], marker=".")
        ax3.plot(x, results["recall"], marker=",", linestyle="dotted", color=ax3.get_lines()[len(ax3.get_lines())-1].get_color())

        if dataset == None:
            dataset = results["dataset"].values[0]

    fig.suptitle(f'TranAD precision on {dataset} dataset with several compression techniques')
    fig.legend()
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
