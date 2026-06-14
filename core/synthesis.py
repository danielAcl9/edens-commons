import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import anthropic

from dotenv import load_dotenv
load_dotenv()

MODEL = "claude-haiku-4-5-20251001"

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def synthesize_calendar(calendar_data: dict) -> dict | None:
    location = calendar_data.get("location", {})
    climate = calendar_data.get("climate", [])
    lunar_phases = calendar_data.get("lunar_phases", [])
    crop_data = calendar_data.get("crop_data", {})
    community_entries = calendar_data.get("community_entries", [])

    climate_summary = json.dumps(climate[:12], ensure_ascii=False)
    lunar_summary = json.dumps(lunar_phases[:12], ensure_ascii=False)

    community_sample = community_entries[:10]
    community_summary = json.dumps(
        [
            {
                "region": e.get("region"),
                "activity": e.get("activity"),
                "timing_local": e.get("timing_local"),
                "lunar_condition": e.get("lunar_condition"),
                "raw_text": e.get("raw_text", "")[:200],
            }
            for e in community_sample
        ],
        ensure_ascii=False,
    )

    prompt = f"""You are an agricultural calendar assistant. Based on the data below, generate a brief monthly summary for a {crop_data.get('common_name', 'crop')} growing calendar in {location.get('name', 'the given location')}.

CLIMATE DATA (monthly averages, last year):
{climate_summary}

UPCOMING LUNAR PHASES:
{lunar_summary}

CROP INFO:
- Water requirement: {crop_data.get('water_requirement')}
- Sun requirement: {crop_data.get('sun_requirement')}
- Germination: {crop_data.get('germination_days_min')}–{crop_data.get('germination_days_max')} days
- Days to harvest: {crop_data.get('days_to_harvest_min')}–{crop_data.get('days_to_harvest_max')} days
- Frost tolerant: {crop_data.get('frost_tolerant')}
- Notes: {crop_data.get('notes', '')}

COMMUNITY ENTRIES (sample):
{community_summary}

For each of the 12 months (January through December), determine the single most recommended activity from this list:
- planting
- fertilizing
- pruning
- harvest
- irrigation
- rest

Base your decision on:
1. The climate data for that month (temperature, precipitation)
2. The nearest upcoming lunar phase
3. Relevant community entries that mention that time of year

Respond with ONLY the JSON object, no other text, no markdown code blocks, no explanation.
The very first character of your response must be {{ and the very last must be }}.
Use this exact structure:
{{"months": [{{"month": "January", "activity": "planting", "explanation": "Brief reason"}}, ...]}}

Include all 12 months in order."""

    try:
        response = _get_client().messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        text = next((b.text for b in response.content if b.type == "text"), "")
        start = text.find("{")
        end = text.rfind("}") + 1
        json_str = text[start:end] if start != -1 and end > start else text
        return json.loads(json_str)
    except Exception:
        return None


def validate_contribution(form_data: dict, existing_entries: list) -> dict:
    practice_text = form_data.get("practice_text", "")
    region = form_data.get("region", "")
    crop_id = form_data.get("crop_id", "")
    timing = form_data.get("timing", "")
    source = form_data.get("source", "")

    existing_sample = existing_entries[:15]
    existing_summary = json.dumps(
        [
            {
                "region": e.get("region"),
                "activity": e.get("activity"),
                "timing_local": e.get("timing_local"),
                "lunar_condition": e.get("lunar_condition"),
                "status": e.get("status"),
                "raw_text": e.get("raw_text", "")[:150],
            }
            for e in existing_sample
        ],
        ensure_ascii=False,
    )

    prompt = f"""You are a community agricultural knowledge validator.

A user submitted the following contribution:
- Crop: {crop_id}
- Region: {region}
- Timing: {timing}
- Source: {source}
- Practice description: {practice_text}

EXISTING COMMUNITY ENTRIES FOR THIS CROP:
{existing_summary}

Your tasks:
1. Parse the practice description into a structured JSON with these fields:
   - activity: one of [planting, fertilizing, pruning, harvest, irrigation, rest, other]
   - lunar_condition: lunar phase preference mentioned (or null)
   - soil_condition: soil requirement mentioned (or null)
   - timing_local: local timing described (e.g. "early March", "after first rain")
   - timing_hemisphere: "northern", "southern", or null

2. Compare the contribution against existing entries to assign a status:
   - "verified": consistent with existing entries from the same or similar region
   - "unverified": no similar entries exist to compare against
   - "regional_variant": contradicts entries from other regions but is geographically plausible (not invalid)
   - "rejected": the text is spam, irrelevant, nonsensical, or clearly not agricultural practice

3. Write a brief user-facing message (1–2 sentences) explaining the status.

Respond with ONLY the JSON object, no other text, no markdown code blocks, no explanation.
The very first character of your response must be {{ and the very last must be }}.
Use this exact structure:
{{"structured_json": {{"activity": "...", "lunar_condition": null, "soil_condition": null, "timing_local": "...", "timing_hemisphere": null}}, "status": "...", "message": "..."}}"""

    try:
        response = _get_client().messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = next((b.text for b in response.content if b.type == "text"), "")
        start = text.find("{")
        end = text.rfind("}") + 1
        json_str = text[start:end] if start != -1 and end > start else text
        return json.loads(json_str)
    except Exception:
        return {
            "structured_json": None,
            "status": "unverified",
            "message": "Could not validate automatically — saved for review.",
        }
