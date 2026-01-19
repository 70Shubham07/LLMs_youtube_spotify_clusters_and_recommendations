_Note: This README was generated with help from GitHub Copilot and manually audited for accuracy._

# ETL Notebooks Overview

This README explains, in simple bullet points, what each notebook does in the ETL pipeline.

## 00_iterate_kaggle_and_scrape_comments.ipynb
- Reads settings from `parameters_file.json` (input CSV path, API key, start index, limits).
- Builds a YouTube Data API client and loads `Spotify_Youtube.csv` mapping.
- Loops through songs, extracts Spotify and YouTube IDs from the mapping file.
- Fetches top-level YouTube comments per video (paginates until the configured limit).
- Handles disabled comments and API errors; records any failures separately.
- Sorts comments by likes and keeps the top ones for each video.
- Saves curated comments to CSV (e.g., `spotify_youtube_comment_88247.csv`).

## 01_merging_the_datasets.ipynb
- Loads prepared CSVs (e.g., Spotify attributes, YouTube comments, mappings).
- Cleans and normalizes key columns (IDs, names, and basic types).
- Joins datasets on common identifiers (Spotify or YouTube IDs).
- Resolves duplicates/conflicts and keeps relevant columns.
- Exports a combined dataset for downstream steps (e.g., `merged_df.csv`).

## 02_create_comment_classes_refined_1.ipynb
- Loads the YouTube comments dataset.
- Cleans and preprocesses comment text (lowercasing, punctuation removal, etc.).
- Builds text features (e.g., token counts or n-grams) for categorization.
- Applies refined rules or models to assign one or more categories to each comment.
- Produces labeled/Indexed outputs:
  - `df_indexed.csv`: comments with category columns/indices.
  - `index_comment_categories_recent.csv`: mapping of category ids/names.

## 02b_create_lyric_classes_refined_2.ipynb (Supplemental)
- Loads song lyrics and related metadata (e.g., `songs_with_attributes_and_lyrics[1].csv`).
- Cleans and preprocesses lyric text.
- Builds features and applies refined labeling logic for lyric categories.
- Outputs:
  - `df_indexed_lyric.csv`: lyrics with category indices.
  - `index_lyric_categories_recent.csv`: mapping of lyric category ids/names.

## 03_final_structure_cleaning.ipynb
- Loads intermediate outputs (merged data, comment and lyric label indices).
- Merges labels back into the combined dataset.
- Drops unused columns, fixes types, and removes duplicates.
- Standardizes final column names and structure for analytics/ML.
- Saves the final cleaned dataset(s) for use in modeling or reporting.

## Notes
- Source inputs commonly used: `Spotify_Youtube.csv`, curated comment CSV(s), and lyric CSV(s).
- Outputs are listed in the `etl__/` folder (e.g., `merged_df.csv`, `df_indexed.csv`, `df_indexed_lyric.csv`).
- Exact variable names and limits (e.g., `MAX_COMMENTS_PER_VIDEO`) are configured via `parameters_file.json` in notebook 00.

## ml_stuff/clustering_comments.ipynb
- Load the aggregated dataset (`df_final_aggregated.csv`) that includes comment-category features per track.
- Select comment feature columns (e.g., Humor/Memes, Appreciation/Praise, Words of empathy, Personal Stories/Experiences).
- Scale features using `StandardScaler` to normalize different ranges.
- Explore cluster counts with a dendrogram (hierarchical linkage) and silhouette scores.
- Cluster records using Agglomerative (hierarchical) clustering (tested with 3–4 clusters).
- Visualize clusters with t-SNE scatter, parallel coordinates, and boxplots to understand feature distributions.
- Attach `spotify_id` to clustered rows and save results to `x_scaled_df_comments.csv`.
- Persist the fitted scaler to `scaler_comments.pkl` for consistent later use.
- Provide simple, human-readable observations describing what each cluster emphasizes (e.g., humor-heavy, empathy/personal-story heavy, low all-around).

