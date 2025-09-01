import re
import json
import requests
import pandas as pd
from tqdm import tqdm
from io import StringIO
from functools import reduce
from collections import defaultdict

# Function to Extract All Sessions Data
# --------------------------------------------------------------------------------------------------------------------------------
def get_all_sessions(client, CONGRESS_ID: str) -> pd.DataFrame:
    if not client:
        raise RuntimeError("No login session found. Please call login(env_path) first.")
        
    url = f"https://admin-portal.ferma.ai/congresses/{CONGRESS_ID}/sessions/download"
    response = requests.get(url, headers=client)
    if response.status_code == 200:
        try:
            df = pd.read_csv(StringIO(response.text), dtype={"tweets": str})
            return df
        except Exception as e:
            raise RuntimeError(f"Error parsing sessions CSV: {e}")
    else:
        raise RuntimeError(f"Failed to fetch sessions: HTTP {response.status_code}")


# Function to Extract Session Keywords Data
# --------------------------------------------------------------------------------------------------------------------------------
def get_skg(client, CONGRESS_ID: str) -> pd.DataFrame:
    if not client:
        raise RuntimeError("No login session found. Please call login(env_path) first.")
        
    url = f"https://admin-portal.ferma.ai/congresses/{CONGRESS_ID}/sessions/keywords/download?download_type=grouped"
    try:
        response = requests.get(url, headers=client)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df
        else:
            raise RuntimeError(f"Failed to fetch session keywords: HTTP {response.status_code}")
    except Exception as e:
        raise RuntimeError(f"Error fetching or parsing session keywords: {e}")


# Function to Extract Sessions - Full Abstracts Data
# --------------------------------------------------------------------------------------------------------------------------------
def get_fullabstracts(client, CONGRESS_ID: str) -> pd.DataFrame:
    if not client:
        raise RuntimeError("No login session found. Please call login(env_path) first.")
        
    url = f"https://admin-portal.ferma.ai/congresses/{CONGRESS_ID}/sessions/full_abstracts"
    try:
        response = requests.get(url, headers=client)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df
        else:
            raise RuntimeError(f"Failed to fetch session keywords: HTTP {response.status_code}")
    except Exception as e:
        raise RuntimeError(f"Error fetching or parsing session full abstracts: {e}")


# Function to Extract Session Keywords Data
# --------------------------------------------------------------------------------------------------------------------------------
def get_summary(client, CONGRESS_ID: str) -> pd.DataFrame:
    if not client:
        raise RuntimeError("No login session found. Please call login(env_path) first.")
        
    url = f"https://admin-portal.ferma.ai/congresses/{CONGRESS_ID}/sessions/v1_summary?status=1"
    try:
        response = requests.get(url, headers=client)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df
        else:
            raise RuntimeError(f"Failed to fetch session keywords: HTTP {response.status_code}")
    except Exception as e:
        raise RuntimeError(f"Error fetching or parsing session summary: {e}")


# Function to Extract Session - Tweets Data
# --------------------------------------------------------------------------------------------------------------------------------
def get_tweets(client, CONGRESS_ID: str) -> pd.DataFrame:
    if not client:
        raise RuntimeError("No login session found. Please call login(env_path) first.")
        
    url = f"https://admin-portal.ferma.ai/congresses/{CONGRESS_ID}/tweets/download"
    try:
        response = requests.get(url, headers=client)
        if response.status_code == 200:
            tweets_df = pd.read_csv(StringIO(response.text))
            sessions_metadata_df = get_all_sessions(client, CONGRESS_ID)
            
            tweets_df['session_buzz_scores'] = tweets_df['session_buzz_scores'].apply(lambda x: json.loads(x.replace("'", '"')) if isinstance(x, str) else [])
            tweets_df = tweets_df.explode('session_buzz_scores')
            tweets_df['buzz_score'] = tweets_df['session_buzz_scores'].apply(lambda x: x.get('buzz_score') if isinstance(x, dict) else None)
            tweets_df['session_id'] = tweets_df['session_buzz_scores'].apply(lambda x: x.get('session_id') if isinstance(x, dict) else None)
            tweets_df = tweets_df.drop(columns=['session_buzz_scores', 'session_ids'])
            tweets_df = tweets_df.sort_values(by='session_id').reset_index(drop=True)
            tweets_df['tweet_id'] = tweets_df['tweet_url'].str.extract(r'/status/(\d+)')
            tweets_df = tweets_df.merge(sessions_metadata_df[['session_id', 'internal_id', 'session_title', 'abstract_title']], on='session_id', how='left')
            
            tweets_df = tweets_df[['internal_id', 'session_id', 'session_title', 'abstract_title', 'tweet_id', 'tweet_url', 'text', 'created_at',
                'retweet_count', 'reply_count', 'like_count', 'view_count', 'user_name', 'user_description', 'followers_count',
                'following_count', 'location', 'buzz_score']]

            tweets_df = tweets_df.rename(columns={'internal_id': 'Internal ID', 'session_id': 'Session ID', 'session_title': 'Session Title',
                            'abstract_title': 'Abstract Title', 'tweet_id': 'Tweet ID', 'tweet_url': 'Tweet URL', 'text': 'Tweet Text', 'created_at': 'Date of Posting',
                            'retweet_count': 'Retweet Count', 'reply_count': 'Reply Count', 'like_count': 'Like Count', 'view_count': 'View Count',
                            'user_name': 'User Name', 'user_description': 'User Description', 'followers_count': 'Followers Count', 'following_count': 'Following Count',
                            'location': 'Location', 'buzz_score': 'Buzz Score'})
            
            priority_df = get_priority(client, CONGRESS_ID)
            
            columns_to_remove = {'internal_id', 'abstract_id', 'session_title', 'session_type', 'abstract_title', 'authors', 'classification', 'location',
                                'start_date','end_date', 'Filename', 'Combined Priority', 'Teams'}
            
            priority_df = priority_df[[col for col in priority_df.columns if col not in columns_to_remove and 'Combined' not in col]]

            tweets_df = tweets_df.merge(priority_df, how='left', left_on='Session ID', right_on='session_id')
            tweets_df = tweets_df.drop(columns=['session_id'])
            return tweets_df
        
        else:
            raise RuntimeError(f"Failed to fetch session keywords: HTTP {response.status_code}")
    except Exception as e:
        raise RuntimeError(f"Error fetching or parsing session tweets: {e}")

