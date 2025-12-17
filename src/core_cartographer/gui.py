"""Streamlit GUI for Core Cartographer."""

import sys
import tempfile
from pathlib import Path

import streamlit as st

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
    from core_cartographer.cost_estimator import count_tokens, estimate_cost, format_cost, format_tokens


def main() -> None:
    """Main entry point for the Streamlit GUI."""
    st.set_page_config(
        page_title="Core Cartographer",
        page_icon="🗺️",
        layout="wide",
    )

    st.title(f"🗺️ Core Cartographer v{__version__}")
    st.markdown(
        "Extract **validation rules** and **localization guidelines** from copy documents"
    )

    # Load settings
    try:
        settings = get_settings()
    except Exception as e:
        st.error(f"⚠️ Configuration error: {e}")
        st.info("Make sure you have a `.env` file with `ANTHROPIC_API_KEY` set.")
        st.stop()

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        client_name = st.text_input(
            "Client Name",
            value="",
            placeholder="e.g., dundle, acme",
            help="Name of the client for this extraction"
        )

        subtype_name = st.text_input(
            "Document Subtype",
            value="",
            placeholder="e.g., gift_cards, payment_cards",
            help="Type of documents being analyzed"
        )

        st.divider()

        st.markdown(f"**Model:** {settings.model}")
        st.markdown(f"**Supported formats:** {', '.join(SUPPORTED_EXTENSIONS)}")

    # Main content
    if not client_name or not subtype_name:
        st.info("👈 Enter client name and document subtype in the sidebar to begin")
        st.markdown("---")
        _show_help()
        st.stop()

    # File upload
    st.header("📤 Upload Documents")

    uploaded_files = st.file_uploader(
        "Upload copy documents to analyze",
        type=list(ext.replace(".", "") for ext in SUPPORTED_EXTENSIONS),
        accept_multiple_files=True,
        help="Upload one or more documents in supported formats"
    )

    if not uploaded_files:
        st.info("Upload documents to begin extraction")
        st.stop()

    # Process uploaded files
    st.success(f"✓ {len(uploaded_files)} document(s) uploaded")

    # Parse documents and create DocumentSet
    with st.spinner("Parsing documents..."):
        documents = []
        total_tokens = 0

        for uploaded_file in uploaded_files:
            # Save to temp file for parsing
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=Path(uploaded_file.name).suffix
            ) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = Path(tmp.name)

            try:
                content = parse_document(tmp_path)
                documents.append((Path(uploaded_file.name), content))
                total_tokens += count_tokens(content)
            except Exception as e:
                st.warning(f"⚠️ Failed to parse {uploaded_file.name}: {e}")
            finally:
                tmp_path.unlink()

    if not documents:
        st.error("No documents could be parsed successfully")
        st.stop()

    # Create DocumentSet
    doc_set = DocumentSet(
        client_name=client_name,
        subtype=subtype_name,
        documents=documents,
        total_tokens=total_tokens,
    )

    # Show summary
    st.header("📊 Document Summary")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documents", len(doc_set.documents))
    with col2:
        st.metric("Total Tokens", format_tokens(doc_set.total_tokens))
    with col3:
        example_tokens = 5000
        total_input = doc_set.total_tokens + example_tokens
        estimated_output = int(total_input * 0.5)
        cost = estimate_cost(total_input, estimated_output, settings.model)
        st.metric("Estimated Cost", format_cost(cost))

    # Document list
    with st.expander("📄 View Document List"):
        for path, content in doc_set.documents:
            tokens = count_tokens(content)
            st.markdown(f"- **{path.name}** — {format_tokens(tokens)}")

    # Extract button
    st.header("🚀 Extraction")

    if st.button("Extract Rules & Guidelines", type="primary", use_container_width=True):
        with st.spinner("🤖 Claude is analyzing documents..."):
            try:
                result = extract_rules_and_guidelines(settings, doc_set)

                # Store in session state
                st.session_state.extraction_result = result
                st.session_state.client_name = client_name
                st.session_state.subtype_name = subtype_name

                st.success("✓ Extraction complete!")
                st.balloons()

            except Exception as e:
                st.error(f"❌ Extraction failed: {e}")
                st.stop()

    # Show results if available
    if "extraction_result" in st.session_state:
        result = st.session_state.extraction_result

        st.header("📋 Results")

        # Token usage
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Input Tokens", f"{result.input_tokens:,}")
        with col2:
            st.metric("Output Tokens", f"{result.output_tokens:,}")

        # Tabs for results
        tab1, tab2 = st.tabs(["🔧 Client Rules (JavaScript)", "📖 Guidelines (Markdown)"])

        with tab1:
            st.code(result.client_rules, language="javascript", line_numbers=True)
            st.download_button(
                label="⬇️ Download client_rules.js",
                data=result.client_rules,
                file_name="client_rules.js",
                mime="text/javascript",
                use_container_width=True,
            )

        with tab2:
            st.markdown(result.guidelines)
            st.download_button(
                label="⬇️ Download guidelines.md",
                data=result.guidelines,
                file_name="guidelines.md",
                mime="text/markdown",
                use_container_width=True,
            )


def _show_help() -> None:
    """Show help information."""
    st.markdown("""
    ## 🎯 How It Works

    1. **Enter client and subtype** in the sidebar
    2. **Upload documents** — multiple files in any supported format
    3. **Review summary** — check document count, tokens, and estimated cost
    4. **Extract** — Claude analyzes all documents together
    5. **Download results** — get client_rules.js and guidelines.md

    ## 📁 What You Get

    - **`client_rules.js`** — Machine-readable validation config
    - **`guidelines.md`** — Human-readable localization guidance

    ## 💡 Tips

    - Group similar documents together (e.g., all gift card content)
    - Mix languages (EN/DE pairs) for better terminology extraction
    - Upload 5-20 documents for best pattern recognition
    - Review the examples in `templates/` to understand output format
    """)


if __name__ == "__main__":
    main()
