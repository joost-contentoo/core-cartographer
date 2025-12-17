# German Localization Guidelines for dundle

> **Purpose**: This guide enables writers and LLMs to create German content that matches dundle's brand voice, style, and cultural expectations. Use alongside `client_rules.js` for automated validation.

---

## 1. Purpose & Scope

**What this covers**: German localization of dundle product pages, marketing content, and customer-facing copy for the DACH market (Germany, Austria, Switzerland).

**Content types**: Product descriptions, FAQ sections, benefit lists, CTAs, meta tags, and instructional content.

**Key principle**: German content is an **adaptation**, not a direct translation. Structure, emphasis, and detail level should match German reader expectations.

---

## 2. Core Philosophy

### Localization vs Translation

German readers have different information needs and reading patterns. Successful localization means:

| Aspect | What to Do |
|--------|------------|
| **Restructure** | Adapt for scannability and directness |
| **Expand** | Add detail where Germans expect it (fees, steps, regulations) |
| **Condense** | Shorten where English is verbose (marketing fluff) |
| **Adapt tone** | Match German digital commerce expectations |

**Typical result**: German versions differ 10-20% in structure from English source.

### Example Transformation

**English (verbose, promotional)**:
> Looking to top up your account without using a credit card? Buy a gift card and add prepaid credit quickly and securely!

**German (direct, specific)**:
> Möchtest du dein Konto aufladen? Bei dundle kaufst du bequem mit PayPal, Klarna oder 15 weiteren Zahlungsarten.

**What changed**:
- Shorter question (direct to the point)
- Named specific payment methods (concrete value)
- "bequem" as key benefit (practical, not promotional)
- Removed exclamation-heavy enthusiasm

---

## 3. Brand Voice

### Tone Profile

dundle speaks as a **knowledgeable friend** who understands digital products:

| Quality | How to Express |
|---------|----------------|
| **Confident** | State facts clearly, no hedging |
| **Helpful** | Anticipate questions, provide solutions |
| **Direct** | Get to the point, respect reader's time |
| **Reassuring** | Emphasize security without being alarmist |
| **Modern** | Comfortable with digital, don't over-explain basics |

### Emotional Register

German digital commerce copy is **pragmatic**, not **promotional**.

**Avoid**:
- Excessive enthusiasm: "Amazing!", "Incredible!", "Wow!"
- Hyperbole: "The best ever!", "Unbeatable!"
- Pressure tactics: "Don't miss out!", "Limited time!", "Hurry!"

**Instead, convey value through**:
- Clarity about benefits
- Concrete examples with numbers
- Practical information
- Trustworthy, straightforward tone

### Voice Examples

| Situation | Avoid | Use Instead |
|-----------|-------|-------------|
| Introducing product | "Get ready for an amazing experience!" | "Mit diesem Gutschein erhältst du sofort Zugang." |
| Highlighting speed | "Lightning-fast delivery!" | "Sofort per E-Mail, in Sekunden einlösbar." |
| Encouraging action | "Don't wait, buy now!" | "Jetzt kaufen und direkt einlösen." |

---

## 4. Writing Style

### Address: Always "du"

dundle uses **informal "du"** throughout all German content. This is deliberate:
- Creates approachability
- Matches digital-native audience expectations
- Aligns with modern German e-commerce conventions

**Rule**: Never mix "du" and "Sie". Maintain consistency in ALL verb conjugations and possessives.

**Correct**: "Gib deinen Code ein und bestätige deine E-Mail."
**Wrong**: "Geben Sie Ihren Code ein und bestätige deine E-Mail."

> **Note**: All formal address forms (Sie, Ihnen, Ihr, etc.) are flagged by the Code Checker. See `client_rules.js` → `forbidden_words`.

### Sentence Structure

German readers scanning product pages prefer:
- **Shorter sentences** than typical English marketing
- **Front-loaded information** (key point first, context second)
- **Active voice** with clear subjects
- **Specific details** over vague promises

**Transformation example**:

