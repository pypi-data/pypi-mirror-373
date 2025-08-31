# Easy Recommender

**English** | [日本語](README.ja.md)

⚠️ **This package is currently broken and under repair. Please do not use.** ⚠️

**This project only works with Python 3.11.11 because LightFM requires this specific version. Other versions are not supported.**

A simple and efficient recommendation system library using LightFM.

## Features

- Simple API for building recommendation systems
- Support for both implicit and explicit feedback
- Built on top of proven library (LightFM)
- Easy data preprocessing utilities

## Installation

```bash
pip install easy-recommender
```

## Quick Start

```python
from easy_recommender import recommend, process_df, build_feature_data
import pandas as pd

# Load your data
df = pd.read_csv('your_ratings.csv')

user_features = ['gender', 'age']
item_features = ['price', 'genre']

# Get recommendations
recommendations = recommend(
    processed_df, 
    user_features, 
    item_features,
)

print(recommendations)
```

Higher values indicate items that are more recommended.

If you want to recommend users for items instead, please swap the user and item columns.

## Data Requirements
This library takes user behavior log CSV as an argument.
Behavior logs are records of users purchasing/viewing/liking item A.

Specifically, to use this library, you need CSV data in the following format:

- **CSV with headers**: Must include column names
- **Required columns**: `user_id` and `item_id` must be present
- **Feature columns**: 
  - User-related column names should be specified as `user_features` (list of strings)
  - Item-related column names should be specified as `item_features` (list of strings)
  - If you have columns that don't belong to either users or items, include them in `user_features`
- **Data quality**: Columns with many null or undefined values may affect recommendation accuracy. Please remove such columns in advance.

### Data Example
For example, the following data format is expected. Note that case sensitivity matters.
Also, there is no automatic conversion between numeric and string types. If you write rankings as "1", it's treated as a string. If categories are handled as numbers like 2,3, they are treated as numeric values, which may reduce recommendation accuracy.

```csv
user_id,item_id,gender,age,price,genre
1,101,M,25,1200,Action
1,102,M,25,800,Comedy
2,101,F,30,1200,Action
```

## Requirements

- Python =3.11.11

## License

MIT License

## References

This implementation is based on the approach described in:
https://zenn.dev/genda_jp/articles/2c2a1b5d185741