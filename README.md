# 🍽️ FlavorForge

A Flask + SQLite recipe app with **predictive ingredient matching**, **cultural fusion** queries, **tag browsing**, and **preparation step management** — powered by HTMX on the frontend.

## ✨ Features

- 🔍 **Predictive Match** — Input ingredients you have; get recipes ranked by how many of those ingredients they use.
- 🌍 **Cultural Fusion** — Find recipes that belong to two cuisines simultaneously (e.g. Italian × Indian).
- 🏷️ **Tag Browser** — Browse recipes by tag (Vegetarian, Vegan, High-Protein, Quick-Prep, Gluten-Free, Spicy).
- ➕ **Add Tag** — Attach tags to any recipe.
- 📝 **Preparation Steps** — View and add numbered step-by-step instructions for any recipe.
- ➕ **Add Recipes** — Dynamically add new recipes with ingredients, cuisine, tags, and steps.
- 📖 **View All Recipes** — Browse the full recipe catalog with a single click.

## 🛠️ Tech Stack

| Layer     | Technology   |
|-----------|--------------|
| Backend   | Python 3.10+, Flask |
| Database  | SQLite3 (raw `sqlite3` module, no ORM) |
| Frontend  | HTMX 2.x, vanilla CSS |

## 🚀 Quick Start

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

## 🗄️ Database Schema

| Table | Description |
|---|---|
| `Recipes` | id, name, instructions |
| `Ingredients` | id, name (unique) |
| `Cuisines` | id, name (unique) |
| `Recipe_Ingredients` | many-to-many link |
| `Recipe_Cuisines` | many-to-many link |
| `Tags` | id, name (unique) |
| `Recipe_Tags` | many-to-many link |
| `Preparation_Steps` | id, recipe_id, step_number, instruction |

The schema is defined in `init_db.py` and seeds **15 recipes**, **18 ingredients**, **4 cuisines**, and **6 tags**.

## 🌐 Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Main page |
| `/add_recipe` | POST | Create a recipe (name, ingredients, cuisine, tags, steps) |
| `/predictive_match` | POST | Rank recipes by ingredient match count |
| `/cultural_fusion` | POST | Find recipes in two cuisines |
| `/list_recipes` | GET | List all recipes with ingredients and cuisines |
| `/recipes_by_tag` | GET | List recipes by tag (or all tags if no tag given) |
| `/add_tag` | POST | Attach a tag to a recipe |
| `/recipe_steps` | GET | Get ordered preparation steps for a recipe |
| `/add_step` | POST | Insert/replace a preparation step |

## 📄 License

MIT