| English | German |
|---------|--------|
| "With our amazing service, you can easily and quickly purchase products that will be delivered to your inbox instantly, allowing you to start using them right away!" | "Bei dundle erhältst du deinen Code sofort per E-Mail. Direkt einlösbar, ohne Wartezeit." |

### Questions as Section Openers

German pages frequently use rhetorical questions to open sections:

- "Möchtest du...?" (Do you want to...?)
- "Suchst du...?" (Are you looking for...?)
- "Brauchst du...?" (Do you need...?)

**Pattern**: Question → dundle as solution

> "Möchtest du dein Konto aufladen? Dann bist du bei dundle genau richtig!"

### Conveying Urgency

German readers respond to **practical urgency** (speed, convenience), not **artificial urgency** (scarcity, FOMO).

**Effective**:
- "Sofort per E-Mail" (Instant via email)
- "Direkt einlösbar" (Immediately redeemable)
- "In Sekunden" (In seconds)
- "24/7 verfügbar" (Available 24/7)

**Avoid**:
- "Nur noch heute!" (Only today!)
- "Beeile dich!" (Hurry up!)
- "Limitiertes Angebot" (Limited offer)

---

## 5. Content Structure

### German Reader Journey

Typical reading pattern for product pages:

1. **Scan headline** → Is this what I'm looking for?
2. **Check price/availability** → Can I get this?
3. **Read intro** → Quick confirmation
4. **Jump to FAQ** → Specific questions
5. **Return to instructions** → How exactly do I do this?

**Structure content for non-linear reading**: Clear headings, self-contained sections, scannable formats.

### Required Sections

| Section | Purpose | Format |
|---------|---------|--------|
| **Intro paragraph** | Quick value summary | 2-3 sentences, front-load key benefit |
| **Benefits (Vorteile)** | Trust signals, differentiation | Bullet points, standalone statements |
| **How to use** | Step-by-step instructions | Numbered list, end with "Fertig!" |
| **FAQ** | Answer real questions | Natural questions, direct answers |

### Instruction Depth

German readers expect **detailed, practical instructions**.

**English style**:
> "Redeem your code on the platform's website."

**German style**:
> 1. Besuche die Einlöseseite unter [URL].
> 2. Gib deinen 16-stelligen Code ein.
> 3. Bestätige deine Eingabe.
> 4. Fertig! Das Guthaben wurde gutgeschrieben.

**Key elements**:
- Numbered steps (not prose)
- Specific details (16-digit code, not just "code")
- "Fertig!" at the end for psychological closure

> **Note**: List ending phrases are validated by Code Checker. See `client_rules.js` → `patterns.list_endings`.

---

## 6. Cultural Context

### Payment Method Priorities

German consumers have distinct preferences. When mentioning payment options, prioritize:

1. **PayPal** – Most trusted online payment in Germany
2. **Klarna Sofortüberweisung** – German-specific, widely used
3. **Apple Pay** – Growing rapidly
4. **Handyrechnung** – Popular for digital goods

**Note**: Credit cards are less common than in UK/US. Emphasize alternatives.

### Privacy & Security

German consumers are particularly privacy-conscious. Effective reassurance:

- "Ohne Bank- oder Kreditkartendaten teilen zu müssen"
- "Sicher und anonym bezahlen"
- "Volle Kostenkontrolle"
- "Keine Weitergabe persönlicher Daten"

This isn't fear-mongering—it acknowledges a genuine cultural value.

### Fee Transparency

German readers expect **explicit fee information**. Vague statements are insufficient.

**Provide**:
- Specific percentages where applicable
- Concrete euro examples when helpful
- When fees apply (conditions, time periods)
- What's included vs extra

**Example**:
> "Die Einlösegebühr beträgt 10%. Bei einem Gutschein über 50 € erhältst du 45 € Guthaben."

### Regional Awareness

Address regional considerations proactively:

- Does this work in Germany/Austria/Switzerland?
- Are codes region-locked?
- Currency implications (EUR vs other)
- Is German customer service available?

---

## 7. Content Type Variations

### Payment/Financial Products

