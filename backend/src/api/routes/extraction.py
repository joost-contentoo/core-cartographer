"""Extraction endpoints with SSE streaming support."""

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from core_cartographer.config import get_settings
from core_cartographer.cost_estimator import estimate_cost
from core_cartographer.extractor import extract_rules_and_guidelines
from core_cartographer.models import Document, DocumentSet

from ...cache.file_cache import file_cache
from ..dependencies import handle_anthropic_error, logger
from ..models.requests import ExtractionRequest

router = APIRouter()


@router.post("/extract-stream")
async def extract_with_streaming(request: ExtractionRequest):
    """
    Extract rules and guidelines with SSE progress streaming.

    This endpoint returns a Server-Sent Events stream with the following event types:

    - `started`: Extraction begun. Fields: `subtypes` (list of subtypes to process)
    - `progress`: Processing update. Fields: `subtype`, `current`, `total`
    - `subtype_complete`: One subtype finished. Fields: `subtype`, `current`, `total`
    - `subtype_error`: One subtype failed. Fields: `subtype`, `message`
    - `complete`: All done. Fields: `results`, `total_input_tokens`, `total_output_tokens`, `total_cost`
    - `error`: Fatal error. Fields: `message`

    Args:
        request: Extraction configuration with document sets

    Returns:
        StreamingResponse with Server-Sent Events (text/event-stream)
    """
    async def event_stream():
        try:
            # Validate request
            if not request.client_name:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Client name is required'})}\n\n"
                return

            if not request.document_sets or len(request.document_sets) == 0:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No document sets provided'})}\n\n"
                return

            settings = get_settings()
            settings.debug_mode = request.debug_mode
            settings.batch_processing = request.batch_processing

            logger.info(f"Starting extraction for client: {request.client_name}")

            # Build document sets from file_ids
            document_sets = []
            for ds_req in request.document_sets:
                if not ds_req.files or len(ds_req.files) == 0:
                    logger.warning(f"Skipping empty document set: {ds_req.subtype}")
                    continue

                documents = []
                for file_ref in ds_req.files:
                    cached = file_cache.get(file_ref.file_id)
                    if not cached:
                        error_msg = f"File not found in cache: {file_ref.file_id}"
                        logger.error(error_msg)
                        yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                        return

                    documents.append(Document(
                        filename=cached.filename,
                        content=cached.content,
                        language=file_ref.language,
                        pair_id=file_ref.pair_id,
                        tokens=cached.tokens
                    ))

                document_sets.append(DocumentSet(
                    client_name=request.client_name,
                    subtype=ds_req.subtype,
                    documents=documents,
                    total_tokens=sum(d.tokens for d in documents)
                ))

            if not document_sets:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No valid document sets to process'})}\n\n"
                return

            # Send started event
            subtypes = [ds.subtype for ds in document_sets]
            logger.info(f"Processing {len(subtypes)} subtypes: {subtypes}")
            yield f"data: {json.dumps({'type': 'started', 'subtypes': subtypes})}\n\n"

            results = {}
            total = len(document_sets)

            for i, doc_set in enumerate(document_sets):
                try:
                    # Send progress event
                    yield f"data: {json.dumps({'type': 'progress', 'subtype': doc_set.subtype, 'current': i, 'total': total})}\n\n"

                    logger.info(f"Extracting subtype {i+1}/{total}: {doc_set.subtype}")

                    # Run extraction (this blocks, but we're in async context)
                    result = await asyncio.to_thread(
                        extract_rules_and_guidelines, settings, doc_set
                    )

                    results[doc_set.subtype] = {
                        "client_rules": result.client_rules,
                        "guidelines": result.guidelines,
                        "input_tokens": result.input_tokens,
                        "output_tokens": result.output_tokens
                    }

                    # Send subtype complete event
                    yield f"data: {json.dumps({'type': 'subtype_complete', 'subtype': doc_set.subtype, 'current': i + 1, 'total': total})}\n\n"

                except Exception as e:
                    # Handle Anthropic API errors specifically
                    error = handle_anthropic_error(e)
                    error_msg = f"Failed to extract {doc_set.subtype}: {error.detail}"
                    logger.error(error_msg)
                    # Send error for this subtype but continue processing others
                    yield f"data: {json.dumps({'type': 'subtype_error', 'message': error_msg, 'subtype': doc_set.subtype})}\n\n"
                    # Continue to next subtype instead of returning
                    continue

            # Calculate totals (only from successful results)
            if not results:
                yield f"data: {json.dumps({'type': 'error', 'message': 'All extractions failed'})}\n\n"
                return

            total_input = sum(r["input_tokens"] for r in results.values())
            total_output = sum(r["output_tokens"] for r in results.values())
            total_cost = estimate_cost(total_input, total_output, settings.model)

            logger.info(f"Extraction complete: {total_input} input tokens, {total_output} output tokens, ${total_cost:.2f}")

            # Send complete event with all results
            yield f"data: {json.dumps({'type': 'complete', 'results': results, 'total_input_tokens': total_input, 'total_output_tokens': total_output, 'total_cost': total_cost})}\n\n"

        except Exception as e:
            logger.error(f"Extraction stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Extraction failed: {str(e)}'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
