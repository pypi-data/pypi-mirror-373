# F.I.R.E. Factor Investment Research Engine

This repo is the bundled opensource toolkit for book _Navigating the Factor Zoo：The Science of Quantitative Investing_.

## Installation

```bash
# for stable version
pip install firefin

# for test and nightly version
pip install -i https://test.pypi.org/simple/ firefin

# Install from source for loacl testing!!!
## replace $ThisRepoURL with the actual repo url
git clone $ThisRepoURL 
## install from source
pip install -e .
```

## Usage

Download the data 
from [here](https://github.com/fire-institute/fire/releases/download/marketdata/AStockData.tar.gz)

run the command and download data put in correct path automatically.

```bash
# We have not released this repo yet, so you need download the data manually!!! See command below!!!
# Auto download data
firefin download
```

If you have already downloaded the data from [here](https://github.com/fire-institute/fire/releases/download/marketdata/AStockData.tar.gz), you can run the command to check the data and put the data in the correct path

```bash
# replace path_to_data.tar.gz with the actual path
firefin load path_to_data.tar.gz
```

## Start to code

```python
import firefin

# get data
data = firefin.fetch_data(["open", "close", "volume"])
open_price = data["open"]


def pv_corr(close, volume):
    # price volume correlation
    return close.rolling(20).corr(volume)


factor = pv_corr(data["close"], data["volume"])

# compute forward returns
fr = firefin.compute_forward_returns(open_price.shift(-1), [1, 5, 10])

# evaluate factor
mng = firefin.Evaluator(factor, fr)
mng.get_ic("pearson")
mng.get_quantile_returns(5)

```

## Features

1. handy functions for fast factor computation
2. various tools for factor evaluation


