// Contract:
// Input: { content_object OR text_to_audit (string), context, metadata }
//   - context.client_rules: structured validation rules
//   - context.seo_data: keyword requirements (optional)
// Output: { status, issues, stats, debug, content_object, content_string, text_to_audit, context, metadata }

// NOTE: Schema validation (required fields, types) is handled by n8n's Structured Output Parser.
// This validator focuses on BUSINESS LOGIC: lengths, keywords, patterns, terminology, etc.

const input = $json;

// ============================================
// INPUTS
// ============================================

const incomingMetadata = input.metadata || {};
const log = incomingMetadata.log || {};
const contextFromJson = input.context;
const contextFromMetadata = incomingMetadata.context;
const context = contextFromJson || contextFromMetadata || {};

// Extract client rules (structured JSON)
const clientRules = context.client_rules || {};
const hasSeoData = !!(context?.seo_data?.keywords);
const hasClientRules = Object.keys(clientRules).length > 0;

const issues = [];

// ============================================
// HELPERS
// ============================================

function escapeForRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function wordCount(str) {
    if (!str || typeof str !== 'string') return 0;
    return str.trim().split(/\s+/).filter(Boolean).length;
}

/**
 * Normalizes content to both object and string forms
 */
function normalizeContent(input) {
    let content_object = null;
    let content_string = null;

    if (typeof input === 'object' && input !== null) {
        content_object = input;
        content_string = JSON.stringify(input, null, 2);
    } else if (typeof input === 'string') {
        content_string = input;
        try {
            // Try to extract JSON from potential markdown fence
            let jsonStr = input;
            const fenceMatch = input.match(/```(?:json)?\s*([\s\S]*?)```/);
            if (fenceMatch) {
                jsonStr = fenceMatch[1];
            }
            content_object = JSON.parse(jsonStr.trim());
        } catch (e) {
            // Parse failed - content_object stays null
        }
    }

    return { content_object, content_string };
}

/**
 * Builds a map of all text segments with their JSON paths for keyword searching
 */
function buildSegmentsMap(content) {
    const segments = {};

    if (content.meta?.title) {
        segments['meta.title'] = content.meta.title;
    }
    if (content.meta?.description) {
        segments['meta.description'] = content.meta.description;
    }
    if (content.h1) {
        segments['h1'] = content.h1;
    }

    if (Array.isArray(content.sections)) {
        content.sections.forEach((section, index) => {
            if (section.h2) {
                segments[`sections[${index}].h2`] = section.h2;
            }
            if (section.body) {
                segments[`sections[${index}].body`] = section.body;
            }
        });
    }

    if (content.faq_heading) {
        segments['faq_heading'] = content.faq_heading;
    }

    if (Array.isArray(content.faqs)) {
        content.faqs.forEach((faq, index) => {
            if (faq.question) {
                segments[`faqs[${index}].question`] = faq.question;
            }
            if (faq.answer) {
                segments[`faqs[${index}].answer`] = faq.answer;
            }
        });
    }

    return segments;
}

/**
 * Gets full text from all content fields
 */
function getFullText(content) {
    const parts = [
        content.meta?.title,
        content.meta?.description,
        content.h1,
        ...(content.sections || []).flatMap(s => [s.h2, s.body]),
        content.faq_heading,
        ...(content.faqs || []).flatMap(f => [f.question, f.answer])
    ];
    return parts.filter(Boolean).join(' ');
}

// ============================================
// PARSE INPUT
// ============================================

// Try multiple sources for content
let rawContent = input.content_object || input.text_to_audit || input.output;

// Also check metadata for writer's first draft
if (!rawContent && log.writer_first_draft) {
    rawContent = log.writer_first_draft.content_object || log.writer_first_draft;
}

const { content_object, content_string } = normalizeContent(rawContent);

const debug = {
    has_content: !!content_object,
    content_type: content_object ? 'object' : (content_string ? 'string_unparsed' : 'missing'),
    seo_data_found: hasSeoData,
    client_rules_found: hasClientRules,
    client: clientRules.client || 'unknown',
    locale: clientRules.locale || 'unknown',
    context_source: contextFromJson ? 'json.context' : (contextFromMetadata ? 'metadata.context' : 'none'),
};

// ============================================
// VALIDATE INPUT
// ============================================

if (!content_object) {
    issues.push({
        type: 'internal_error',
        severity: 'CRITICAL',
        message: 'Could not parse content as JSON.',
        fix: 'Check workflow: ensure Writer/Refiner output is valid JSON.',
        location: 'global',
    });

    return {
        status: 'FAIL',
        issues,
        stats: {},
        debug,
        content_object: null,
        content_string: content_string || null,
        text_to_audit: content_string || null,
        context,
        metadata: { ...incomingMetadata, context, log: { ...log } },
    };
}

