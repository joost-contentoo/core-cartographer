"""Streamlit GUI for Core Cartographer."""

import re
import sys
import tempfile
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st
from langdetect import detect, LangDetectException

# Handle imports for both direct execution and package import
try:
    from . import __version__
    from .config import get_settings
    from .extractor import extract_rules_and_guidelines, DocumentSet
    from .parser import parse_document, SUPPORTED_EXTENSIONS
    from .cost_estimator import count_tokens, estimate_cost, format_cost, format_tokens
except ImportError:
    # Running directly with streamlit, add parent to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core_cartographer import __version__
    from core_cartographer.config import get_settings
    from core_cartographer.extractor import extract_rules_and_guidelines, DocumentSet
    from core_cartographer.parser import parse_document, SUPPORTED_EXTENSIONS
    from core_cartographer.cost_estimator import (
        count_tokens,
        estimate_cost,
        format_cost,
        format_tokens,
    )


def detect_language(text: str) -> str:
    """Detect language from text content."""
    try:
        # Take first 1000 chars for detection (faster and usually sufficient)
        sample = text[:1000]
        lang_code = detect(sample)
        # Convert to uppercase for consistency (en -> EN, de -> DE)
        return lang_code.upper()
    except LangDetectException:
        return "UNKNOWN"


def extract_language_from_filename(filename: str) -> Optional[str]:
    """Extract language code from filename (e.g., card_EN.txt -> EN)."""
    # Common patterns: _EN, _DE, -EN, -DE, (EN), (DE), etc.
    pattern = r"[_\-\(\[]([A-Z]{2})[_\-\)\]]"
    match = re.search(pattern, filename.upper())
    if match:
        return match.group(1)
    return None


def find_base_name(filename: str) -> str:
    """Extract base name without language code and extension."""
    # Remove extension
    name = Path(filename).stem

    # Remove common language patterns
    name = re.sub(r"[_\-\(\[]([A-Z]{2})[_\-\)\]]", "", name, flags=re.IGNORECASE)

    # Clean up double separators
    name = re.sub(r"[_\-]{2,}", "_", name)
    name = name.strip("_-")

    return name


def find_pairs_by_filename(df: pd.DataFrame) -> pd.DataFrame:
    """Auto-detect paired files based on filename similarity."""
    df = df.copy()

    # Extract base names for each file
    df["base_name"] = df["Filename"].apply(find_base_name)

    # For each file, find potential pairs with same base name but different language
    for idx, row in df.iterrows():
        if pd.isna(row["Paired with"]) or row["Paired with"] == "":
            # Find files with same base name but different language
            same_base = df[
                (df["base_name"] == row["base_name"])
                & (df["Filename"] != row["Filename"])
                & (df["Language"] != row["Language"])
                & (df["Language"] != "UNKNOWN")
                & (row["Language"] != "UNKNOWN")
            ]

            if len(same_base) > 0:
                # Pair with first match
                paired_file = same_base.iloc[0]["Filename"]
                df.at[idx, "Paired with"] = paired_file

    # Remove helper column
    df = df.drop(columns=["base_name"])

    return df


def detect_translation_direction(file1_content: str, file2_content: str, lang1: str, lang2: str) -> str:
    """
    Detect translation direction based on content length and common patterns.
    Returns format like "EN → DE" or "DE → EN".
    """
    len1 = len(file1_content)
    len2 = len(file2_content)

    # Heuristic: English is often source language in localization
    if lang1 == "EN" and lang2 != "EN":
        return f"{lang1} → {lang2}"
    elif lang2 == "EN" and lang1 != "EN":
        return f"{lang2} → {lang1}"

    # Heuristic: Longer text is often the source (target may be condensed)
    if len1 > len2 * 1.1:  # 10% threshold
        return f"{lang1} → {lang2}"
    elif len2 > len1 * 1.1:
        return f"{lang2} → {lang1}"

    # Default: alphabetical
    if lang1 < lang2:
        return f"{lang1} → {lang2}"
    else:
        return f"{lang2} → {lang1}"


