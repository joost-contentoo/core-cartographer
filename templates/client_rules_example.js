// ============================================================================
// CLIENT RULES CONFIGURATION
// ============================================================================
//
// This file defines machine-readable validation rules consumed by the Code
// Checker. Each section has specific validation behavior documented below.
//
// Contract:
//   Input: none
//   Output: { client_rules: {...structured rules for code checker...} }
//
// ============================================================================

const client_rules = {
  // ==========================================================================
  // METADATA
  // ==========================================================================
  // Identifies this ruleset. Used for logging and rule selection.

  client: "dundle",           // Client/brand name
  locale: "de",               // Primary target language (ISO 639-1)

  // ==========================================================================
  // FORBIDDEN WORDS
  // ==========================================================================
  // Words that MUST NEVER appear in target content.
  // Code Checker: Flags each occurrence as CRITICAL error.
  //
  // How to extract:
  // - Formal address forms when content consistently uses informal (du vs Sie)
  // - Competitor brand names never mentioned
  // - Negative/pressure language conspicuously absent from all documents
  // - Marketing buzzwords the brand avoids
  //
  // Evidence needed: Word must be absent from ALL analyzed documents.
  // ==========================================================================

  forbidden_words: [
    // Formal German address - brand uses informal "du" throughout
    "Sie",
    "Ihnen",
    "Ihr",
    "Ihre",
    "Ihrem",
    "Ihren",
    "Ihrer",
    // Pressure language the brand avoids
    "Beeile dich",
    "Limitiert",
    "Nur noch heute"
  ],

  // ==========================================================================
  // TERMINOLOGY
  // ==========================================================================
  // Required translations for specific terms.
  // Code Checker: If English term found WITHOUT German equivalent nearby,
  //               flags as CRITICAL error.
  //
  // How to extract:
  // - REQUIRES source+target language pairs to identify translations
  // - Find terms translated consistently 3+ times across documents
  // - Include 'context' when same English word has multiple German translations
  //   (e.g., "balance" → "Guthaben" for account, "Gleichgewicht" for physical)
  //
  // Evidence needed: 3+ consistent translation occurrences across documents.
  // If no language pairs available: Leave this section empty or minimal.
  // ==========================================================================

  terminology: [
    // Product terms
    { en: "gift card", de: "Gutschein", context: "general product term" },
    { en: "voucher", de: "Gutschein", context: "alternative to gift card" },
    { en: "prepaid card", de: "Prepaid-Karte", context: "payment product" },

    // Actions
    { en: "redeem", de: "einlösen", context: "using a code/voucher" },
    { en: "top up", de: "aufladen", context: "adding credit (verb)" },
    { en: "top-up", de: "Aufladung", context: "adding credit (noun)" },

    // Account/payment terms
    { en: "balance", de: "Guthaben", context: "account/credit balance" },
    { en: "credit", de: "Guthaben", context: "prepaid credit" },
    { en: "checkout", de: "Kasse", context: "payment process" },
    { en: "cart", de: "Warenkorb", context: "shopping cart" },

    // Delivery/service
    { en: "instant delivery", de: "Sofortlieferung", context: "immediate fulfillment" },
    { en: "delivery", de: "Lieferung", context: "digital delivery" },
    { en: "customer service", de: "Kundenservice", context: "support contact" },
    { en: "payment method", de: "Zahlungsart", context: "how to pay" }
  ],

  // ==========================================================================
  // PATTERNS
  // ==========================================================================
  // Formatting rules validated with regex patterns.
  // Code Checker: Tests each pattern, flags violations at specified severity.
  //
  // How to extract:
  // - Currency format: Is it "€5", "5€", "5 €", or "5,00 €"?
  // - Date format: DD.MM.YYYY vs DD/MM/YYYY vs other
  // - Number format: 1.000 (German) vs 1,000 (English)
  // - List endings: Do numbered lists end with "Fertig!" or similar?
  // - Punctuation: Ellipsis style, quote marks, etc.
  //
  // Evidence needed: 80%+ consistency across occurrences.
  // ==========================================================================

  patterns: {
    // Currency: German uses "X €" (number + space + euro sign)
    currency: {
      invalid_patterns: [
        "\\d+€",           // Missing space: "5€"
        "€\\d+",           // Euro before number: "€5"
        "€\\s*\\d+",       // Euro before with optional space: "€ 5"
        "EUR\\s*\\d+"      // EUR prefix: "EUR 5"
      ],
      valid_format: "X €",
      fix_message: "German currency format: number + space + euro sign (e.g., '5 €', '10,00 €')"
    },

    // Numbered lists should end with psychological closure phrase
    list_endings: {
      required: ["Fertig!", "Das war's!", "Geschafft!"],
      fix_message: "End numbered instruction lists with 'Fertig!' or 'Das war's!' for closure"
    },

    // Date format (if dates appear in content)
    date_format: {
      invalid_patterns: [
        "\\d{1,2}/\\d{1,2}/\\d{2,4}",   // Slash format: 12/31/2024
        "\\d{4}-\\d{2}-\\d{2}"           // ISO format: 2024-12-31
      ],
      valid_format: "DD.MM.YYYY",
      fix_message: "German date format: DD.MM.YYYY (e.g., '31.12.2024')"
    }
  },

  // ==========================================================================
  // LENGTHS
  // ==========================================================================
  // Character and word limits per content type.
  // Code Checker: Measures content length, flags violations at specified severity.
  //
  // Severities:
  // - CRITICAL: Hard limit, must not exceed (e.g., SEO meta tags)
  // - LOW: Soft recommendation, can exceed with good reason
  //
  // How to extract:
  // - Meta titles: Typically 50-60 chars for SEO
  // - Meta descriptions: Typically 150-160 chars
  // - Body paragraphs: Observe typical lengths in documents
  // - FAQ answers: Observe typical lengths in documents
  //
  // Evidence needed: Observable limits in document structure.
  // ==========================================================================

  lengths: {
    // SEO meta tags - hard limits
    meta_title: {
      max_chars: 60,
      severity: "CRITICAL"
    },
    meta_description: {
      max_chars: 154,
      severity: "CRITICAL"
    },

    // Body content - soft recommendations
    // (Code checker applies pattern-based defaults for sections/FAQs)
    h1: {
      max_chars: 80,
      severity: "LOW"
    }
  },

  // ==========================================================================
  // KEYWORDS (SEO)
  // ==========================================================================
  // Rules for keyword placement in SEO content.
  // Code Checker: Verifies keywords appear in required locations.
  //
  // How to extract:
  // - Observe where primary keywords consistently appear (H1, intro, H2s)
  // - Note density patterns (how many times keywords repeat)
  //
  // Evidence needed: Consistent placement patterns across SEO documents.
  // If content is not SEO-focused: This section can be minimal or omitted.
  // ==========================================================================

  keywords: {
    // Where primary keyword MUST appear
    primary_placement: {
      h1: true,                // Must be in main heading
      p1_trans: true,          // Must be in first/transactional paragraph
      any_h2: true             // Must be in at least one subheading
    },

    // Count limits (can be overridden by SEO data per document)
    default_counts: {
      primary_min: 5,          // Minimum occurrences of primary keyword
      primary_max: 15,         // Maximum (avoid keyword stuffing)
      first_secondary_min: 3,  // First secondary keyword minimum
      other_secondary_min: 2,  // Other secondary keywords minimum
      secondary_max: 10        // Maximum for any secondary keyword
    }
  },

  // ==========================================================================
  // STRUCTURE
  // ==========================================================================
  // Required document elements.
  // Code Checker: Verifies these tags/fields are present.
  //
  // How to extract:
  // - Identify tags/sections present in EVERY document
  // - Note required metadata fields
  //
  // Evidence needed: 100% presence across all analyzed documents.
  // Only include truly universal requirements.
  // ==========================================================================

  structure: {
    // Tags that MUST be present in every document
    required_tags: [
      "meta_title",
      "meta_description",
      "h1"
    ]

    // Note: Code checker discovers other tags dynamically.
    // It validates consistency (e.g., faq3_question requires faq3_answer)
    // but doesn't enforce a fixed schema beyond required_tags.
  }
};

// ============================================================================
// OUTPUT
// ============================================================================

return { client_rules };
