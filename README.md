### Application Architecture


eden-commons/
├── app.py                  # Streamlit entry point
├── requirements.txt
├── .env                    # local secrets (never committed)
├── .env.example            # template without values
├── README.md
│
├── core/
│   ├── almanac.py          # Almanac Engine: calendar generation
│   ├── lunar.py            # Lunar phase calculations via ephem
│   ├── climate.py          # Open-Meteo API wrapper
│   ├── geocoding.py        # Nominatim wrapper
│   └── synthesis.py        # Claude API: calendar synthesis + contribution pipeline
│
├── db/
│   ├── connection.py       # SQLite (dev) / Supabase (prod) connection manager
│   ├── queries.py          # All DB read/write operations
│   └── seed/
│       ├── crops.json      # Crop technical data — 10 crops
│       └── entries.json    # Community seed entries — ~50 entries
│
├── ui/
│   ├── calendar_view.py    # Annual calendar component
│   ├── crop_card.py        # Crop data card component
│   ├── contribute_form.py  # Contribution form + live AI validation
│   └── browse_commons.py   # Public browse view
│
└── assets/
    └── style.css           # Custom Streamlit CSS