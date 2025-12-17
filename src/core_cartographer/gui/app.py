"""Main Streamlit application for Core Cartographer.

This module contains the main application logic and step orchestration
for the GUI.
"""

import sys
import tempfile
from pathlib import Path

import streamlit as st

# Handle imports for both direct execution and package import
try:
    from ..config import get_settings
    from ..cost_estimator import count_tokens, estimate_cost, format_cost, format_tokens
    from ..extractor import (
        extract_rules_and_guidelines,
        extract_rules_and_guidelines_batch,
        estimate_prompt_tokens,
    )
    from ..icons import ICON_SETTINGS
    from ..logging_config import get_logger, setup_logging
    from ..models import DocumentSet
    from ..parser import SUPPORTED_EXTENSIONS, parse_document
    from .components import (
        load_css,
        render_file_status,
        render_metric_card,
        render_step_header,
        render_subtype_badges,
    )
    from .data_manager import (
        apply_colored_subtypes,
        auto_detect_all,
        dataframe_to_document_sets,
        extract_subtypes_from_display,
        get_colored_subtype_options,
        sort_dataframe,
    )
except ImportError:
    # Running directly with streamlit, add parent to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from core_cartographer.config import get_settings
    from core_cartographer.cost_estimator import (
        count_tokens,
        estimate_cost,
        format_cost,
        format_tokens,
    )
    from core_cartographer.extractor import (
        extract_rules_and_guidelines,
        extract_rules_and_guidelines_batch,
        estimate_prompt_tokens,
    )
    from core_cartographer.gui.components import (
        load_css,
        render_file_status,
        render_metric_card,
        render_step_header,
        render_subtype_badges,
    )
    from core_cartographer.gui.data_manager import (
        apply_colored_subtypes,
        auto_detect_all,
        dataframe_to_document_sets,
        extract_subtypes_from_display,
        get_colored_subtype_options,
        sort_dataframe,
    )
    from core_cartographer.icons import ICON_SETTINGS
    from core_cartographer.logging_config import get_logger, setup_logging
    from core_cartographer.models import DocumentSet
    from core_cartographer.parser import SUPPORTED_EXTENSIONS, parse_document

logger = get_logger(__name__)


def init_session_state() -> None:
    """Initialize Streamlit session state with defaults."""
    if "file_data" not in st.session_state:
        st.session_state.file_data = {}
    if "df" not in st.session_state:
        st.session_state.df = None
    if "subtypes" not in st.session_state:
        st.session_state.subtypes = ["general"]
    if "step" not in st.session_state:
        st.session_state.step = 1


def render_step_upload() -> None:
    """Render Step 1: File Upload."""
    st.markdown(
        "<h3 style='text-align: center; margin-top: 0;'>Upload Documents</h3>",
        unsafe_allow_html=True,
    )

    # Client Name input
    client_name = st.text_input(
        "Client Name",
        value=st.session_state.get("client_name", ""),
        placeholder="Client Name (e.g. Acme Corp)",
        label_visibility="hidden",
    )
    if client_name:
        st.session_state.client_name = client_name

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload files",
        type=list(ext.replace(".", "") for ext in SUPPORTED_EXTENSIONS),
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    # Process uploads
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.file_data:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=Path(uploaded_file.name).suffix
                ) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = Path(tmp.name)
                try:
                    content = parse_document(tmp_path)
                    st.session_state.file_data[uploaded_file.name] = content
                    logger.info(f"Uploaded file: {uploaded_file.name}")
                except Exception as e:
                    st.warning(f"Failed to parse {uploaded_file.name}: {e}")
                    logger.error(f"Failed to parse {uploaded_file.name}: {e}")
                finally:
                    tmp_path.unlink()

    # Footer / Action Area
    col_info, col_next = st.columns([2, 1])

    with col_info:
        render_file_status(len(st.session_state.file_data))

    with col_next:
        if st.session_state.file_data:
            if st.button("Next →", type="primary", use_container_width=True):
                if not st.session_state.get("client_name"):
                    st.toast("⚠️ Please enter a Client Name before proceeding.", icon="⚠️")
                else:
                    st.session_state.step = 2
                    st.rerun()


