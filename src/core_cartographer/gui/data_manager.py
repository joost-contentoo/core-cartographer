"""Data management for the Streamlit GUI.

This module handles file data processing, language detection,
and translation pair matching for the GUI.
"""

import sys
from pathlib import Path

import pandas as pd

# Handle imports for both direct execution and package import
try:
    from ..file_utils import (
        detect_language,
        extract_language_from_filename,
        find_base_name,
        find_translation_pair,
    )
    from ..logging_config import get_logger
except ImportError:
    # Running directly with streamlit, add parent to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core_cartographer.file_utils import (
        detect_language,
        extract_language_from_filename,
        find_base_name,
        find_translation_pair,
    )
    from core_cartographer.logging_config import get_logger

logger = get_logger(__name__)


def create_file_dataframe(
    file_data: dict[str, str],
    subtypes: list[str],
) -> pd.DataFrame:
    """
    Create initial dataframe from uploaded files.

    Args:
        file_data: Dictionary mapping filenames to content.
        subtypes: List of available subtypes.

    Returns:
        DataFrame with columns: ❌, Filename, Subtype, Language, Pair #
    """
    default_subtype = subtypes[0] if subtypes else "general"

    data = {
        "❌": [False] * len(file_data),
        "Filename": list(file_data.keys()),
        "Subtype": [default_subtype] * len(file_data),
        "Language": [""] * len(file_data),
        "Pair #": ["-"] * len(file_data),
    }
    return pd.DataFrame(data)


def detect_languages(df: pd.DataFrame, file_data: dict[str, str]) -> pd.DataFrame:
    """
    Detect languages for all files in the dataframe.

    Args:
        df: The file dataframe.
        file_data: Dictionary mapping filenames to content.

    Returns:
        Updated dataframe with Language column populated.
    """
    df = df.copy()

    for idx, row in df.iterrows():
        filename = row["Filename"]
        content = file_data.get(filename, "")

        # Try filename first, fall back to content detection
        lang_from_file = extract_language_from_filename(filename)
        if lang_from_file:
            df.at[idx, "Language"] = lang_from_file
            logger.debug(f"Detected language {lang_from_file} from filename: {filename}")
        else:
            detected = detect_language(content)
            df.at[idx, "Language"] = detected
            logger.debug(f"Detected language {detected} from content: {filename}")

    return df


def find_pairs(df: pd.DataFrame, file_data: dict[str, str]) -> pd.DataFrame:
    """
    Auto-detect translation pairs based on filename similarity and content.

    Args:
        df: The file dataframe with Language column populated.
        file_data: Dictionary mapping filenames to content.

    Returns:
        Updated dataframe with Pair # column populated.
    """
    df = df.copy()
    df["base_name"] = df["Filename"].apply(find_base_name)

    pair_number = 1
    processed: set[str] = set()

    for idx, row in df.iterrows():
        filename = row["Filename"]
        if filename in processed:
            continue

        language = row["Language"]

        # Skip files with unknown language
        if language == "UNKNOWN":
            df.loc[idx, "Pair #"] = "-"
            processed.add(filename)
            logger.debug(f"Skipping unknown language file: {filename}")
            continue

        # Find candidates (different language, not yet processed)
        candidates_df = df[
            (~df["Filename"].isin(processed))
            & (df["Filename"] != filename)
            & (df["Language"] != language)
            & (df["Language"] != "UNKNOWN")
        ]

        if len(candidates_df) == 0:
            df.loc[idx, "Pair #"] = "-"
            processed.add(filename)
            continue

        # Build candidate list
        candidates = [
            (r["Filename"], r["Language"], r["base_name"])
            for _, r in candidates_df.iterrows()
        ]

        # Find best match
        match = find_translation_pair(filename, language, candidates, file_data)

        if match:
            df.loc[df["Filename"] == filename, "Pair #"] = str(pair_number)
            df.loc[df["Filename"] == match, "Pair #"] = str(pair_number)
            processed.add(filename)
            processed.add(match)
            logger.info(f"Paired: {filename} <-> {match} (pair {pair_number})")
            pair_number += 1
        else:
            df.loc[idx, "Pair #"] = "-"
            processed.add(filename)

    return df.drop(columns=["base_name"])


def sort_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort dataframe: paired files together, then alphabetically.

    Args:
        df: The file dataframe.

    Returns:
        Sorted dataframe.
    """
    df = df.copy()

    def sort_key(row: pd.Series) -> tuple:
        pair = row["Pair #"]
        if pair == "-":
            return (999999, row["Filename"])
        try:
            pair_int = int(pair)
        except (ValueError, TypeError):
            pair_int = 999999
        return (pair_int, row["Filename"])

    df["sort_key"] = df.apply(sort_key, axis=1)
    df = df.sort_values("sort_key").reset_index(drop=True)
    return df.drop(columns=["sort_key"])


def auto_detect_all(
    file_data: dict[str, str],
    subtypes: list[str],
) -> pd.DataFrame:
    """
    Run full auto-detection pipeline on all files.

    This creates a dataframe, detects languages, finds pairs,
    and sorts the result.

    Args:
        file_data: Dictionary mapping filenames to content.
        subtypes: List of available subtypes.

    Returns:
        Fully processed and sorted dataframe.
    """
    logger.info(f"Running auto-detection on {len(file_data)} files")

    df = create_file_dataframe(file_data, subtypes)
    df = detect_languages(df, file_data)
    df = find_pairs(df, file_data)
    df = sort_dataframe(df)

    paired_count = len(df[df["Pair #"] != "-"])
    logger.info(f"Auto-detection complete: {paired_count} files paired")

    return df


def get_colored_subtype_options(subtypes: list[str]) -> dict[str, str]:
    """
    Create colored subtype options for the data editor.

    Args:
        subtypes: List of subtype names.

    Returns:
        Dictionary mapping display name (with color) to actual value.
    """
    from .components import get_subtype_color

    return {
        f"{get_subtype_color(s, subtypes)} {s}": s
        for s in subtypes
    }


def apply_colored_subtypes(df: pd.DataFrame, subtypes: list[str]) -> pd.DataFrame:
    """
    Convert subtype column to display format with colors.

    Args:
        df: The file dataframe.
        subtypes: List of all subtypes.

    Returns:
        DataFrame with colored subtype display names.
    """
    from .components import get_subtype_color

    df = df.copy()
    df["Subtype"] = df["Subtype"].apply(
        lambda x: f"{get_subtype_color(x, subtypes)} {x}"
    )
    return df


def extract_subtypes_from_display(
    df: pd.DataFrame,
    colored_options: dict[str, str],
) -> pd.DataFrame:
    """
    Convert colored display subtypes back to actual values.

    Args:
        df: DataFrame with colored subtype names.
        colored_options: Mapping from display to actual values.

    Returns:
        DataFrame with actual subtype values.
    """
    df = df.copy()
    df["Subtype"] = df["Subtype"].apply(
        lambda x: colored_options.get(x, x.split(" ", 1)[-1] if " " in x else x)
    )
    return df
