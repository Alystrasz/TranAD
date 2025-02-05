import math
import pandas as pd

from fast_linear_interpolation import FastLinearInterpolation

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