# Function to Extract All Client's Priority Data
# --------------------------------------------------------------------------------------------------------------------------------
def get_priority(client, CONGRESS_ID: str, include=None, exclude=None) -> pd.DataFrame:
    if not client:
        raise RuntimeError("No login session found. Please call login(env_path) first.")
    
    # 1 Extracting All Sessions Data for additional columns
    # ----------------------------------------------------------------
    sessions_metadata_df = get_all_sessions(client, CONGRESS_ID)
    
    
    # 2 Extracting the list of planners
    # ----------------------------------------------------------------
    url = f"https://admin-portal.ferma.ai/congresses/{CONGRESS_ID}?include=planners"
    response = requests.get(url, headers=client)
    if response.status_code == 200:
        planners = response.json().get('data', {}).get('planners', [])
        if not planners:
            raise RuntimeError("No Priority Planners Found")
    else:
        raise RuntimeError(f"Failed to fetch planners: {response.status_code}")
        
    planner_df = pd.json_normalize(planners)
    planner_df['link'] = planner_df['id'].apply(lambda pid: f'https://admin-portal.ferma.ai/planners/{pid}/download?download_type=all')
    
    
    #3 Processing Include/Exclude Lists
    # ------------------------------------------------------------------------------------------------------------
    include_normalized = [item.strip().lower() for item in include] if include else None
    
    # Always exclude 'zoomrx'
    if exclude is None:
        exclude = ['ZoomRx', 'congress-insights']
    else:
        normalized = [e.strip().lower() for e in exclude]
        if 'zoomrx' not in normalized:
            exclude.append('ZoomRx')
        if 'congress-insights' not in normalized:
            exclude.append('Congress')
            
    exclude_normalized = [item.strip().lower() for item in exclude] if exclude else None

    # 4 Defning the priority mapping and Inverse mapping
    # ------------------------------------------------------------------------------------------------------------
    PRIORITY_MAP = {"Very High": 1, "High": 2, "Internal": 3, "Medium": 4, "Low": 5, "Not Relevant": 6}
    REVERSE_PRIORITY_MAP = {v: k for k, v in PRIORITY_MAP.items()}
    
    
    # 5. Download and parse each planner file, applying include/exclude filters
    # ------------------------------------------------------------------------------------------------------------
    planner_priority_dfs = []

    for _, row in tqdm(planner_df.iterrows(), total=len(planner_df), desc="Planners"):
        tenant_name = row['tenantName']
        tenant_normalized = tenant_name.strip().lower()

        # Filtering logic (comparison only)
        if include_normalized and tenant_normalized not in include_normalized:
            continue
        if exclude_normalized and tenant_normalized in exclude_normalized:
            continue

        priority_column_name = f"{tenant_name} - {row['teamName']}"
        try:
            planner_file_response = requests.get(row['link'], headers=client)
            planner_file_response.raise_for_status()
        except Exception as e:
            print(f"Skipping planner {priority_column_name} due to download error: {e}")
            continue

        try:
            priority_df = pd.read_csv(
                StringIO(planner_file_response.text),
                usecols=['internal_id', 'abstract_title', 'priority_name']
            )
            priority_df = priority_df.rename(columns={'priority_name': priority_column_name})
            planner_priority_dfs.append(priority_df)
        except Exception as e:
            print(f"Skipping planner {priority_column_name} due to CSV parsing error: {e}")
            continue

    if not planner_priority_dfs:
        raise RuntimeError("No planner data was successfully downloaded or parsed.")

    # 6. Merge all planners' priority data into one dataframe by internal_id and abstract_title
    # ------------------------------------------------------------------------------------------------------------
    combined_priority_df = reduce(
        lambda left, right: pd.merge(left, right, on=['internal_id', 'abstract_title'], how='outer'),
        planner_priority_dfs
    )

    # 7. Compute combined priority by mapping to numeric values and selecting the minimum
    # ------------------------------------------------------------------------------------------------------------
    priority_columns = [col for col in combined_priority_df.columns if col not in ['internal_id', 'abstract_title']]
    for column in priority_columns:
        combined_priority_df[column + '_num'] = combined_priority_df[column].map(PRIORITY_MAP)

    numeric_priority_columns = [col + '_num' for col in priority_columns]
    combined_priority_df['combined_priority_num'] = combined_priority_df[numeric_priority_columns].min(axis=1)
    combined_priority_df['Combined Priority'] = combined_priority_df['combined_priority_num'].map(REVERSE_PRIORITY_MAP)
    
    # 7b. Compute client-level combined priorities
    # ------------------------------------------------------------------------------------------------------------

    tenant_to_columns = defaultdict(list)
    for col in priority_columns:
        tenant = col.split(" - ")[0].strip()
        tenant_to_columns[tenant].append(col)

    for tenant, cols in tenant_to_columns.items():
        numeric_cols = [col + '_num' for col in cols]
        combined_col_name = f"{tenant} - Combined Priority"
        combined_priority_df[f"{tenant}_combined_priority_num"] = combined_priority_df[numeric_cols].min(axis=1)
        combined_priority_df[combined_col_name] = combined_priority_df[f"{tenant}_combined_priority_num"].map(REVERSE_PRIORITY_MAP)
    
    # 8. Determine which teams agree on the selected combined priority
    # ------------------------------------------------------------------------------------------------------------
    def compute_team_match(row):
        matched_columns = [
            col for col, num_col in zip(priority_columns, numeric_priority_columns)
            if row[num_col] == row['combined_priority_num']
        ]
        return "All Teams" if len(matched_columns) == len(priority_columns) else ', '.join(matched_columns)

    combined_priority_df['Teams'] = combined_priority_df.apply(compute_team_match, axis=1)
    combined_priority_df.drop(
        columns=numeric_priority_columns + ['combined_priority_num'] +
        [f"{tenant}_combined_priority_num" for tenant in tenant_to_columns], inplace=True
        )

    # 9. Merge session-level metadata to enrich the final output
    # ------------------------------------------------------------------------------------------------------------
    session_columns_needed = [
        'internal_id', 'session_id', 'abstract_id', 'session_title', 'session_type', 'authors',
        'classification', 'location', 'start_date', 'end_date'
    ]
    sessions_metadata_df = sessions_metadata_df[session_columns_needed].drop_duplicates()
    sessions_metadata_df['start_date'] = pd.to_datetime(sessions_metadata_df['start_date'])
    sessions_metadata_df['end_date'] = pd.to_datetime(sessions_metadata_df['end_date'])
    final_df = pd.merge(combined_priority_df, sessions_metadata_df, on='internal_id', how='left')
    final_df['Filename'] = final_df.apply(lambda row: f"{row['session_id']}_{re.sub(r'[^A-Za-z0-9 ]+', '', str(row['abstract_title'])).strip()[:20].replace(' ', '').strip()}",axis=1)

    # 10. Set final column order for clean output
    # ------------------------------------------------------------------------------------------------------------
    fixed_columns = [
        'internal_id', 'session_id', 'abstract_id', 'session_title', 'session_type', 'abstract_title', 'authors', 
        'classification', 'location', 'start_date', 'end_date', 'Filename', 'Combined Priority', 'Teams'
    ]

    # Organize by client: first their combined priority, then their team columns
    client_priority_columns = []
    for tenant in sorted(tenant_to_columns):  # Optional: sort for consistent order
        client_combined = f"{tenant} - Combined Priority"
        team_columns = tenant_to_columns[tenant]
        client_priority_columns.extend([client_combined] + team_columns)

    # Remaining columns not already accounted for
    already_included = set(fixed_columns + client_priority_columns)
    remaining_columns = [col for col in final_df.columns if col not in already_included]

    # Final column ordering
    ordered_columns = fixed_columns + client_priority_columns + remaining_columns

    return final_df[ordered_columns]