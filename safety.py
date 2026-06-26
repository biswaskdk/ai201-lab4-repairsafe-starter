from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)


def classify_safety_tier(question: str) -> dict:
    """
    Classify a home repair question into one of three safety tiers.
    """

    system_message = """
You are a safety classifier for a home repair assistant.

Classify the user's repair question into exactly one tier:
safe, caution, or refuse.

Definitions:
safe: A routine home repair that has low risk, does not involve electrical, gas, structural, or permit-related work, and where mistakes are easy to notice and fix.

caution: A repair that a careful homeowner may be able to do, but where mistakes can cause leaks, damage, minor injury, shock risk, or costly repairs.

refuse: A repair that should be handled by a licensed professional because mistakes can cause fire, flooding, structural failure, serious injury, death, or involve new electrical, gas, structural, or permitted work.

Rules:
- Replacing an existing electrical component in the same location is usually caution.
- Adding, moving, extending, or creating new electrical wiring, outlets, switches, or circuits is refuse.
- Gas line work is refuse.
- Structural changes are refuse.
- Work that usually requires a permit is refuse.
- Classify based on what the repair actually requires, not how small the user says it is.
- If unsure, choose the safer tier.

Examples:
Question: Can I patch a small hole in drywall?
Tier: safe
Reason: This is a simple cosmetic repair with low risk.

Question: Can I replace an electrical outlet that stopped working?
Tier: caution
Reason: This is replacing an existing component, but it still involves shock risk.

Question: Can I add a new electrical outlet to my garage?
Tier: refuse
Reason: Adding a new outlet requires new wiring and can create fire risk.

Question: Can I move my light switch six inches to the left?
Tier: refuse
Reason: Moving a switch requires wiring to a new location, which creates electrical safety risk.

Return exactly this format:
Tier: <safe|caution|refuse>
Reason: <one sentence>
"""

    user_message = f"""
Classify this home repair question:

{question}
"""

    fallback = {
        "tier": "caution",
        "reason": "The classifier response could not be validated, so the request was treated with caution.",
    }

    try:
        completion = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
        )

        raw_response = completion.choices[0].message.content.strip()

        tier = None
        reason = None

        for line in raw_response.splitlines():
            clean_line = line.strip()

            if clean_line.lower().startswith("tier:"):
                tier = clean_line.split(":", 1)[1].strip().lower()
                tier = tier.replace('"', "").replace("'", "").strip()

            elif clean_line.lower().startswith("reason:"):
                reason = clean_line.split(":", 1)[1].strip()

        if tier not in VALID_TIERS:
            return fallback

        if not reason:
            reason = "The question was classified based on the home repair safety rules."

        return {
            "tier": tier,
            "reason": reason,
        }

    except Exception:
        return fallback
