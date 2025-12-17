// Contract:
// Input: none
// Output: { client_rules: {...structured rules for code checker...} }

// ============================================
// CLIENT RULES CONFIGURATION
// ============================================
// This structured config drives the Code Checker validations.
// To adapt for a new client/locale:
// 1. Copy this file
// 2. Update the rules below
// 3. Load the appropriate config in your workflow
// ============================================

const client_rules = {
  // ==========================================
  // CLIENT METADATA
  // ==========================================
  // Override these per client/locale
  client: "default",
  locale: "de",

  // ==========================================
  // FORBIDDEN WORDS
  // ==========================================
  // Words that must NEVER appear in the output.
  // Code Checker will flag these as CRITICAL errors.
  forbidden_words: [
    // Formal German address (we use informal "du")
    "Sie",
    "Ihnen",
    "Ihr",
    "Ihre",
    "Ihrem",
    "Ihren",
    "Ihrer"
  ],

  // ==========================================
  // TERMINOLOGY MAPPING
  // ==========================================
  // English terms that MUST be translated to specific German equivalents.
  // If English term is found without German equivalent, it's a CRITICAL error.
  terminology: [
    { en: "gift card", de: "Gutschein", context: "general product term" },
    { en: "voucher", de: "Gutschein", context: "alternative to gift card" },
    { en: "redeem", de: "einlösen", context: "action verb" },
    { en: "top up", de: "aufladen", context: "adding credit" },
    { en: "top-up", de: "Aufladung", context: "noun form" },
    { en: "balance", de: "Guthaben", context: "account balance" },
    { en: "credit", de: "Guthaben", context: "prepaid credit" },
    { en: "checkout", de: "Kasse", context: "payment process" },
    { en: "cart", de: "Warenkorb", context: "shopping cart" },
    { en: "delivery", de: "Lieferung", context: "digital delivery" },
    { en: "instant delivery", de: "Sofortlieferung", context: "immediate fulfillment" },
    { en: "customer service", de: "Kundenservice", context: "support" },
    { en: "payment method", de: "Zahlungsart", context: "how to pay" }
  ],

  // ==========================================
  // PATTERN RULES
  // ==========================================
  // Formatting patterns that must be followed.
  patterns: {
    // Currency formatting: German uses "X €" (number + space + euro sign)
    currency: {
      invalid_patterns: [
        "\\d+€",      // Missing space: "5€"
        "€\\d+"       // Euro before number: "€5"
      ],
      valid_format: "X €",
      fix_message: "Use German currency format: number + space + euro sign (e.g., '5 €', '10 €')"
    },

    // Numbered lists must end with closure phrase
    list_endings: {
      required: ["Fertig!", "Das war's!"],
      fix_message: "End numbered lists with 'Fertig!' or 'Das war's!' for psychological closure"
    }
  },

  // ==========================================
  // LENGTH LIMITS
  // ==========================================
  // Maximum lengths per tag. Exceeding these triggers validation errors.
  // Note: The code checker also applies pattern-based defaults:
  //   - All p*_ tags: max 300 words (LOW severity)
  //   - All faq*_answer tags: max 150 words (LOW severity)
  lengths: {
    // Meta tags - character limits (for SEO)
    meta_title: {
      max_chars: 60,
      severity: "CRITICAL"
    },
    meta_description: {
      max_chars: 154,
      severity: "CRITICAL"
    }
    // Body section limits are applied dynamically via pattern matching
    // in the code checker - no need to enumerate them here
  },

  // ==========================================
  // KEYWORD RULES
  // ==========================================
  // SEO keyword placement and density rules.
  keywords: {
    // Where primary keyword MUST appear
    primary_placement: {
      h1: true,
      p1_trans: true,
      any_h2: true
    },

    // Count limits (can be overridden by SEO data)
    default_counts: {
      primary_min: 5,
      primary_max: 15,
      first_secondary_min: 3,
      other_secondary_min: 2,
      secondary_max: 10
    }
  },

  // ==========================================
  // STRUCTURE RULES
  // ==========================================
  // Only truly required tags are enforced.
  // The code checker discovers tags dynamically from content,
  // validates consistency (e.g., faq3_question requires faq3_answer),
  // but does NOT enforce a fixed schema.
  structure: {
    // These tags MUST be present - everything else is flexible
    required_tags: ["meta_title", "meta_description", "h1"]

    // NOTE: schema_tags removed - the code checker now discovers
    // tags dynamically instead of checking against a fixed list.
    // This allows flexible content: 0-N FAQs, 0-N extra sections, etc.
  }
};

// ============================================
// OUTPUT
// ============================================

return {
  client_rules
};