def sort_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort dataframe: paired files together, then alphabetically.
    """
    df = df.copy()

    # Create a sort key that groups pairs together
    df["sort_key"] = ""
    processed = set()

    for idx, row in df.iterrows():
        if row["Filename"] in processed:
            continue

        if row["Paired with"] and row["Paired with"] != "":
            # This file has a pair - create a group key
            pair_files = sorted([row["Filename"], row["Paired with"]])
            group_key = pair_files[0]  # Use first alphabetically as group key

            # Assign same sort key to both files
            df.loc[df["Filename"] == row["Filename"], "sort_key"] = group_key
            df.loc[df["Filename"] == row["Paired with"], "sort_key"] = group_key

            processed.add(row["Filename"])
            processed.add(row["Paired with"])
        else:
            # No pair - use filename as sort key
            df.loc[idx, "sort_key"] = row["Filename"]
            processed.add(row["Filename"])

    # Sort by sort_key, then by filename
    df = df.sort_values(["sort_key", "Filename"]).reset_index(drop=True)
    df = df.drop(columns=["sort_key"])

    return df


def auto_detect_all(file_data: dict) -> pd.DataFrame:
    """Run auto-detection on all files and return dataframe."""
    # Initialize dataframe
    data = {
        "Delete": [False] * len(file_data),
        "Filename": list(file_data.keys()),
        "Subtype": [""] * len(file_data),
        "Language": [""] * len(file_data),
        "Paired with": [""] * len(file_data),
        "Direction": [""] * len(file_data),
    }
    df = pd.DataFrame(data)

    # Detect languages
    for idx, row in df.iterrows():
        content = file_data[row["Filename"]]

        # Try filename first
        lang_from_file = extract_language_from_filename(row["Filename"])
        if lang_from_file:
            df.at[idx, "Language"] = lang_from_file
        else:
            # Detect from content
            detected = detect_language(content)
            df.at[idx, "Language"] = detected

    # Find pairs
    df = find_pairs_by_filename(df)

    # Detect directions for pairs
    for idx, row in df.iterrows():
        if row["Paired with"] and row["Paired with"] != "":
            paired_row = df[df["Filename"] == row["Paired with"]]
            if len(paired_row) > 0:
                content1 = file_data[row["Filename"]]
                content2 = file_data[row["Paired with"]]
                direction = detect_translation_direction(
                    content1, content2, row["Language"], paired_row.iloc[0]["Language"]
                )
                df.at[idx, "Direction"] = direction

    # Sort the dataframe
    df = sort_dataframe(df)

    return df


def main() -> None:
    """Main entry point for the Streamlit GUI."""
    st.set_page_config(
        page_title="Core Cartographer",
        page_icon="🗺️",
        layout="wide",
    )

    st.title(f"🗺️ Core Cartographer v{__version__}")
    st.markdown("Extract **validation rules** and **localization guidelines** from copy documents")

    # Load settings
    try:
        settings = get_settings()
    except Exception as e:
        st.error(f"⚠️ Configuration error: {e}")
        st.info("Make sure you have a `.env` file with `ANTHROPIC_API_KEY` set.")
        st.stop()

    # Initialize session state
    if "file_data" not in st.session_state:
        st.session_state.file_data = {}  # {filename: content}
    if "df" not in st.session_state:
        st.session_state.df = None
    if "all_subtypes" not in st.session_state:
        st.session_state.all_subtypes = ["gift_cards", "game_cards", "payment_cards"]

    # Sidebar: Client name
    with st.sidebar:
        st.header("⚙️ Configuration")

        client_name = st.text_input(
            "Client Name",
            value=st.session_state.get("client_name", ""),
            placeholder="e.g., dundle, acme",
            help="Name of the client for this extraction",
        )

        if client_name:
            st.session_state.client_name = client_name

        st.divider()
        st.markdown(f"**Model:** {settings.model}")
        st.markdown(f"**Supported:** {', '.join(SUPPORTED_EXTENSIONS)}")

    # Step 1: File Upload
    st.header("📤 Step 1: Upload Documents")

    uploaded_files = st.file_uploader(
        "Upload all documents to analyze",
        type=list(ext.replace(".", "") for ext in SUPPORTED_EXTENSIONS),
        accept_multiple_files=True,
        help="Select all files at once",
    )

    if uploaded_files:
        # Parse and store new files
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.file_data:
                # Save to temp and parse
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = Path(tmp.name)

                try:
                    content = parse_document(tmp_path)
                    st.session_state.file_data[uploaded_file.name] = content
                except Exception as e:
                    st.warning(f"⚠️ Failed to parse {uploaded_file.name}: {e}")
                finally:
                    tmp_path.unlink()

        st.success(f"✓ {len(st.session_state.file_data)} document(s) uploaded")

        # Show list of uploaded files
        with st.expander("📄 View uploaded files"):
            for filename in sorted(st.session_state.file_data.keys()):
                tokens = count_tokens(st.session_state.file_data[filename])
                st.markdown(f"- {filename} — {format_tokens(tokens)}")

    if not st.session_state.file_data:
        st.info("👆 Upload documents to continue")
        st.stop()

    # Automatically move to step 2 - run auto-detection if not done yet
    if st.session_state.df is None:
        with st.spinner("🔍 Auto-detecting languages and finding pairs..."):
            st.session_state.df = auto_detect_all(st.session_state.file_data)

    # Step 2: Edit table
    st.header("📋 Step 2: Label & Review Documents")

    st.markdown("**Instructions:**")
    st.markdown("- Language and paired files are auto-detected")
    st.markdown("- Add **Subtype** labels to group files for extraction")
    st.markdown("- Edit any fields if auto-detection is incorrect")
    st.markdown("- Check **❌ Delete** to remove unwanted files")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🔄 Re-run Auto-detection", use_container_width=True):
            with st.spinner("Detecting..."):
                st.session_state.df = auto_detect_all(st.session_state.file_data)
                st.success("✓ Auto-detection complete!")
                st.rerun()

    with col2:
        if st.button("🗑️ Clear All Labels", use_container_width=True):
            st.session_state.df["Subtype"] = ""
            st.session_state.df["Delete"] = False
            st.rerun()

    with col3:
        if st.button("❌ Remove All Files", use_container_width=True):
            st.session_state.file_data = {}
            st.session_state.df = None
            st.rerun()

    # Editable table - full height, no pagination
    edited_df = st.data_editor(
        st.session_state.df,
        column_config={
            "Delete": st.column_config.CheckboxColumn(
                "❌",
                help="Check to delete this file",
                default=False,
                width="small",
            ),
            "Filename": st.column_config.TextColumn("Filename", disabled=True, width="medium"),
            "Subtype": st.column_config.SelectboxColumn(
                "Subtype",
                options=st.session_state.all_subtypes,
                required=False,
                width="medium",
            ),
            "Language": st.column_config.TextColumn("Language", width="small"),
            "Paired with": st.column_config.SelectboxColumn(
                "Paired with", options=[""] + list(st.session_state.df["Filename"]), width="medium"
            ),
            "Direction": st.column_config.TextColumn("Direction", width="small"),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        height=600,  # Fixed height to show more rows
    )

    # Update session state with edits
    st.session_state.df = edited_df

    # Handle deletions
    files_to_delete = edited_df[edited_df["Delete"] == True]
    if len(files_to_delete) > 0:
        if st.button(f"🗑️ Confirm Delete {len(files_to_delete)} File(s)", type="secondary", use_container_width=True):
            # Remove from file_data
            for filename in files_to_delete["Filename"]:
                if filename in st.session_state.file_data:
                    del st.session_state.file_data[filename]

            # Remove from dataframe and re-sort
            remaining_df = edited_df[edited_df["Delete"] == False].copy()
            st.session_state.df = sort_dataframe(remaining_df)

            st.success(f"✓ Deleted {len(files_to_delete)} file(s)")
            st.rerun()

    # Update subtype suggestions
    unique_subtypes = [s for s in edited_df["Subtype"].unique() if s and s != ""]
    for subtype in unique_subtypes:
        if subtype not in st.session_state.all_subtypes:
            st.session_state.all_subtypes.append(subtype)

    # Validation
    missing_subtypes = edited_df[edited_df["Subtype"] == ""]
    if len(missing_subtypes) > 0:
        st.info(f"ℹ️ {len(missing_subtypes)} file(s) need subtype labels before extraction")

    # Step 3: Extract
    st.header("🚀 Step 3: Extract Rules & Guidelines")

    # Group by subtype
    subtypes = [s for s in edited_df["Subtype"].unique() if s and s != ""]

    if not subtypes:
        st.info("👆 Add subtype labels to files before extracting")
        st.stop()

    # Show summary
    col1, col2, col3 = st.columns(3)

    files_with_subtype = edited_df[edited_df["Subtype"] != ""]
    total_tokens = sum(
        count_tokens(st.session_state.file_data[fname])
        for fname in files_with_subtype["Filename"]
    )
    example_tokens = 5000 * len(subtypes)
    total_input = total_tokens + example_tokens
    estimated_output = int(total_input * 0.5)
    cost = estimate_cost(total_input, estimated_output, settings.model)

    with col1:
        st.metric("Subtypes to Process", len(subtypes))
    with col2:
        st.metric("Total Tokens", format_tokens(total_tokens))
    with col3:
        st.metric("Estimated Cost", format_cost(cost))

    # Show what will be processed
    with st.expander(f"📦 View Extraction Groups ({len(subtypes)} subtypes)"):
        for subtype in sorted(subtypes):
            subtype_files = edited_df[edited_df["Subtype"] == subtype]
            languages = [lang for lang in subtype_files["Language"].unique() if lang and lang != ""]

            st.markdown(f"**{subtype}**")
            st.markdown(f"- Files: {len(subtype_files)}")
            st.markdown(f"- Languages: {', '.join(languages) if languages else 'Not specified'}")

            # Show which files
            for _, row in subtype_files.iterrows():
                pair_info = f" (paired with {row['Paired with']})" if row["Paired with"] else ""
                st.markdown(f"  - {row['Filename']}{pair_info}")

    if not client_name:
        st.warning("⚠️ Please enter a client name in the sidebar")
        st.stop()

    # Extract button
    if st.button("🤖 Extract Rules & Guidelines", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        results = {}

        for i, subtype in enumerate(sorted(subtypes)):
            status_text.text(f"Processing {subtype}... ({i+1}/{len(subtypes)})")

            # Get files for this subtype
            subtype_files = edited_df[edited_df["Subtype"] == subtype]

            # Build document set
            documents = []
            for _, row in subtype_files.iterrows():
                filename = row["Filename"]
                content = st.session_state.file_data[filename]
                documents.append((Path(filename), content))

            doc_set = DocumentSet(
                client_name=client_name,
                subtype=subtype,
                documents=documents,
                total_tokens=sum(count_tokens(content) for _, content in documents),
            )

            try:
                result = extract_rules_and_guidelines(settings, doc_set)
                results[subtype] = result
            except Exception as e:
                st.error(f"❌ Extraction failed for {subtype}: {e}")
                continue

            progress_bar.progress((i + 1) / len(subtypes))

        status_text.text("✓ Extraction complete!")
        st.session_state.results = results
        st.balloons()
        st.rerun()

    # Show results
    if "results" in st.session_state and st.session_state.results:
        st.header("📋 Results")

        for subtype, result in st.session_state.results.items():
            with st.expander(f"📦 {subtype}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Input Tokens", f"{result.input_tokens:,}")
                with col2:
                    st.metric("Output Tokens", f"{result.output_tokens:,}")

                tab1, tab2 = st.tabs(["🔧 Client Rules (JS)", "📖 Guidelines (MD)"])

                with tab1:
                    st.code(result.client_rules, language="javascript", line_numbers=True)
                    st.download_button(
                        label="⬇️ Download client_rules.js",
                        data=result.client_rules,
                        file_name=f"{client_name}_{subtype}_client_rules.js",
                        mime="text/javascript",
                        key=f"download_rules_{subtype}",
                    )

                with tab2:
                    st.markdown(result.guidelines)
                    st.download_button(
                        label="⬇️ Download guidelines.md",
                        data=result.guidelines,
                        file_name=f"{client_name}_{subtype}_guidelines.md",
                        mime="text/markdown",
                        key=f"download_guidelines_{subtype}",
                    )


if __name__ == "__main__":
    main()
