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

    # Remove common language patterns (e.g., _EN, -DE, (FR), [NL])
    name = re.sub(r"[_\-\(\[]([A-Z]{2})[_\-\)\]]", "", name, flags=re.IGNORECASE)

    # Also remove trailing/standalone language codes (e.g., "document EN" or "documentEN")
    name = re.sub(r"[\s_\-]*(EN|DE|FR|NL|ES|IT|PT|PL|RU|JA|ZH|KO)[\s_\-]*$", "", name, flags=re.IGNORECASE)

    # Clean up double separators and whitespace
    name = re.sub(r"[\s_\-]{2,}", "_", name)
    name = name.strip("_- ")

    return name.lower()  # Normalize to lowercase for better matching


def fuzzy_similarity(s1: str, s2: str) -> float:
    """Calculate simple similarity ratio between two strings."""
    if not s1 or not s2:
        return 0.0

    # Normalize strings
    s1, s2 = s1.lower(), s2.lower()

    # If one is substring of the other, high similarity
    if s1 in s2 or s2 in s1:
        return 0.8

    # Count common characters
    common = sum(1 for c in s1 if c in s2)
    return common / max(len(s1), len(s2))


def find_pairs_by_filename(df: pd.DataFrame, file_data: dict) -> pd.DataFrame:
    """
    Auto-detect paired files based on filename similarity and content.
    Returns dataframe with pair numbers assigned.

    Strategy:
    1. Exact base name match (after removing language codes)
    2. Fuzzy filename matching for similar names
    3. Content length similarity for files with same detected language count
    """
    df = df.copy()

    # Extract base names for each file
    df["base_name"] = df["Filename"].apply(find_base_name)

    # Assign pair numbers
    pair_number = 1
    processed = set()

    for idx, row in df.iterrows():
        if row["Filename"] in processed:
            continue

        my_lang = row["Language"]
        my_base = row["base_name"]
        my_filename = row["Filename"]

        # Skip if language is unknown
        if my_lang == "UNKNOWN":
            df.loc[idx, "Pair #"] = "-"
            processed.add(my_filename)
            continue

        # Candidates: files not yet processed, different language
        candidates = df[
            (~df["Filename"].isin(processed))
            & (df["Filename"] != my_filename)
            & (df["Language"] != my_lang)
            & (df["Language"] != "UNKNOWN")
        ]

        if len(candidates) == 0:
            df.loc[idx, "Pair #"] = "-"
            processed.add(my_filename)
            continue

        best_match = None
        best_score = 0.0

        for _, candidate in candidates.iterrows():
            cand_base = candidate["base_name"]
            cand_filename = candidate["Filename"]

            # Score 1: Exact base name match (highest priority)
            if my_base and cand_base and my_base == cand_base:
                best_match = cand_filename
                break  # Perfect match, stop searching

            # Score 2: Fuzzy filename similarity
            fuzzy_score = fuzzy_similarity(my_base, cand_base)

            # Score 3: Content length similarity (documents in different languages often have similar length)
            my_content = file_data.get(my_filename, "")
            cand_content = file_data.get(cand_filename, "")
            if my_content and cand_content:
                len_ratio = min(len(my_content), len(cand_content)) / max(len(my_content), len(cand_content))
                # Weight content similarity as bonus
                combined_score = fuzzy_score * 0.7 + len_ratio * 0.3
            else:
                combined_score = fuzzy_score

            if combined_score > best_score and combined_score > 0.5:  # Threshold
                best_score = combined_score
                best_match = cand_filename

        if best_match:
            # Assign pair number to both files (as string)
            df.loc[df["Filename"] == my_filename, "Pair #"] = str(pair_number)
            df.loc[df["Filename"] == best_match, "Pair #"] = str(pair_number)
            processed.add(my_filename)
            processed.add(best_match)
            pair_number += 1
        else:
            df.loc[idx, "Pair #"] = "-"
            processed.add(my_filename)

    # Remove helper column
    df = df.drop(columns=["base_name"])

    return df


