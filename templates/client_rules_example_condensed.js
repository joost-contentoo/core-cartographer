// Machine-readable validation rules for Code Checker
// Evidence-based extraction from source documents only

const client_rules = {
  // ===== METADATA =====
  client: "[CLIENT_NAME]",     // Brand/client name
  locale: "[LOCALE]",          // Target language (ISO 639-1: de, nl, fr, etc.)

  // ===== FORBIDDEN WORDS =====
  // Words that MUST NEVER appear (flagged as CRITICAL)
  // Evidence: Conspicuous absence across ALL documents
  forbidden_words: [
    // Example: Formal address when informal is used
    "Sie", "Ihnen", "Ihr",
    // Example: Pressure language brand avoids
    "Beeile dich", "Limitiert"
  ],

  // ===== TERMINOLOGY =====
  // Required translations (flagged if source term appears without target)
  // Evidence: 3+ consistent occurrences (requires source+target pairs)
  // If no pairs: leave empty or minimal
  terminology: [
    { en: "gift card", de: "Gutschein", context: "product term" },
    { en: "redeem", de: "einlösen", context: "use code/voucher" },
    { en: "balance", de: "Guthaben", context: "account credit" }
    // Add more based on observed translations...
  ],

  // ===== PATTERNS =====
  // Formatting rules validated with regex
  // Evidence: 80%+ consistency
  patterns: {
    currency: {
      invalid_patterns: ["\\d+€", "€\\d+"],  // Missing space or wrong order
      valid_format: "X €",
      fix_message: "Use: number + space + € (e.g., '5 €')"
    },
    date_format: {
      invalid_patterns: ["\\d{1,2}/\\d{1,2}/\\d{2,4}"],  // Slash format
      valid_format: "DD.MM.YYYY",
      fix_message: "Use dots: DD.MM.YYYY (e.g., '31.12.2024')"
    }
    // Add list_endings, number_format, etc. if observed...
  },

  // ===== LENGTHS =====
  // Character/word limits per content type
  // Evidence: Observable limits in document structure
  lengths: {
    meta_title: { max_chars: 60, severity: "CRITICAL" },
    meta_description: { max_chars: 154, severity: "CRITICAL" },
    h1: { max_chars: 80, severity: "LOW" }
    // Add FAQ, paragraph limits if consistent patterns found...
  },

  // ===== KEYWORDS (SEO) =====
  // Keyword placement rules for SEO content
  // Evidence: Consistent patterns across SEO docs
  // Omit if content is not SEO-focused
  keywords: {
    primary_placement: {
      h1: true,           // Must appear in H1
      p1_trans: true,     // Must appear in first paragraph
      any_h2: true        // Must appear in at least one H2
    },
    default_counts: {
      primary_min: 5,
      primary_max: 15,
      first_secondary_min: 3,
      secondary_max: 10
    }
  },

  // ===== STRUCTURE =====
  // Required document elements
  // Evidence: 100% presence across documents
  structure: {
    required_tags: ["meta_title", "meta_description", "h1"]
    // Only include truly universal requirements
  }
};

return { client_rules };
