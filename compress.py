import math
import pandas as pd

from fast_linear_interpolation import FastLinearInterpolation

# todo: dedup
class color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_staired_tolerated_error(t: int, stop: int, step_count: int, max_err: float) -> float:
    if t == 0:
        return max_err
    if t >= stop:
        return 0
    
    step_x_length = stop / step_count
    step_y_size = max_err / step_count

    return max_err - ((math.floor(t / step_x_length)) * step_y_size)


def stairs_power_compress(df: pd.DataFrame, stop: float, step_count: float, max_err: float) -> pd.DataFrame:
    model = FastLinearInterpolation()

    # First point is uncompressed
    #todo: no timestamp? :(
    model.add(df.index[0], df.iloc[0].values[0])

    for i in range(1, len(df)):
        tolerated_error = get_staired_tolerated_error(i, stop, step_count, max_err)
        model.setError(tolerated_error)
        model.add(df.index[i], df.iloc[i].values[0])
    
    values = [df.iloc[0].values[0]]
    for i in range(1, len(df)):
        values.append(model.read(df.index[i]))
    
    print(f"\tFLI model state length: {len(model.data())}")

    df2 = pd.DataFrame(index=df.index)
    df2['val'] = values
    return df2

def average_compress(df: pd.DataFrame, window_size: int) -> pd.DataFrame:
    frame = df.copy()

    iterations_count = math.ceil(len(df) / window_size)
    for i in range(0, iterations_count):
        lower_bound = window_size * i
        upper_bound = lower_bound + window_size

        if upper_bound > len(df):
            upper_bound = len(df)
        print(f"\t~> Averaging values on the interval [{lower_bound}, {upper_bound}].")

        frame[lower_bound:upper_bound] = df[lower_bound:upper_bound].mean()

    print(f"\tWindow size: {window_size}")
    print(f"\tWindows count: {iterations_count}")
    return frame

def average_compress_count(df: pd.DataFrame, window_count: int) -> pd.DataFrame:
    if window_count == 1:
        print(f"\t{color.FAIL}Cannot normalize frame if averaged in a single window, skipping compression.{color.ENDC}")
        return df
    elif window_count > len(df):
        print(f"\t{color.FAIL}Cannot split frame in more windows than it contains rows, skipping compression.{color.ENDC}")
        return df

    frame = df.copy()

    window_length = round(len(df) / window_count)
    iterations_count = math.ceil(len(df) / window_length)

    for i in range(0, iterations_count):
        lower_bound = window_length * i
        upper_bound = lower_bound + window_length

        if upper_bound > len(df):
            upper_bound = len(df)
        print(f"\t~> Averaging values on the interval [{lower_bound}, {upper_bound}].")

        frame[lower_bound:upper_bound] = df[lower_bound:upper_bound].mean()

    print(f"\tWindow size: {window_length}")
    print(f"\tWindows count: {iterations_count}")
    return frame