if (!hasSeoData && !hasClientRules) {
    issues.push({
        type: 'configuration_warning',
        severity: 'LOW',
        message: 'No SEO data or client rules found. Only generic checks applied.',
        location: 'global',
    });
}

// ============================================
// BUILD SEGMENTS MAP
// ============================================

const segments = buildSegmentsMap(content_object);
const fullText = getFullText(content_object);

// ============================================
// STRUCTURE VALIDATION (SOFT CHECKS)
// ============================================
// Schema validation is handled by Structured Output Parser.
// We only do soft checks and stats collection here.

const structureStats = {
    section_count: content_object.sections?.length || 0,
    faq_count: content_object.faqs?.length || 0,
    section_types: (content_object.sections || []).map(s => s.type),
    has_transactional: false,
    transactional_index: -1,
};

// Find transactional section
if (Array.isArray(content_object.sections)) {
    const idx = content_object.sections.findIndex(s => s.type === 'transactional');
    if (idx >= 0) {
        structureStats.has_transactional = true;
        structureStats.transactional_index = idx;
    }
}

// Soft warning if no transactional section
if (!structureStats.has_transactional && structureStats.section_count > 0) {
    issues.push({
        type: 'content_recommendation',
        severity: 'LOW',
        message: 'No section marked as "transactional". Consider setting one section type to "transactional" for SEO.',
        fix: 'Change one section\'s type to "transactional" where the primary keyword should appear early.',
        location: 'sections[0].type',
    });
}

// FAQ heading consistency
const hasFaqs = Array.isArray(content_object.faqs) && content_object.faqs.length > 0;
const hasFaqHeading = content_object.faq_heading && content_object.faq_heading.trim().length > 0;

if (hasFaqs && !hasFaqHeading) {
    issues.push({
        type: 'structure_warning',
        severity: 'LOW',
        message: 'FAQs array has items but faq_heading is missing.',
        fix: 'Add a faq_heading field (e.g., "Häufige Fragen")',
        location: 'faq_heading',
    });
}

if (hasFaqHeading && !hasFaqs) {
    issues.push({
        type: 'structure_warning',
        severity: 'LOW',
        message: 'faq_heading exists but faqs array is empty.',
        fix: 'Either add FAQ items or remove faq_heading',
        location: 'faqs',
    });
}

debug.structure = structureStats;

// ============================================
// LENGTH VALIDATION
// ============================================

const lengthRules = clientRules.lengths || {};
const defaultLengthRules = {
    'meta.title': { max_chars: 60, severity: 'CRITICAL' },
    'meta.description': { max_chars: 154, severity: 'CRITICAL' },
};

const lengthStats = {};

// Meta title
if (content_object.meta?.title) {
    const chars = content_object.meta.title.length;
    const rules = lengthRules['meta.title'] || lengthRules['meta_title'] || defaultLengthRules['meta.title'];
    lengthStats['meta.title'] = { chars };

    if (rules?.max_chars && chars > rules.max_chars) {
        issues.push({
            type: 'length_violation',
            severity: rules.severity || 'CRITICAL',
            message: `meta.title has ${chars} characters, max is ${rules.max_chars}.`,
            fix: `Shorten meta.title to max ${rules.max_chars} characters.`,
            location: 'meta.title',
        });
    }
}

// Meta description
if (content_object.meta?.description) {
    const chars = content_object.meta.description.length;
    const rules = lengthRules['meta.description'] || lengthRules['meta_description'] || defaultLengthRules['meta.description'];
    lengthStats['meta.description'] = { chars };

    if (rules?.max_chars && chars > rules.max_chars) {
        issues.push({
            type: 'length_violation',
            severity: rules.severity || 'CRITICAL',
            message: `meta.description has ${chars} characters, max is ${rules.max_chars}.`,
            fix: `Shorten meta.description to max ${rules.max_chars} characters.`,
            location: 'meta.description',
        });
    }
}

// Section bodies
if (Array.isArray(content_object.sections)) {
    content_object.sections.forEach((section, index) => {
        if (section.body) {
            const words = wordCount(section.body);
            const location = `sections[${index}].body`;
            lengthStats[location] = { words };

            if (words > 300) {
                issues.push({
                    type: 'length_violation',
                    severity: 'LOW',
                    message: `${location} has ${words} words, recommended max is 300.`,
                    fix: `Shorten the ${section.type || 'section'} body to ~300 words.`,
                    location: location,
                    section_type: section.type,
                });
            }
        }
    });
}