def render_step_label() -> None:
    """Render Step 2: Label & Organize."""
    st.markdown("### Organize & Label")

    # Label Management
    col_add, col_tags = st.columns([1, 2])
    with col_add:
        new_label = st.text_input(
            "New Category", placeholder="New Category", label_visibility="collapsed"
        )
        if st.button("+ Add", use_container_width=True):
            if new_label and new_label.strip():
                label = new_label.strip().lower().replace(" ", "_")
                if label not in st.session_state.subtypes:
                    st.session_state.subtypes.append(label)
                    st.rerun()

    with col_tags:
        render_subtype_badges(st.session_state.subtypes)

    # Auto Detection Logic
    if st.session_state.df is None:
        st.session_state.df = auto_detect_all(
            st.session_state.file_data, st.session_state.subtypes
        )

    # Controls
    c1, c2, c3 = st.columns(3)
    if c1.button("Re-run Auto-detect", type="secondary"):
        st.session_state.df = auto_detect_all(
            st.session_state.file_data, st.session_state.subtypes
        )
        st.rerun()
    if c2.button("Clear All Labels", type="secondary"):
        st.session_state.df["Subtype"] = st.session_state.subtypes[0]
        st.rerun()
    if c3.button("Remove All Files", type="secondary"):
        st.session_state.file_data = {}
        st.session_state.df = None
        st.session_state.step = 1
        st.rerun()

    # Data Editor
    st.divider()
    colored_options = get_colored_subtype_options(st.session_state.subtypes)
    display_df = apply_colored_subtypes(st.session_state.df, st.session_state.subtypes)

    edited_df = st.data_editor(
        display_df,
        column_config={
            "❌": st.column_config.CheckboxColumn("Del", width="small"),
            "Filename": st.column_config.TextColumn("Filename", disabled=True),
            "Subtype": st.column_config.SelectboxColumn(
                "Category", options=list(colored_options.keys()), required=True
            ),
            "Pair #": st.column_config.TextColumn("Pair", width="small"),
        },
        hide_index=True,
        use_container_width=True,
        height=500,
    )

    # Sync back and handle deletion
    edited_df = extract_subtypes_from_display(edited_df, colored_options)

    if edited_df["❌"].any():
        files_to_delete = edited_df[edited_df["❌"]]["Filename"]
        for f in files_to_delete:
            if f in st.session_state.file_data:
                del st.session_state.file_data[f]
                logger.info(f"Deleted file: {f}")
        st.session_state.df = sort_dataframe(edited_df[~edited_df["❌"]])
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
        if not st.session_state.get("client_name"):
            st.toast("⚠️ Please enter a Client Name (Step 1) to proceed!", icon="⚠️")
            st.session_state.step = 1
            st.rerun()
        else:
            st.session_state.step = 3
            st.rerun()