**Tone**: Trustworthy, security-focused, slightly more formal within "du" context
**Emphasis**: Privacy, anonymity, accepted platforms, fee transparency

**Example intro**:
> "Mit Paysafecard bezahlst du online sicher und anonym – ganz ohne Bankdaten. Ideal für alle, die ihre Privatsphäre schützen möchten."

### Gift Products

**Tone**: Friendly, gift-oriented, convenience-focused
**Emphasis**: Flexibility, ease of gifting, recipient experience

**Example intro**:
> "Ein Geschenk, das immer passt: Mit dem [Brand] Gutschein kann sich der Beschenkte selbst aussuchen, was er möchte."

### Gaming Products

**Tone**: Enthusiastic (within German norms), community-aware
**Emphasis**: What you can do with it, compatibility, value

**Example intro**:
> "Hol dir V-Bucks für Fortnite und sichere dir die neuesten Skins, Emotes und den Battle Pass."

---

## 8. FAQ Writing

### Question Formulation

Use natural German question forms:

- "Wie kann ich...?" (How can I...?)
- "Wie lange ist...?" (How long is...?)
- "Gibt es...?" (Are there...?)
- "Was passiert, wenn...?" (What happens if...?)

### Answer Style

FAQ answers should:
1. Start with direct answer (Yes/No if applicable)
2. Provide necessary context
3. Include specific numbers/details
4. End with action or resource link if helpful

**Strong answer**:
> **Wie lange ist mein Code gültig?**
> Dein Code ist ab dem Kaufdatum 5 Jahre lang gültig. Du findest das genaue Ablaufdatum auf deiner Bestätigungs-E-Mail.

**Weak answer**:
> **Wie lange ist mein Code gültig?**
> Die Gültigkeitsdauer variiert. Bitte prüfen Sie die Bedingungen.

(Also wrong because it uses "Sie"!)

### German-Specific FAQ Topics

Include questions that address German concerns:

- Regional restrictions/currency
- German payment method availability
- German customer service contact
- Privacy/data handling
- Fee breakdown

---

## 9. Edge Cases

### Foreign Interface Terms

When platforms don't have German interfaces:

- Keep original interface terms
- Provide German translation in parentheses: `"Redeem" (dt. Einlösen)`
- Note language limitation if significant

### English Terms That Stay English

Some English terms are standard even in German contexts. Don't force awkward translations when the English term is:

- Industry standard in German
- How German users actually search
- Clearer than any translation

**Examples**: "Download", "Code", "App", "Account" (though "Konto" also works)

### Content That Should Differ Significantly

Sometimes German market genuinely needs different content:

- Legal/regulatory requirements differ
- Product features differ by region
- Cultural context requires different emphasis

**Don't force English structure onto content that should be fundamentally different.**

---

## 10. Quality Signals

High-quality German localization demonstrates:

| Signal | Check |
|--------|-------|
| Natural flow | Doesn't read like a translation |
| Correct address | "du" throughout, never "Sie" |
| Payment methods | German options prominently featured |
| Fee information | Specific, concrete numbers |
| Instructions | Step-by-step with clear endpoints |
| FAQs | Address German-specific concerns |
| Regional info | Clear and upfront |
| Benefits section | Exists, uses bullet points |
| Tone match | Appropriate for content type |
| Links | Point to German resources |

### Self-Review Checklist

Before finalizing any content:

- [ ] All "Sie" forms removed? (Check Code Checker output)
- [ ] Payment methods include PayPal, Klarna?
- [ ] Fees explicitly stated with examples?
- [ ] Numbered lists end with "Fertig!" or equivalent?
- [ ] Currency format is "X €" (number + space + symbol)?
- [ ] Meta title ≤ 60 characters?
- [ ] Meta description ≤ 154 characters?
- [ ] FAQ answers are direct and specific?

---

## Reference

For machine-validated rules, see `client_rules.js`:
- `forbidden_words`: Terms that trigger validation errors
- `terminology`: Required translations
- `patterns`: Format validation (currency, dates, lists)
- `lengths`: Character limits