// FAQ answers
if (Array.isArray(content_object.faqs)) {
    content_object.faqs.forEach((faq, index) => {
        if (faq.answer) {
            const words = wordCount(faq.answer);
            const location = `faqs[${index}].answer`;
            lengthStats[location] = { words };

            if (words > 150) {
                issues.push({
                    type: 'length_violation',
                    severity: 'LOW',
                    message: `${location} has ${words} words, recommended max is 150.`,
                    fix: 'Shorten FAQ answer to ~150 words.',
                    location: location,
                });
            }
        }
    });
}

// ============================================
// PLACEHOLDER + LENGTH CONFLICT DETECTION
// ============================================

if (content_object.meta?.title) {
    const metaTitle = content_object.meta.title;
    const hasCountryCode = metaTitle.includes('{{countryCode}}');
    const hasCountry = metaTitle.includes('{{country}}');
    const currentLength = metaTitle.length;
    const maxLength = lengthRules['meta.title']?.max_chars || lengthRules['meta_title']?.max_chars || 60;

    if (hasCountryCode || hasCountry) {
        const placeholderLength = hasCountryCode ? '{{countryCode}}'.length : '{{country}}'.length;
        const withoutPlaceholderLength = currentLength - placeholderLength;

        if (currentLength > maxLength && withoutPlaceholderLength <= maxLength) {
            issues.push({
                type: 'placeholder_length_conflict',
                severity: 'CRITICAL',
                message: `meta.title is ${currentLength} chars with placeholder (max ${maxLength}). Removing placeholder would be ${withoutPlaceholderLength} chars.`,
                fix: `CHOOSE ONE: (A) Keep placeholder and shorten title to fit ${maxLength} chars total, OR (B) Remove placeholder if country-specificity is not required.`,
                location: 'meta.title',
            });
        }
    } else {
        const estimatedWithPlaceholder = currentLength + 5;

        if (currentLength <= maxLength && estimatedWithPlaceholder > maxLength) {
            issues.push({
                type: 'placeholder_length_conflict',
                severity: 'LOW',
                message: `meta.title is ${currentLength} chars. Adding {{countryCode}} would exceed ${maxLength} chars.`,
                fix: `If country-specific, shorten title to ~${maxLength - 5} chars before adding {{countryCode}}.`,
                location: 'meta.title',
            });
        } else if (currentLength <= maxLength - 15) {
            issues.push({
                type: 'placeholder_suggestion',
                severity: 'LOW',
                message: 'meta.title has no country placeholder. Consider adding {{countryCode}} or {{country}} if relevant.',
                fix: 'Add {{countryCode}} or {{country}} to meta.title if this product is country-specific.',
                location: 'meta.title',
            });
        }
    }
}

// ============================================
// KEYWORD VALIDATION
// ============================================

const keywordStats = {
    keywords_found: {},
    keywords_by_location: {},
    primary_keyword: null,
    keywords_in_h1: [],
    keywords_in_transactional: [],
    keywords_in_h2s: [],
};

