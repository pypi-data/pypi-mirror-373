import pandas as pd
from typing import List, Tuple, Dict, Optional
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import coo_matrix
from lightfm.data import Dataset
from lightfm import LightFM
import numpy as np


def build_feature_data(df: pd.DataFrame, target_column_name: str) -> List[Tuple[int, Dict]]:
    """カテゴリ変数は0.5、連続変数は0-1に正規化して特徴量辞書を生成"""
    result = []
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    continuous_cols = df.select_dtypes(include=['int', 'float']).columns.tolist()
    # user_id, item_idは正規化する必要がないため除外（あれば）
    continuous_cols.remove(target_column_name)

    # user_id, item_idは正規化する必要がないため除外
    for col in ['user_id', 'item_id']:
        if col in continuous_cols:
            continuous_cols.remove(col)

    # 連値を0-1スケーリング
    if continuous_cols:
        scaler = MinMaxScaler()
        df[continuous_cols] = scaler.fit_transform(df[continuous_cols])

    for idx, row in df.iterrows():
        features = {}

        # カテゴリ変数
        for col in categorical_cols:
            val = row[col]
            if pd.notnull(val):
                features[f"{col}_{val}"] = 0.5

        # 連続値
        for col in continuous_cols:
            features[col] = row[col]
        id = row[target_column_name]

        result.append((id, features))
    return result

def process_df(df: pd.DataFrame, user_features: List[str], item_features: List[str]) -> Tuple[List[int], List[int], List[str], List[str]]:
    """
    Preprocess the input data for the recommender system.
    This function is a placeholder and should be implemented as needed.
    """

    df = df.copy()

    # 必要な７種の変数を用意する。
    all_user_ids = sorted(df['user_id'].unique())
    all_item_ids = sorted(df['item_id'].unique())


    unique_user_features_list = []

    for col in user_features:
        # NAN二も対応すべくuser_ageのような、target+カラム名のようなケースも考慮する。
        unique_user_features_list.append(f"{col}")
        unique_values = df[col].dropna().unique()
        for val in unique_values:
            unique_user_features_list.append(f"{col}_{val}")

    unique_item_features_list = []

    for col in item_features:
        # NAN二も対応すべくuser_ageのような、target+カラム名のようなケースも考慮する。
        unique_item_features_list.append(f"{col}")
        unique_values = df[col].dropna().unique()
        for val in unique_values:
            unique_item_features_list.append(f"{col}_{val}")

    # DataFrameからuser_idとitem_idのペアを作成。
    data: List[Tuple[int, int]] = list(zip(df['user_id'], df['item_id']))

    # ユーザー特徴量抽出
    user_df = df[user_features + ['user_id']]
    user_features_data = build_feature_data(user_df, 'user_id')

    # アイテム特徴量抽出
    item_df = df[item_features + ['item_id']]
    item_features_data = build_feature_data(item_df, 'item_id')

    dataset = Dataset()

    # 全てのユーザー、アイテムをリストアップ。
    dataset.fit(users=all_user_ids, items=all_item_ids, user_features=unique_user_features_list, item_features=unique_item_features_list)
    print(dataset)

    interactions, _ = dataset.build_interactions(data=data)
    print('interactions: ', interactions)

    user_features = dataset.build_user_features(user_features_data)
    item_features = dataset.build_item_features(item_features_data)

    return interactions, user_features, item_features, all_user_ids, all_item_ids

# DataFrameで結果を整理（オプション）
def create_recommendation_dataframe(user_recommendations):
    """
    推薦結果をDataFrameに変換
    """
    results = []
    for user_id, recommendations in user_recommendations.items():
        for rank, (item_id, score) in enumerate(recommendations, 1):
            results.append({
                'user_id': user_id,
                'rank': rank,
                'item_id': item_id,
                'score': score
            })
    return pd.DataFrame(results)

