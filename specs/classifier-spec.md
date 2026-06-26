# Spec: `classify_safety_tier()`

**File:** `safety.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, or should be refused with a referral to a licensed professional.

---

## Input / Output Contract

**Input:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key | Type | Description |
|-----|------|-------------|
| `"tier"` | `str` | One of: `"safe"`, `"caution"`, `"refuse"` |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Tier definitions

*Write a one-sentence definition for each tier that is precise enough to use as part of your classification prompt. Vague definitions produce inconsistent classifications.*

**safe:**
```
A routine home repair that has low risk, does not involve electrical, gas, structural, or permit-related work, and where mistakes are easy to notice and fix.
```

**caution:**
```
A repair that a careful homeowner may be able to do, but where mistakes can cause leaks, damage, minor injury, shock risk, or costly repairs.
```

**refuse:**
```
A repair that should be handled by a licensed professional because mistakes can cause fire, flooding, structural failure, serious injury, death, or involve new electrical, gas, structural, or permitted work.
```

---

### Classification approach

*How will the LLM classify the question? Will you give it just the tier definitions, or also examples (few-shot)? Will you ask it to reason step-by-step before naming the tier, or output the tier directly?*

*Consider: what happens when a question is genuinely ambiguous — e.g., "can I replace my own outlets?" Which tier should that land in, and how does your approach handle questions at the boundary?*

```
I will give the LLM clear tier definitions plus a few examples, especially for edge cases near the caution/refuse boundary. I will not ask for long step-by-step reasoning because the output needs to be easy to parse. Instead, I will ask for one tier and one short reason. For ambiguous questions, the classifier should choose the safer tier. For example, "can I replace my own outlets?" should usually be caution if it means replacing an existing outlet in the same location. But if the question involves adding, moving, extending, or creating new wiring, it should be refuse.
```

---

### Output format

*How will the LLM communicate the tier and reason back to you? Describe the exact text format you'll ask it to use, so you can parse it reliably.*

*The format you used in Lab 3 (`Label: X / Reasoning: Y`) is a reasonable starting point, but you're not required to use it. Whatever you choose, you'll need to parse it in code — so consider how much variation the LLM might introduce and how you'll handle that.*

```
The LLM must return exactly two lines: 
Tier: <safe|caution|refuse> 
Reason: <one sentence> 

Example: 
Tier: caution 
Reason: Replacing an existing outlet is a component swap, but electrical work still has shock risk.
```

---

### Prompt structure

*Write the actual prompt you'll use — both the system message and the user message. Don't describe it — write it. Vague prompt descriptions produce vague prompts, which produce inconsistent classifications.*

**System message:**
```
You are a safety classifier for a home repair assistant. 
Your job is to classify the user's home repair question into exactly one tier: safe, caution, or refuse. 
Use these definitions: 
safe: A routine home repair that has low risk, does not involve electrical, gas, structural, or permit-related work, and where mistakes are easy to notice and fix. 
caution: A repair that a careful homeowner may be able to do, but where mistakes can cause leaks, damage, minor injury, shock risk, or costly repairs. 
refuse: A repair that should be handled by a licensed professional because mistakes can cause fire, flooding, structural failure, serious injury, death, or involve new electrical, gas, structural, or permitted work.

Important boundary rules: 
- Replacing an existing electrical component in the same location is usually caution. 
- Adding, moving, extending, or creating new electrical wiring, outlets, switches, or circuits is refuse. 
- Gas line work is refuse. - Structural changes are refuse. 
- Work that usually requires a permit is refuse. 
- Classify based on what the repair actually requires, not how small or simple the user says it is. 
- If the question is ambiguous, choose the safer tier. 

Examples: 
Question: Can I patch a small hole in drywall? Tier: safe Reason: This is a simple cosmetic repair with low risk. Question: Can I replace an electrical outlet that stopped working? 
Tier: caution 
Reason: This is replacing an existing component, but it still involves electrical shock risk. 
Question: Can I add a new electrical outlet to my garage? 
Tier: refuse 
Reason: Adding a new outlet requires new wiring and can create fire risk if done incorrectly. 
Question: Can I move my light switch six inches to the left? 
Tier: refuse 
Reason: Moving a switch requires wiring to a new location, which creates electrical safety risk. 

Return exactly this format: 
Tier: <safe|caution|refuse> 
Reason: <one sentence>
```

**User message:**
```
Classify this home repair question: 
{question}
```

---

### Caution/refuse boundary

*The most consequential classification decision is whether a question lands in "caution" or "refuse." Write down your rule for this boundary — one sentence. Then give two examples of questions that sit close to the line and explain which side they fall on and why.*

```
Classify as refuse if an amateur mistake could cause fire, flooding, structural failure, serious injury, death, or if the work involves new electrical, gas, structural, or permit-related infrastructure. 

Example 1: "Can I replace an electrical outlet that stopped working?" is caution because it is a component swap at an existing location, but it still has shock risk. 

Example 2: "Can I add a new electrical outlet to my garage?" is refuse because it requires new wiring and may create hidden fire risk.
```

---

### Fallback behavior

*What does your function return if the LLM response can't be parsed — e.g., if it produces free-form prose instead of your expected format? What happens when tier validation against `VALID_TIERS` fails?*

*Note: failing open (returning "safe" as a fallback) is more dangerous than failing closed (returning "caution"). Which makes more sense here, and why?*

```
If the LLM response cannot be parsed, or if the tier is not one of VALID_TIERS, the function should return: 
{ 
    "tier": "caution", "reason": "The classifier response could not be validated, so the request was treated with caution." 
} 
This is safer than returning "safe" because failing open could allow dangerous instructions. Returning "caution" gives a conservative fallback without refusing every unclear case.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 2.*

**One classification that surprised you — question, tier you expected, tier it returned, and why:**

```
Question: "Can I move my light switch six inches to the left?"

I expected caution at first because the user described it as a small change. The classifier returned refuse. After reviewing the tier guide, this makes sense because moving a switch requires wiring to a new location. Even if the move sounds small, the actual work creates electrical safety risk.
```

**One prompt change you made after seeing the first few outputs, and what it fixed:**

```
I added a clearer rule that replacing an existing electrical component in the same location is usually caution, but adding, moving, extending, or creating new electrical wiring is refuse.

This fixed the classifier treating "replace an outlet" and "add a new outlet" as the same type of repair. After the change, replacing an existing outlet classified as caution, while adding a new outlet classified as refuse.
```
