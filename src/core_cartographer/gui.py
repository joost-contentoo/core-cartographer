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
    from .icons import ICON_MAP, ICON_UPLOAD, ICON_SETTINGS  # New Premium Icons
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
    from core_cartographer.icons import ICON_MAP, ICON_UPLOAD, ICON_SETTINGS


# --- Utils ---

def load_css():
    """Load and inject custom Premium CSS."""
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def detect_language(text: str) -> str:
    """Detect language from text content."""
    try:
        sample = text[:1000]
        lang_code = detect(sample)
        return lang_code.upper()
    except LangDetectException:
        return "UNKNOWN"


def extract_language_from_filename(filename: str) -> Optional[str]:
    """Extract language code from filename (e.g., card_EN.txt -> EN)."""
    pattern = r"[_\-\(\[]([A-Z]{2})[_\-\)\]]"
    match = re.search(pattern, filename.upper())
    if match:
        return match.group(1)
    return None


def find_base_name(filename: str) -> str:
    """Extract base name without language code and extension."""
    name = Path(filename).stem
    name = re.sub(r"[_\-\(\[]([A-Z]{2})[_\-\)\]]", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[\s_\-]*(EN|DE|FR|NL|ES|IT|PT|PL|RU|JA|ZH|KO)[\s_\-]*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[\s_\-]{2,}", "_", name)
    name = name.strip("_- ")
    return name.lower()


def fuzzy_similarity(s1: str, s2: str) -> float:
    """Calculate simple similarity ratio between two strings."""
    if not s1 or not s2:
        return 0.0
    s1, s2 = s1.lower(), s2.lower()
    if s1 in s2 or s2 in s1:
        return 0.8
    common = sum(1 for c in s1 if c in s2)
    return common / max(len(s1), len(s2))


def find_pairs_by_filename(df: pd.DataFrame, file_data: dict) -> pd.DataFrame:
    """Auto-detect paired files based on filename similarity."""
    df = df.copy()
    df["base_name"] = df["Filename"].apply(find_base_name)
    pair_number = 1
    processed = set()

    for idx, row in df.iterrows():
        if row["Filename"] in processed:
            continue

        my_lang = row["Language"]
        my_base = row["base_name"]
        my_filename = row["Filename"]

        if my_lang == "UNKNOWN":
            df.loc[idx, "Pair #"] = "-"
            processed.add(my_filename)
            continue

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

            if my_base and cand_base and my_base == cand_base:
                best_match = cand_filename
                break

            fuzzy_score = fuzzy_similarity(my_base, cand_base)
            my_content = file_data.get(my_filename, "")
            cand_content = file_data.get(cand_filename, "")
            
            if my_content and cand_content:
                len_ratio = min(len(my_content), len(cand_content)) / max(len(my_content), len(cand_content))
                combined_score = fuzzy_score * 0.7 + len_ratio * 0.3
            else:
                combined_score = fuzzy_score

            if combined_score > best_score and combined_score > 0.5:
                best_score = combined_score
                best_match = cand_filename

        if best_match:
            df.loc[df["Filename"] == my_filename, "Pair #"] = str(pair_number)
            df.loc[df["Filename"] == best_match, "Pair #"] = str(pair_number)
            processed.add(my_filename)
            processed.add(best_match)
            pair_number += 1
        else:
            df.loc[idx, "Pair #"] = "-"
            processed.add(my_filename)

    return df.drop(columns=["base_name"])


def get_subtype_color(subtype: str, all_subtypes: list[str]) -> str:
    """Assign a colored circle emoji to each subtype for visual distinction."""
    colors = ["🔵", "🟢", "🟡", "🟠", "🟣", "🔴", "🟤", "⚫", "⚪", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪"]
    try:
        idx = all_subtypes.index(subtype) % len(colors)
        return colors[idx]
    except ValueError:
        return "⚪"


def sort_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Sort dataframe: paired files together, then alphabetically."""
    df = df.copy()

    def sort_key(row):
        pair = row["Pair #"]
        if pair == "-":
            return (999999, row["Filename"])
        else:
            try:
                pair_int = int(pair)
            except (ValueError, TypeError):
                pair_int = 999999
            return (pair_int, row["Filename"])

    df["sort_key"] = df.apply(sort_key, axis=1)
    df = df.sort_values("sort_key").reset_index(drop=True)
    return df.drop(columns=["sort_key"])


def auto_detect_all(file_data: dict, subtypes: list[str]) -> pd.DataFrame:
    """Run auto-detection on all files and return dataframe."""
    default_subtype = subtypes[0] if subtypes else "general"
    data = {
        "❌": [False] * len(file_data),
        "Filename": list(file_data.keys()),
        "Subtype": [default_subtype] * len(file_data),
        "Language": [""] * len(file_data),
        "Pair #": ["-"] * len(file_data),
    }
    df = pd.DataFrame(data)

    for idx, row in df.iterrows():
        content = file_data[row["Filename"]]
        lang_from_file = extract_language_from_filename(row["Filename"])
        if lang_from_file:
            df.at[idx, "Language"] = lang_from_file
        else:
            df.at[idx, "Language"] = detect_language(content)

    df = find_pairs_by_filename(df, file_data)
    return sort_dataframe(df)


# --- UI Components ---

def render_step_header(current_step: int):
    """Render the CSS-styled progress header."""
    steps = [
        {"id": 1, "label": "Upload"},
        {"id": 2, "label": "Label"},
        {"id": 3, "label": "Extract"},
    ]
    
    html = '<div class="step-header">'
    for i, step in enumerate(steps):
        active_class = 'active' if step['id'] <= current_step else ''
        html += f'<div class="step-item {active_class}">{step["id"]}. {step["label"]}</div>'
        if i < len(steps) - 1:
            loader_active = 'active' if step['id'] < current_step else ''
            html += f'<div class="step-loader {loader_active}"></div>'
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(label: str, value: str):
    """Render a custom metric card."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# --- Main App Logic ---

def main() -> None:
    st.set_page_config(
        page_title="Core Cartographer",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # 1. Inject Global CSS
    load_css()

    # 2. Main Title Area (Centered, Clean, No Version)
    st.markdown("<h1 style='text-align: center; margin-bottom: 0.5rem;'>Core Cartographer</h1>", unsafe_allow_html=True)
    
    # 3. Load Settings
    try:
        settings = get_settings()
    except Exception as e:
        st.error(f"Configuration error: {e}")
        st.stop()

    # 4. Session State Init
    if "file_data" not in st.session_state:
        st.session_state.file_data = {}
    if "df" not in st.session_state:
        st.session_state.df = None
    if "subtypes" not in st.session_state:
        st.session_state.subtypes = ["general"]
    if "step" not in st.session_state:
        st.session_state.step = 1

    # 5. Sidebar (Settings) - Minimal
    with st.sidebar:
        st.markdown(f"{ICON_SETTINGS}", unsafe_allow_html=True)
        st.markdown("### Configuration")
        
        st.caption(f"Model: {settings.model}")
        st.caption(f"Files: {', '.join(SUPPORTED_EXTENSIONS)}")
        st.divider()

    # 6. Render Current Step
    render_step_header(st.session_state.step)
    
    # Wrap content in a "Clean Card" (Light mode)
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        # --- STEP 1: UPLOAD ---
        if st.session_state.step == 1:
            st.markdown("<h3 style='text-align: center; margin-top: 0;'>Upload Documents</h3>", unsafe_allow_html=True)
            
            # Client Name - Prominent but compact
            client_name = st.text_input(
                "Client Name",
                value=st.session_state.get("client_name", ""),
                placeholder="Client Name (e.g. Acme Corp)",
                label_visibility="hidden"
            )
            if client_name:
                st.session_state.client_name = client_name
            
            # Simplified Dropzone Text (removed redundant "Drag & drop...")
            
            uploaded_files = st.file_uploader(
                "Upload files",
                type=list(ext.replace(".", "") for ext in SUPPORTED_EXTENSIONS),
                accept_multiple_files=True,
                label_visibility="collapsed"
            )

            # Process uploads
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    if uploaded_file.name not in st.session_state.file_data:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                            tmp.write(uploaded_file.read())
                            tmp_path = Path(tmp.name)
                        try:
                            content = parse_document(tmp_path)
                            st.session_state.file_data[uploaded_file.name] = content
                        except Exception as e:
                            st.warning(f"Failed to parse {uploaded_file.name}: {e}")
                        finally:
                            tmp_path.unlink()

            # Footer / Action Area - Compact
            col_info, col_next = st.columns([2, 1])
            
            with col_info:
                if st.session_state.file_data:
                    st.success(f"{len(st.session_state.file_data)} documents ready.")
                else:
                    st.markdown("<div style='padding-top: 0.5rem; color: #94a3b8; font-size: 0.9rem;'>Waiting for files...</div>", unsafe_allow_html=True)

            with col_next:
                if st.session_state.file_data:
                    if st.button("Next →", type="primary", use_container_width=True):
                        # Validation: Check client name
                        if not st.session_state.get("client_name"):
                             st.toast("⚠️ Please enter a Client Name before proceeding.", icon="⚠️")
                        else:
                            st.session_state.step = 2
                            st.rerun()

        # --- STEP 2: LABEL ---
        elif st.session_state.step == 2:
            st.markdown("### Organize & Label")
            
            # Label Management (Compact)
            col_add, col_tags = st.columns([1, 2])
            with col_add:
                new_label = st.text_input("New Category", placeholder="New Category", label_visibility="collapsed")
                if st.button("+ Add", use_container_width=True):
                     if new_label and new_label.strip():
                        label = new_label.strip().lower().replace(" ", "_")
                        if label not in st.session_state.subtypes:
                            st.session_state.subtypes.append(label)
                            st.rerun()
                            
            with col_tags:
                 st.markdown(" ".join([f"<span class='badge' style='background: #e2e8f0; color: #1e293b; border: 1px solid #cbd5e1;'>{s}</span>" for s in st.session_state.subtypes]), unsafe_allow_html=True)

            # Auto Detection Logic (Run once if needed)
            if st.session_state.df is None:
                st.session_state.df = auto_detect_all(st.session_state.file_data, st.session_state.subtypes)

            # Controls
            c1, c2, c3 = st.columns(3)
            if c1.button("Re-run Auto-detect", type="secondary"):
                st.session_state.df = auto_detect_all(st.session_state.file_data, st.session_state.subtypes)
                st.rerun()
            if c2.button("Clear All Labels", type="secondary"):
                st.session_state.df["Subtype"] = st.session_state.subtypes[0]
                st.rerun()
            if c3.button("Remove All Files", type="secondary"):
                st.session_state.file_data = {}
                st.session_state.df = None
                st.session_state.step = 1
                st.rerun()

            # Editor
            st.divider()
            colored_options = {
                f"{get_subtype_color(s, st.session_state.subtypes)} {s}": s
                for s in st.session_state.subtypes
            }
            
            # Prepare display DF
            display_df = st.session_state.df.copy()
            display_df["Subtype"] = display_df["Subtype"].apply(
                lambda x: f"{get_subtype_color(x, st.session_state.subtypes)} {x}"
            )

            edited_df = st.data_editor(
                display_df,
                column_config={
                    "❌": st.column_config.CheckboxColumn("Del", width="small"),
                    "Filename": st.column_config.TextColumn("Filename", disabled=True),
                    "Subtype": st.column_config.SelectboxColumn("Category", options=list(colored_options.keys()), required=True),
                    "Pair #": st.column_config.TextColumn("Pair", width="small")
                },
                hide_index=True,
                use_container_width=True,
                height=500
            )

            # Sync Back
            edited_df["Subtype"] = edited_df["Subtype"].apply(
                lambda x: colored_options.get(x, x.split(" ", 1)[-1] if " " in x else x)
            )
            
            # Handle Deletion
            if edited_df["❌"].any():
                files_to_delete = edited_df[edited_df["❌"] == True]["Filename"]
                for f in files_to_delete:
                    if f in st.session_state.file_data:
                        del st.session_state.file_data[f]
                st.session_state.df = sort_dataframe(edited_df[edited_df["❌"] == False])
                st.rerun()
            else:
                st.session_state.df = edited_df

            # Navigation
            st.divider()
            cb, cn = st.columns([1, 1])
            if cb.button("← Back"):
                st.session_state.step = 1
                st.rerun()
            if cn.button("Extract Data →", type="primary"):
                # Double check client name
                if not st.session_state.get("client_name"):
                    st.toast("⚠️ Please enter a Client Name (Step 1) to proceed!", icon="⚠️")
                    st.session_state.step = 1
                    st.rerun()
                else:
                    st.session_state.step = 3
                    st.rerun()

        # --- STEP 3: EXTRACT ---
        elif st.session_state.step == 3:
            st.markdown("### Extraction & Results")
            
            subtypes = [s for s in st.session_state.df["Subtype"].unique() if s]
            
            # Summary Metrics
            c1, c2, c3 = st.columns(3)
            with c1: render_metric_card("Groups", str(len(subtypes)))
            total_tokens = sum(count_tokens(c) for c in st.session_state.file_data.values())
            with c2: render_metric_card("Total Tokens", format_tokens(total_tokens))
            est_cost = estimate_cost(total_tokens + (5000 * len(subtypes)), total_tokens * 0.5, settings.model)
            with c3: render_metric_card("Est. Cost", format_cost(est_cost))

            st.divider()

            if "results" not in st.session_state:
                st.session_state.results = {}

            # Action Button
            if not st.session_state.results:
                if st.button("Start Extraction 🚀", type="primary", use_container_width=True):
                    progress_bar = st.progress(0, text="Initializing...")
                    results = {}
                    
                    for i, subtype in enumerate(sorted(subtypes)):
                        progress_bar.progress((i) / len(subtypes), text=f"Analyzing {subtype} group...")
                        
                        subtype_files = st.session_state.df[st.session_state.df["Subtype"] == subtype]
                        documents = []
                        for _, row in subtype_files.iterrows():
                            filename = row["Filename"]
                            content = st.session_state.file_data[filename]
                            documents.append((Path(filename), content))

                        doc_set = DocumentSet(
                            client_name=st.session_state.client_name,
                            subtype=subtype,
                            documents=documents,
                            total_tokens=sum(count_tokens(c) for _, c in documents),
                        )

                        try:
                            result = extract_rules_and_guidelines(settings, doc_set)
                            results[subtype] = result
                        except Exception as e:
                            st.error(f"Error processing {subtype}: {e}")
                    
                    progress_bar.empty()
                    st.session_state.results = results
                    st.balloons()
                    st.rerun()
            
            # Display Results
            if st.session_state.results:
                for subtype, result in st.session_state.results.items():
                    with st.expander(f"📦 {subtype.upper()} Results", expanded=True):
                        tab1, tab2 = st.tabs(["Client Rules (JS)", "Guidelines (MD)"])
                        
                        with tab1:
                            st.download_button("Download .js", result.client_rules, f"{subtype}.js", "text/javascript")
                            st.code(result.client_rules, language="javascript")
                            
                        with tab2:
                            st.download_button("Download .md", result.guidelines, f"{subtype}.md", "text/markdown")
                            st.markdown(result.guidelines)
                
                if st.button("Start Over", type="secondary"):
                    st.session_state.results = {}
                    st.session_state.step = 1
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True) # End glass-card

if __name__ == "__main__":
    main()