def create_ranking(fitted_model, all_user_ids, all_item_ids, top_k=10):
    """
    全ユーザーに対する推薦ランキングを作成
    """
    user_mesh, item_mesh = np.meshgrid(all_user_ids, all_item_ids, indexing='ij')

    # 一次元配列に変換
    input_user_ids = user_mesh.flatten()
    input_item_ids = item_mesh.flatten()
    # 予測スコアを取得
    scores = fitted_model.predict(user_ids=input_user_ids, item_ids=input_item_ids)

    # スコアを2次元配列に変換（ユーザー × アイテム）
    num_users = len(all_user_ids)
    num_items = len(all_item_ids)
    score_matrix = scores.reshape(num_users, num_items)

    print(f"Score matrix shape: {score_matrix.shape}")
    print(f"Users: {num_users}, Items: {num_items}")

    # 各ユーザーのトップK推薦を作成
    results = []
    for user_idx, user_id in enumerate(all_user_ids):
        user_scores = score_matrix[user_idx]
        # スコアの高い順にソート
        top_indices = np.argsort(user_scores)[::-1][:top_k]
        
        for rank, item_idx in enumerate(top_indices, 1):
            item_id = all_item_ids[item_idx]
            score = user_scores[item_idx]
            results.append({
                'user_id': user_id,
                'rank': rank,
                'item_id': item_id,
                'score': score
            })
    
    return pd.DataFrame(results)

def create_ranking_exclude_known(fitted_model, all_user_ids, all_item_ids, interactions_df, top_k=10):
    """
    全ユーザーに対する推薦ランキングを作成（既知アイテムを除外）
    """
    user_mesh, item_mesh = np.meshgrid(all_user_ids, all_item_ids, indexing='ij')

    # 一次元配列に変換
    input_user_ids = user_mesh.flatten()
    input_item_ids = item_mesh.flatten()
    # 予測スコアを取得
    scores = fitted_model.predict(user_ids=input_user_ids, item_ids=input_item_ids)

    # スコアを2次元配列に変換（ユーザー × アイテム）
    num_users = len(all_user_ids)
    num_items = len(all_item_ids)
    score_matrix = scores.reshape(num_users, num_items)

    # 既知のアイテムを取得
    known_items = {}
    for _, row in interactions_df.iterrows():
        user_id = row['user_id']
        item_id = row['item_id']
        if user_id not in known_items:
            known_items[user_id] = set()
        known_items[user_id].add(item_id)

    # 各ユーザーのトップK推薦を作成（既知アイテムを除外）
    results = []
    for user_idx, user_id in enumerate(all_user_ids):
        user_scores = score_matrix[user_idx]
        user_known_items = known_items.get(user_id, set())
        
        # 既知アイテムのスコアを除外
        filtered_scores = []
        filtered_item_ids = []
        for item_idx, item_id in enumerate(all_item_ids):
            if item_id not in user_known_items:
                filtered_scores.append(user_scores[item_idx])
                filtered_item_ids.append(item_id)
        
        if filtered_scores:
            # スコアの高い順にソート
            sorted_indices = np.argsort(filtered_scores)[::-1][:top_k]
            
            for rank, sorted_idx in enumerate(sorted_indices, 1):
                item_id = filtered_item_ids[sorted_idx]
                score = filtered_scores[sorted_idx]
                results.append({
                    'user_id': user_id,
                    'rank': rank,
                    'item_id': item_id,
                    'score': score
                })
    
    return pd.DataFrame(results)

def recommend(df: pd.DataFrame, user_features: List[str], item_features: List[str], 
              top_k: int = 10, exclude_known: bool = True) -> pd.DataFrame:
    """
    Generate recommendations for users based on their features and item features.
    
    Args:
        df: DataFrame containing user-item interactions and features
        user_features: List of user feature column names
        item_features: List of item feature column names
        top_k: Number of top recommendations per user
        exclude_known: Whether to exclude already known items
    
    Returns:
        DataFrame with columns: user_id, rank, item_id, score
    """
    df = df.copy()

    interactions, user_features_data, item_features_data, all_user_ids, all_item_ids = process_df(df, user_features, item_features)

    # モデルの作成
    model = LightFM(no_components=100, loss="warp", random_state=123)

    # 学習
    fitted_model = model.fit(interactions=interactions, user_features=user_features_data, item_features=item_features_data)

    if exclude_known:
        ranking_df = create_ranking_exclude_known(
            fitted_model=fitted_model, 
            all_user_ids=all_user_ids, 
            all_item_ids=all_item_ids,
            interactions_df=df,
            top_k=top_k
        )
    else:
        ranking_df = create_ranking(
            fitted_model=fitted_model, 
            all_user_ids=all_user_ids, 
            all_item_ids=all_item_ids,
            top_k=top_k
        )

    return ranking_df