if (hasSeoData) {
    const seoData = context.seo_data;
    const keywordRules = clientRules.keywords || {};
    const placementRules = keywordRules.primary_placement || {};

    const validationRules = seoData.validation_rules || {
        primary_in_h1: placementRules.h1 !== false,
        primary_in_first_paragraph: placementRules.p1_trans !== false,
        primary_in_subheading: placementRules.any_h2 !== false,
    };

    // Find transactional section body for keyword placement check
    const transactionalIndex = structureStats.transactional_index >= 0
        ? structureStats.transactional_index
        : 0;
    const transactionalBodyKey = `sections[${transactionalIndex}].body`;

    // Get all h2 keys
    const h2Keys = Object.keys(segments).filter(k => k.endsWith('.h2'));

    let primaryKeyword = null;

    for (const keyword of seoData.keywords) {
        const term = keyword.term;
        const minCount = keyword.min_count || 1;
        const maxCount = keyword.max_count || 20;
        const isPrimary = keyword.type === 'primary';

        if (!term) continue;

        if (isPrimary) {
            primaryKeyword = term;
            keywordStats.primary_keyword = term;
        }

        const escaped = escapeForRegex(term);
        const regex = new RegExp(escaped, 'gi');

        // Total count
        const totalMatches = fullText.match(regex);
        const totalCount = totalMatches ? totalMatches.length : 0;
        keywordStats.keywords_found[term] = totalCount;

        // Per-location counts
        keywordStats.keywords_by_location[term] = {};
        for (const [location, text] of Object.entries(segments)) {
            const matches = text.match(regex);
            if (matches && matches.length > 0) {
                keywordStats.keywords_by_location[term][location] = matches.length;
            }
        }

        // Track h1, transactional, h2 presence
        if (segments['h1'] && regex.test(segments['h1'])) {
            keywordStats.keywords_in_h1.push(term);
        }
        if (segments[transactionalBodyKey] && regex.test(segments[transactionalBodyKey])) {
            keywordStats.keywords_in_transactional.push(term);
        }
        for (const h2Key of h2Keys) {
            if (regex.test(segments[h2Key])) {
                if (!keywordStats.keywords_in_h2s.includes(term)) {
                    keywordStats.keywords_in_h2s.push(term);
                }
            }
        }

        // Count validation
        if (totalCount < minCount) {
            issues.push({
                type: 'keyword_missing',
                severity: 'CRITICAL',
                message: `Keyword "${term}" appears ${totalCount}x, minimum: ${minCount}.`,
                fix: `Add "${term}" ${minCount - totalCount} more time(s) naturally.`,
                keyword: term,
                keyword_type: keyword.type,
                location: 'global',
            });
        }

        if (totalCount > maxCount) {
            issues.push({
                type: 'keyword_density',
                severity: 'CRITICAL',
                message: `Keyword "${term}" appears ${totalCount}x, maximum: ${maxCount}.`,
                fix: `Reduce "${term}" to max ${maxCount} occurrences.`,
                keyword: term,
                keyword_type: keyword.type,
                location: 'global',
            });
        }
    }

    // Primary keyword placement checks
    if (primaryKeyword) {
        if (validationRules.primary_in_h1 && !keywordStats.keywords_in_h1.includes(primaryKeyword)) {
            issues.push({
                type: 'keyword_placement',
                severity: 'CRITICAL',
                message: `Primary keyword "${primaryKeyword}" missing from h1.`,
                fix: `Add "${primaryKeyword}" to the h1 field.`,
                keyword: primaryKeyword,
                location: 'h1',
            });
        }

        if (validationRules.primary_in_first_paragraph && !keywordStats.keywords_in_transactional.includes(primaryKeyword)) {
            issues.push({
                type: 'keyword_placement',
                severity: 'CRITICAL',
                message: `Primary keyword "${primaryKeyword}" missing from transactional section.`,
                fix: `Add "${primaryKeyword}" early in the transactional section body.`,
                keyword: primaryKeyword,
                location: transactionalBodyKey,
                section_type: 'transactional',
            });
        }

        if (validationRules.primary_in_subheading && !keywordStats.keywords_in_h2s.includes(primaryKeyword)) {
            issues.push({
                type: 'keyword_placement',
                severity: 'CRITICAL',
                message: `Primary keyword "${primaryKeyword}" missing from all section headings.`,
                fix: `Add "${primaryKeyword}" to at least one section h2.`,
                keyword: primaryKeyword,
                location: 'sections[*].h2',
            });
        }
    }
}

// ============================================
// FORBIDDEN WORDS
// ============================================

const forbiddenStats = {
    forbidden_words_found: 0,
    words_detected: [],
};

const forbiddenWords = clientRules.forbidden_words || [];

for (const word of forbiddenWords) {
    const regex = new RegExp(`\\b${escapeForRegex(word)}\\b`, 'gi');
    const matches = fullText.match(regex);

    if (matches && matches.length > 0) {
        issues.push({
            type: 'forbidden_word',
            severity: 'CRITICAL',
            message: `Forbidden word "${word}" found ${matches.length}x.`,
            fix: `Remove/replace "${word}" throughout. Use informal "du" forms instead of formal address.`,
            term: word,
            location: 'global',
        });
        forbiddenStats.forbidden_words_found += matches.length;
        forbiddenStats.words_detected.push(word);
    }
}

// ============================================
// PATTERN VALIDATION (Currency, Lists)
// ============================================

const patternStats = { checked: 0, passed: 0, failed: 0 };
const patterns = clientRules.patterns || {};

// Currency validation
if (patterns.currency) {
    const currencyPatterns = patterns.currency.invalid_patterns || ['\\d+€', '€\\d+'];
    const fixMessage = patterns.currency.fix_message || 'Use correct currency format: number + space + euro sign (e.g., "5 €").';

    for (const pattern of currencyPatterns) {
        patternStats.checked++;
        const regex = new RegExp(pattern, 'g');
        const matches = fullText.match(regex);

        if (matches && matches.length > 0) {
            issues.push({
                type: 'pattern_violation',
                severity: 'CRITICAL',
                message: `Currency format error: ${matches.length}x invalid (e.g., "${matches[0]}").`,
                fix: fixMessage,
                location: 'global',
            });
            patternStats.failed++;
        } else {
            patternStats.passed++;
        }
    }
}