def render_step_extract(settings) -> None:
    """Render Step 3: Extract & Results."""
    st.markdown("### Extraction & Results")

    # Convert DataFrame to DocumentSets (preserves language/pair info)
    all_doc_sets = dataframe_to_document_sets(
        df=st.session_state.df,
        file_data=st.session_state.file_data,
        client_name=st.session_state.client_name,
    )

    subtypes = [ds.subtype for ds in all_doc_sets]

    # Summary Metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Groups", str(len(subtypes)))

    total_tokens = sum(ds.total_tokens for ds in all_doc_sets)
    with c2:
        render_metric_card("Total Tokens", format_tokens(total_tokens))

    # Estimate cost using the new function
    est_input_tokens = estimate_prompt_tokens(
        client_name=st.session_state.client_name,
        document_sets=all_doc_sets,
        settings=settings,
    )

    # Adjust for batch vs individual
    if not settings.batch_processing and len(subtypes) > 1:
        # Individual mode: prompt overhead per subtype
        est_input_tokens = est_input_tokens + (4000 * (len(subtypes) - 1))

    est_cost = estimate_cost(
        est_input_tokens, total_tokens * 0.5, settings.model
    )
    with c3:
        render_metric_card("Est. Cost", format_cost(est_cost))

    st.divider()

    # Show language/pair summary
    total_pairs = sum(len(ds.paired_documents) for ds in all_doc_sets)
    total_unpaired = sum(len(ds.unpaired_documents) for ds in all_doc_sets)

    if total_pairs > 0:
        st.success(f"✅ {total_pairs} document pair(s) detected - terminology extraction enabled")
    elif total_unpaired > 0:
        st.warning("⚠️ No document pairs detected - terminology extraction will be limited")

    if "results" not in st.session_state:
        st.session_state.results = {}

    # Show mode indicator
    if settings.debug_mode:
        st.info("🐛 Debug Mode: Prompts will be saved to /debug folder (no API calls)")
    if settings.batch_processing and len(subtypes) > 1:
        st.info("📦 Batch Processing: All subtypes will be processed in one API call")

    # Action Button
    if not st.session_state.results:
        if st.button("Start Extraction 🚀", type="primary", use_container_width=True):
            progress_bar = st.progress(0, text="Initializing...")
            results = {}

            # Process based on mode
            if settings.batch_processing and len(all_doc_sets) > 1:
                # Batch processing: one API call for all subtypes
                progress_bar.progress(0.5, text="Processing all groups in batch...")
                logger.info(f"Batch processing {len(all_doc_sets)} subtypes")

                try:
                    results = extract_rules_and_guidelines_batch(settings, all_doc_sets)
                    logger.info("Batch extraction complete")
                except Exception as e:
                    st.error(f"Error during batch processing: {e}")
                    logger.error(f"Batch extraction failed: {e}")
            else:
                # Individual processing: one API call per subtype
                for i, doc_set in enumerate(all_doc_sets):
                    progress_bar.progress(
                        i / len(all_doc_sets), text=f"Analyzing {doc_set.subtype} group..."
                    )
                    logger.info(f"Processing subtype: {doc_set.subtype}")

                    try:
                        result = extract_rules_and_guidelines(settings, doc_set)
                        results[doc_set.subtype] = result
                        logger.info(f"Extraction complete for {doc_set.subtype}")
                    except Exception as e:
                        st.error(f"Error processing {doc_set.subtype}: {e}")
                        logger.error(f"Extraction failed for {doc_set.subtype}: {e}")

            progress_bar.empty()
            st.session_state.results = results

            if settings.debug_mode:
                st.success("✅ Debug mode: Prompts saved successfully!")
            else:
                st.balloons()

            st.rerun()

    # Display Results
    if st.session_state.results:
        for subtype, result in st.session_state.results.items():
            with st.expander(f"📦 {subtype.upper()} Results", expanded=True):
                tab1, tab2 = st.tabs(["Client Rules (JS)", "Guidelines (MD)"])

                with tab1:
                    st.download_button(
                        "Download .js",
                        result.client_rules,
                        f"{subtype}.js",
                        "text/javascript",
                    )
                    st.code(result.client_rules, language="javascript")

                with tab2:
                    st.download_button(
                        "Download .md",
                        result.guidelines,
                        f"{subtype}.md",
                        "text/markdown",
                    )
                    st.markdown(result.guidelines)

        if st.button("Start Over", type="secondary"):
            st.session_state.results = {}
            st.session_state.step = 1
            st.rerun()


def main() -> None:
    """Main entry point for the Streamlit GUI."""
    # Configure page
    st.set_page_config(
        page_title="Core Cartographer",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Setup logging (only console for GUI)
    setup_logging(console=False)

    # Inject CSS
    load_css()

    # Title
    st.markdown(
        "<h1 style='text-align: center; margin-bottom: 0.5rem;'>Core Cartographer</h1>",
        unsafe_allow_html=True,
    )

    # Load Settings
    try:
        settings = get_settings()
    except Exception as e:
        st.error(f"Configuration error: {e}")
        logger.error(f"Configuration error: {e}")
        st.stop()

    # Initialize session state
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.markdown(f"{ICON_SETTINGS}", unsafe_allow_html=True)
        st.markdown("### Configuration")
        st.caption(f"Model: {settings.model}")
        st.caption(f"Files: {', '.join(SUPPORTED_EXTENSIONS)}")
        st.divider()

        # Processing options
        st.markdown("### Processing Options")

        debug_mode = st.checkbox(
            "Debug Mode",
            value=settings.debug_mode,
            help="Save prompts to /debug folder instead of calling API"
        )
        settings.debug_mode = debug_mode

        batch_processing = st.checkbox(
            "Batch Processing",
            value=settings.batch_processing,
            help="Process all subtypes in one API call (useful for finding common patterns)"
        )
        settings.batch_processing = batch_processing

        st.divider()

    # Render current step
    render_step_header(st.session_state.step)

    # Content container
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        if st.session_state.step == 1:
            render_step_upload()
        elif st.session_state.step == 2:
            render_step_label()
        elif st.session_state.step == 3:
            render_step_extract(settings)

        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
