# EDEN Commons 🌱

**Agricultural wisdom, from the ground up.**

![Python](https://img.shields.io/badge/Python-3.11+-4a7c59?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-8fb339?style=flat&logo=streamlit&logoColor=white)

---

## About

EDEN Commons is a collective intelligence platform that fuses real climate data, lunar cycles, and ancestral agricultural knowledge into personalized 12-month cultivation calendars — for any crop, anywhere in the world.

Built as part of **Project EDEN** — an autonomous agricultural robotics ecosystem inspired by the Solarpunk movement, where technology serves land sovereignty rather than extractive industry.

> *Software for sovereignty — the knowledge belongs to the people who share it.*

> 🌿 Green Hackathon — "Think Globally, Build Locally" — June 2026 Hopamine Community

---

## Features

| | |
|---|---|
| 🌤️ **Climate-based calendar** | Real temperature and precipitation data via Open-Meteo, for any location worldwide |
| 🌙 **Lunar phase timing** | Traditional moon phase windows calculated with `ephem`, rooted in almanac wisdom |
| 👥 **Community knowledge** | A contribution system where farmers share practices from their land |
| 🤖 **AI validation** | Claude (Anthropic) organizes and structures contributions — it never replaces human knowledge |
| 🌍 **Works anywhere** | Geocoding via OpenStreetMap Nominatim supports any city, region, or country |
| 📥 **Public data** | All community entries are browsable and exportable as CSV |

---

## How it works

```
1️⃣  Enter your location and crop
        ↓
2️⃣  Get your personalized 12-month calendar
    (climate data + lunar phases + community wisdom)
        ↓
3️⃣  Contribute what you know
    (your practice is validated, structured, and added to the Commons)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| Language | Python 3.11+ |
| AI | [Claude API](https://anthropic.com) (Haiku) — Anthropic |
| Climate data | [Open-Meteo](https://open-meteo.com) Archive API |
| Lunar phases | [ephem](https://rhodesmill.org/ephem/) |
| Database | SQLite (dev) / Supabase (prod) |
| Geocoding | [OpenStreetMap Nominatim](https://nominatim.org) |

---

## Contributing Knowledge

The Commons grows through three kinds of contributions:

**1. Verified practice** — Consistent with existing entries from the same or similar region.
> *"In Santander, Colombia, we plant maize in late March when the crescent moon rises. The soil must already be warm."*
> → Claude confirms the timing against other Andean entries, labels it `verified`, stores the lunar and soil conditions.

**2. Regional variant** — Contradicts other regions but is geographically plausible — not invalid, just local.
> *"In Patagonia we wait until November for maize — it's the Southern Hemisphere spring."*
> → Stored as `regional_variant` with hemisphere context, visible alongside Northern Hemisphere entries.

**3. New knowledge** — No existing entries to compare against. Stored as `unverified` and surfaced for future validation by the community.
> *"My grandmother always soaked the seeds in chamomile tea before planting."*
> → Saved with full raw text, waiting for corroboration from other farmers.

---

## Project Structure

```
eden-commons/
├── app.py                  # Streamlit entry point + navigation
├── requirements.txt
├── .env.example            # API key template (no values)
├── README.md
│
├── core/
│   ├── almanac.py          # Almanac Engine: calendar data generation + caching
│   ├── lunar.py            # Lunar phase calculations via ephem
│   ├── climate.py          # Open-Meteo API wrapper
│   ├── geocoding.py        # Nominatim geocoding wrapper
│   ├── lunar_heuristics.py # Planting suggestions per moon phase
│   └── synthesis.py        # Claude API: calendar synthesis + contribution validation
│
├── db/
│   ├── connection.py       # SQLite (dev) / Supabase (prod) connection manager
│   ├── init_db.py          # Schema creation
│   ├── queries.py          # All DB read/write operations + calendar cache
│   └── seed/
│       ├── crops.json      # Crop technical data — 10 crops
│       └── entries.json    # Community seed entries — ~50 entries
│
├── ui/
│   ├── calendar_view.py    # 12-month calendar grid + month detail panel
│   ├── crop_card.py        # Crop technical data card component
│   ├── contribute_form.py  # Contribution form with live AI validation
│   └── browse_commons.py   # Public browse view with filters and CSV export
│
└── assets/
    └── style.css           # Solarpunk design system (DM Sans + DM Serif Display)
```

---

## Part of Project EDEN

EDEN Commons is the **knowledge layer** of the EDEN ecosystem.

Project EDEN is building ARIA — an autonomous agricultural robot designed to work alongside small-scale farmers in the Global South. ARIA navigates fields, monitors soil and plant health, and assists with cultivation decisions.

But a robot without context is just a machine. EDEN Commons is what gives ARIA that context: the accumulated, community-verified knowledge of *when* to plant, *how* the moon affects germination, *what* a specific soil in a specific valley needs. Knowledge that doesn't exist in any academic dataset — because it lives in the hands and memory of the people who work the land.

Commons feeds ARIA. ARIA defends the land. The knowledge stays with the people.

---

*Built with 🌱 by the EDEN team · Solarpunk · Open source · For the commons · Project Developed by Daniel Amado*