def get_subtype_color(subtype: str, all_subtypes: list[str]) -> str:
    """Assign a colored circle emoji to each subtype for visual distinction."""
    colors = ["🔵", "🟢", "🟡", "🟠", "🟣", "🔴", "🟤", "⚫", "⚪", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪"]
    try:
        idx = all_subtypes.index(subtype) % len(colors)
        return colors[idx]
    except ValueError:
        return "⚪"


def sort_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort dataframe: paired files together, then alphabetically.
    """
    df = df.copy()

    # Create sort keys
    # Files with pair numbers sort first by pair number, then by filename
    # Files with "-" sort by filename only

    def sort_key(row):
        pair = row["Pair #"]
        if pair == "-":
            # No pair - sort at the end alphabetically
            return (999999, row["Filename"])
        else:
            # Has pair - sort by pair number (as int), then filename
            try:
                pair_int = int(pair)
            except (ValueError, TypeError):
                pair_int = 999999
            return (pair_int, row["Filename"])

    df["sort_key"] = df.apply(sort_key, axis=1)
    df = df.sort_values("sort_key").reset_index(drop=True)
    df = df.drop(columns=["sort_key"])

    return df


def auto_detect_all(file_data: dict, subtypes: list[str]) -> pd.DataFrame:
    """Run auto-detection on all files and return dataframe."""
    # Initialize dataframe with default subtype from the list
    default_subtype = subtypes[0] if subtypes else "general"
    data = {
        "❌": [False] * len(file_data),
        "Filename": list(file_data.keys()),
        "Subtype": [default_subtype] * len(file_data),
        "Language": [""] * len(file_data),
        "Pair #": ["-"] * len(file_data),
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

    # Find pairs and assign numbers (passing file_data for content-based matching)
    df = find_pairs_by_filename(df, file_data)

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
    if "subtypes" not in st.session_state:
        st.session_state.subtypes = ["general"]  # Default with just "general"
    if "show_step2" not in st.session_state:
        st.session_state.show_step2 = False

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

    # Step 1: File Upload & Subtype Labels
    st.header("📤 Step 1: Upload Documents")

    col_upload, col_labels = st.columns([2, 1])

    with col_upload:
        uploaded_files = st.file_uploader(
            "Upload all documents to analyze",
            type=list(ext.replace(".", "") for ext in SUPPORTED_EXTENSIONS),
            accept_multiple_files=True,
            help="Select all files at once",
        )

    with col_labels:
        st.markdown("**Subtype Labels** (optional)")
        st.caption("Define labels to categorize documents. Default is 'general'.")

        # Show current labels as tags
        if st.session_state.subtypes:
            st.markdown(" ".join([f"`{s}`" for s in st.session_state.subtypes]))

        # Add new label
        new_label = st.text_input(
            "Add label",
            placeholder="e.g., gift_cards",
            key="new_subtype_input",
            label_visibility="collapsed",
        )
        if st.button("➕ Add", key="add_subtype_btn", use_container_width=True):
            if new_label and new_label.strip():
                label = new_label.strip().lower().replace(" ", "_")
                if label not in st.session_state.subtypes:
                    st.session_state.subtypes.append(label)
                    st.rerun()

        # Reset labels
        if len(st.session_state.subtypes) > 1:
            if st.button("🔄 Reset to 'general'", key="reset_subtypes_btn", use_container_width=True):
                st.session_state.subtypes = ["general"]
                # Also reset subtypes in the dataframe if it exists
                if st.session_state.df is not None:
                    st.session_state.df["Subtype"] = "general"
                st.rerun()

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

        st.success(f"✓ {len(st.session_state.file_data)} document(s) ready")

    if not st.session_state.file_data:
        st.info("👆 Upload documents to continue")
        st.stop()

    # Show continue button
    st.divider()
    if not st.session_state.show_step2:
        st.info("📝 Add any subtype labels above if needed, then continue to Step 2")
        if st.button("➡️ Continue to Step 2", type="primary", use_container_width=True):
            st.session_state.show_step2 = True
            st.rerun()
        st.stop()

    # Run auto-detection if not done yet
    if st.session_state.df is None:
        with st.spinner("🔍 Auto-detecting languages and finding pairs..."):
            st.session_state.df = auto_detect_all(st.session_state.file_data, st.session_state.subtypes)

    # Step 2: Edit table
    st.header("📋 Step 2: Label & Review Documents")

    st.markdown("**Instructions:**")
    st.markdown("- **✏️ Editable columns**: Subtype, Language, Pair #")
    st.markdown("- **Subtype**: Select from colored labels defined in Step 1")
    st.markdown("- **Language**: Language code (auto-detected, can be edited)")
    st.markdown("- **Pair #**: Files with same number are paired, `-` means no pair")
    st.markdown("- **❌ Delete**: Check to remove files immediately")

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        if st.button("⬅️ Back to Step 1", use_container_width=True):
            st.session_state.show_step2 = False
            st.rerun()

    with col2:
        if st.button("🔄 Re-run Auto-detection", use_container_width=True):
            with st.spinner("Detecting..."):
                st.session_state.df = auto_detect_all(st.session_state.file_data, st.session_state.subtypes)
                st.success("✓ Auto-detection complete!")
                st.rerun()

    with col3:
        if st.button("🗑️ Clear All Labels", use_container_width=True):
            st.session_state.df["Subtype"] = st.session_state.subtypes[0]
            st.session_state.df["❌"] = False
            st.rerun()

    with col4:
        if st.button("❌ Remove All Files", use_container_width=True):
            st.session_state.file_data = {}
            st.session_state.df = None
            st.session_state.show_step2 = False
            st.rerun()

    # Create colored subtype options for the dropdown
    colored_subtype_options = {
        f"{get_subtype_color(subtype, st.session_state.subtypes)} {subtype}": subtype
        for subtype in st.session_state.subtypes
    }

    # Convert current subtype values to colored display format
    display_df = st.session_state.df.copy()
    display_df["Subtype"] = display_df["Subtype"].apply(
        lambda x: f"{get_subtype_color(x, st.session_state.subtypes)} {x}"
    )

    # Editable table - full height, no pagination
    edited_df = st.data_editor(
        display_df,
        column_config={
            "❌": st.column_config.CheckboxColumn(
                "❌",
                help="Click to delete this file",
                default=False,
                width="small",
            ),
            "Filename": st.column_config.TextColumn("Filename", disabled=True, width="medium"),
            "Subtype": st.column_config.SelectboxColumn(
                "Subtype",
                options=list(colored_subtype_options.keys()),
                required=True,
                width="medium",
                help="Document category (editable)",
            ),
            "Language": st.column_config.TextColumn("Language", width="small", help="Language code (editable)"),
            "Pair #": st.column_config.TextColumn("Pair #", width="small", help="Paired document number (editable)"),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        height=600,  # Fixed height to show more rows
    )

    # Convert colored subtypes back to plain values
    edited_df["Subtype"] = edited_df["Subtype"].apply(
        lambda x: colored_subtype_options.get(x, x.split(" ", 1)[-1] if " " in x else x)
    )

    # Handle immediate deletions
    files_to_delete = edited_df[edited_df["❌"] == True]
    if len(files_to_delete) > 0:
        # Remove from file_data
        for filename in files_to_delete["Filename"]:
            if filename in st.session_state.file_data:
                del st.session_state.file_data[filename]

        # Remove from dataframe and re-sort
        remaining_df = edited_df[edited_df["❌"] == False].copy()
        st.session_state.df = sort_dataframe(remaining_df)

        st.success(f"✓ Deleted {len(files_to_delete)} file(s)")
        st.rerun()

    # Update session state with edits
    st.session_state.df = edited_df


    # Step 3: Extract
    st.header("🚀 Step 3: Extract Rules & Guidelines")

    # Group by subtype
    subtypes = [s for s in edited_df["Subtype"].unique() if s and s != ""]

    if not subtypes:
        st.info("👆 All files are using the default 'general' subtype")

    # Show summary
    col1, col2, col3 = st.columns(3)

    total_tokens = sum(count_tokens(content) for content in st.session_state.file_data.values())
    example_tokens = 5000 * len(subtypes) if subtypes else 5000
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
            pairs = [p for p in subtype_files["Pair #"].unique() if p != "-"]

            st.markdown(f"**{subtype}**")
            st.markdown(f"- Files: {len(subtype_files)}")
            st.markdown(f"- Languages: {', '.join(languages) if languages else 'Not specified'}")
            st.markdown(f"- Paired sets: {len(pairs)}")

            # Show which files
            for _, row in subtype_files.iterrows():
                pair_info = f" [Pair #{row['Pair #']}]" if row["Pair #"] != "-" else ""
                st.markdown(f"  - {row['Filename']} ({row['Language']}){pair_info}")

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
