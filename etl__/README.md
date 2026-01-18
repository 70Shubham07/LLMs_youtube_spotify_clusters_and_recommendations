# ETL Notebooks Overview (00–03)

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
