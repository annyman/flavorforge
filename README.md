# FlavorForge

A Flask + SQLite recipe app with **predictive ingredient matching** and **cultural fusion** queries, powered by HTMX on the frontend.

## Features

- **Predictive Match** — Input ingredients you have; get recipes ranked by how many of those ingredients they use.
- **Cultural Fusion** — Find recipes that belong to two cuisines simultaneously (e.g. Italian × Indian).
- **Add Recipes** — Dynamically add new recipes with ingredients and cuisine tags.
- **View All Recipes** — Browse the full recipe catalog with a single click.

## Tech Stack

| Layer     | Technology   |
|-----------|--------------|
| Backend   | Python 3.10+, Flask |
| Database  | SQLite3 (raw `sqlite3` module, no ORM) |
| Frontend  | HTMX 2.x, vanilla CSS |

## Quick Start

```bash
# Clone the repo
git clone git@github.com:annyman/flavorforge.git
cd flavorforge

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask

# Initialize the database
python init_db.py

# Run the app
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Database Schema

- `Recipes` — id, name, instructions
- `Ingredients` — id, name (unique)
- `Cuisines` — id, name (unique)
- `Recipe_Ingredients` — many-to-many link
- `Recipe_Cuisines` — many-to-many link

The schema is defined in `init_db.py` and seeds 10 recipes, 16 ingredients, and 3 cuisines.

## License

MIT