## ml_stuff/clustering_spotify.ipynb
- Load the aggregated dataset (`df_final_aggregated.csv`) that includes Spotify audio features per track.
- Select Spotify feature columns: Danceability, Energy, Key, Loudness, Speechiness, Acousticness, Instrumentalness, Liveness, Valence, Tempo, Duration_ms.
- Scale features using `StandardScaler` so all attributes are on comparable scales.
- Explore cluster counts via KMeans elbow (WCSS) and silhouette scores; optionally compare with hierarchical (Agglomerative) clustering.
- Fit KMeans with the chosen `optimal_k`, assign labels, and examine centroids.
- Visualize clusters using t-SNE scatter, parallel coordinates, pairplots, and per-feature boxplots to interpret differences.
- Attach `spotify_id` to clustered rows and save the scaled+labeled DataFrame to `x_scaled_df_spotify.csv`.
- Persist the fitted scaler to `scaler_spotify.pkl`; save illustrative figures (e.g., `cluster_distribution_spotify_features.jpg`).
- Summarize clusters in plain language (e.g., high-energy/danceable, acoustic/low-energy, speechiness-heavy) to aid downstream recommendations.

## ml_stuff/merging_the_two_clusters_and_recommending.ipynb
- Purpose: suggest songs that match the target’s “comment vibe” and audio profile.
- Inputs: use the scaled frames `x_scaled_df_comments.csv` and `x_scaled_df_spotify.csv`, plus the saved scalers `scaler_comments.pkl` and `scaler_spotify.pkl` to keep feature scaling consistent.
- Pick a target:
  - If targeting a specific song, take its row from both frames (by `spotify_id`).
  - If using a user-defined profile, create a small record of desired comment-category levels and audio features, then transform it with the same scalers.
- Prepare features: choose the comment-category columns for the “vibe” space and the Spotify audio attributes for the “sound” space; ensure column order matches the dataset.
- Compute similarity:
  - Calculate Euclidean distance from the target to every item in the comment space.
  - Calculate Euclidean distance from the target to every item in the audio space.
  - Normalize distances (e.g., min–max to 0–1) so both spaces contribute fairly.
- Combine signals:
  - Weighted sum of normalized distances (example: 0.6 comments + 0.4 audio).
  - Optional penalty if cluster labels differ greatly (encourages cluster-consistent results).
- Rank and select:
  - Sort by the combined score (lower = closer) and pick top N (e.g., 10).
  - Exclude the target itself; optionally cap by artist to keep diversity.
- Enrich output: attach `spotify_id`, title/artist, comment/audio cluster labels, per-space distances, and the combined score.
- Save and review: export a recommendations table for inspection and downstream use; add short, human-readable notes (why it fits: similar empathy-heavy comments + medium energy/valence).

## ml_stuff/ml_multi_class_multi_label.ipynb — Multi-Label Classification
- **Goal:** Predict multiple comment categories per song (multi-label: more than one label can be 1 for the same sample).
- **Inputs (features):**
  - Spotify audio attributes: Danceability, Energy, Key, Loudness, Speechiness, Acousticness, Instrumentalness, Liveness, Valence, Tempo, Duration_ms (scaled with StandardScaler).
  - Lyric category signals: themes such as Love/Relationships, Self-Reflection, Social/Political, Celebration/Fun, Philosophical, Storytelling, Escape/Fantasy, Spiritual, Cultural/Lifestyle, Fun/Humor.
- **Targets (labels):**
  - Comment categories: Humor/Memes; Appreciation/Praise; Words of empathy; Personal Stories/Experiences.
  - Labels are binarized by thresholding each column at its median (0/1).
- **Algorithm:**
  - Binary relevance via `MultiOutputClassifier` (one classifier per label, trained independently).
  - Base learners tried: `RandomForestClassifier`, `GradientBoostingClassifier`, `xgboost.XGBClassifier` (with `GridSearchCV` for GB/XGB).
  - Train/test split: `train_test_split(..., test_size=0.2, random_state=42)`.
- **Outputs:**
  - Per-sample 4-length binary vector indicating presence/absence of each comment category.
- **Metrics reported:**
  - Subset Accuracy (exact match): percentage of samples where all predicted labels equal all true labels.
  - Micro F1-Score: aggregates TP/FP/FN across all labels and samples, then computes F1.
    - Precision_micro = ΣTP / (ΣTP + ΣFP)
    - Recall_micro = ΣTP / (ΣTP + ΣFN)
    - F1_micro = 2·ΣTP / (2·ΣTP + ΣFP + ΣFN)
- **Interpretation tips:**
  - Subset accuracy is strict; with 4 labels, moderate values are common.
  - Micro F1 highlights overall decision quality across all label predictions, favoring frequent labels.
  - Consider also Macro/Weighted F1 to monitor rare-label performance.
- **Notes:**
  - If models output probabilities, tune per-label decision thresholds (not only 0.5) to improve Micro F1.
  - Keep feature scaling consistent with `StandardScaler` fitted on training data.