// List endings validation - check each section/FAQ body
if (patterns.list_endings) {
    const requiredEndings = patterns.list_endings.required || ['Fertig!', "Das war's!"];
    const listFixMessage = patterns.list_endings.fix_message || `End numbered lists with "${requiredEndings[0]}".`;

    const listStats = { found: 0, valid: 0, invalid: 0 };
    const listRegex = /(?:^|\n)(1[.)]\s+[\s\S]+?)(?=\n\n|$)/g;

    // Build list of texts to check with their locations
    const textsToCheck = [];

    if (Array.isArray(content_object.sections)) {
        content_object.sections.forEach((s, i) => {
            if (s.body) {
                textsToCheck.push({ text: s.body, location: `sections[${i}].body` });
            }
        });
    }

    if (Array.isArray(content_object.faqs)) {
        content_object.faqs.forEach((f, i) => {
            if (f.answer) {
                textsToCheck.push({ text: f.answer, location: `faqs[${i}].answer` });
            }
        });
    }

    for (const { text, location } of textsToCheck) {
        let listMatch;
        listRegex.lastIndex = 0; // Reset regex state

        while ((listMatch = listRegex.exec(text)) !== null) {
            listStats.found++;
            const listContent = listMatch[1].trim();
            const items = listContent.split(/\n(?=\d+[.)]\s+)/);
            const lastItem = items[items.length - 1] || '';
            const hasValidEnding = requiredEndings.some(ending => lastItem.includes(ending));

            if (hasValidEnding) {
                listStats.valid++;
            } else {
                listStats.invalid++;
                issues.push({
                    type: 'pattern_violation',
                    severity: 'CRITICAL',
                    message: `Numbered list in ${location} doesn't end with required phrase.`,
                    fix: listFixMessage,
                    location: location,
                });
            }
        }
    }

    debug.list_stats = listStats;
}

// ============================================
// TERMINOLOGY VALIDATION
// ============================================

const terminologyStats = { checked: 0, valid: 0, invalid: 0 };
const terminology = clientRules.terminology || [];

if (terminology.length > 0) {
    // Remove URLs from text before checking terminology
    const textWithoutUrls = fullText
        .replace(/https?:\/\/[^\s\]\)]+/g, '')
        .replace(/\[[^\]]*\]\([^\)]+\)/g, '');

    for (const term of terminology) {
        const englishTerm = term.en;
        const germanRequired = term.de;
        const contextHint = term.context || '';

        if (!englishTerm || !germanRequired) continue;
        terminologyStats.checked++;

        const englishRegex = new RegExp(`\\b${escapeForRegex(englishTerm)}\\b`, 'gi');
        const englishMatches = textWithoutUrls.match(englishRegex);

        if (englishMatches && englishMatches.length > 0) {
            const germanRegex = new RegExp(escapeForRegex(germanRequired), 'gi');
            const germanMatches = fullText.match(germanRegex);

            if (!germanMatches || germanMatches.length === 0) {
                issues.push({
                    type: 'terminology_error',
                    severity: 'CRITICAL',
                    message: `English "${englishTerm}" found but German "${germanRequired}" missing${contextHint ? ` (${contextHint})` : ''}.`,
                    fix: `Replace "${englishTerm}" with "${germanRequired}".`,
                    english: englishTerm,
                    german_required: germanRequired,
                    location: 'global',
                });
                terminologyStats.invalid++;
            } else {
                terminologyStats.valid++;
            }
        } else {
            terminologyStats.valid++;
        }
    }
}

// ============================================
// BUILD RESULT
// ============================================

const hasNonLowIssues = issues.some(i => i.severity && i.severity !== 'LOW');
const status = hasNonLowIssues ? 'FAIL' : 'PASS';

const stats = {
    keywords: keywordStats,
    forbidden_words: forbiddenStats,
    patterns: patternStats,
    terminology: terminologyStats,
    lengths: lengthStats,
    structure: structureStats,
};

// ============================================
// OUTPUT
// ============================================

return {
    status,
    issues,
    stats,
    debug,
    content_object,
    content_string,
    text_to_audit: content_string,  // For backward compatibility
    context,
    metadata: { ...incomingMetadata, context, log: { ...log } },
};
