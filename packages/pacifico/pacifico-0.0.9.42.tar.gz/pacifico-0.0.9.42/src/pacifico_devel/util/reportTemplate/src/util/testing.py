import string
import random
import numpy as np
import pandas as pd

import typing as typ


def _makeRandomString(length: int = 10):
    return "".join(random.choices(string.ascii_lowercase,
                                  k=length)
                   )


def makeRandomCategoricalDf(shape: typ.Tuple[int, int]):
    cols = [f"value_{i}" for i in range(shape[1])]
    idx = pd.date_range(start="2000-01-01", periods=shape[0])
    df = pd.DataFrame(np.random.randint(-100,
                                        100,
                                        size=shape),
                      columns=cols,
                      index=idx)
    df["category"] = [_makeRandomString(shape[0])
                      for _ in range(shape[0])]
    return df


if __name__ == '__main__':
    print(makeRandomCategoricalDf(shape=(20, 3)))
    print(makeRandomCategoricalDf(shape=(1, 3))["value_0"].values)
