import sqlite3

with sqlite3.connect("flavorforge.db") as conn:
    conn.execute("PRAGMA foreign_keys = ON")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS Recipes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            instructions TEXT   NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Ingredients (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Cuisines (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Recipe_Ingredients (
            recipe_id     INTEGER NOT NULL REFERENCES Recipes(id),
            ingredient_id INTEGER NOT NULL REFERENCES Ingredients(id),
            PRIMARY KEY (recipe_id, ingredient_id)
        );

        CREATE TABLE IF NOT EXISTS Recipe_Cuisines (
            recipe_id  INTEGER NOT NULL REFERENCES Recipes(id),
            cuisine_id INTEGER NOT NULL REFERENCES Cuisines(id),
            PRIMARY KEY (recipe_id, cuisine_id)
        );
    """)

    cuisines = ["Italian", "Indian", "Mexican"]
    for name in cuisines:
        conn.execute("INSERT OR IGNORE INTO Cuisines (name) VALUES (?)", (name,))

    ingredients = [
        "tomato", "garlic", "onion", "chicken", "cumin",
        "cheese", "pasta", "chili", "olive oil", "garam masala",
    ]
    for name in ingredients:
        conn.execute("INSERT OR IGNORE INTO Ingredients (name) VALUES (?)", (name,))

    recipes = [
        ("Pasta Pomodoro",    "tomato,garlic,pasta,olive oil",     "Italian"),
        ("Chicken Tikka",     "chicken,garlic,garam masala,onion", "Indian"),
        ("Tacos al Carbon",   "chicken,cumin,chili,onion",         "Mexican"),
        ("Margherita Base",   "tomato,garlic,cheese,olive oil",    "Italian"),
        ("Dal Tadka",         "cumin,garlic,onion,garam masala",   "Indian"),
    ]

    for recipe_name, ingredient_str, cuisine_name in recipes:
        cur = conn.execute(
            "INSERT OR IGNORE INTO Recipes (name, instructions) VALUES (?, ?)",
            (recipe_name, ""),
        )
        recipe_id = cur.lastrowid

        if not recipe_id:
            existing = conn.execute(
                "SELECT id FROM Recipes WHERE name = ?", (recipe_name,)
            ).fetchone()
            if existing is None:
                continue
            recipe_id = existing[0]

        for ing_name in ingredient_str.split(","):
            ing_name = ing_name.strip()
            row = conn.execute(
                "SELECT id FROM Ingredients WHERE name = ?", (ing_name,)
            ).fetchone()
            if row is not None:
                conn.execute(
                    "INSERT OR IGNORE INTO Recipe_Ingredients (recipe_id, ingredient_id) VALUES (?, ?)",
                    (recipe_id, row[0]),
                )

        cuisine_row = conn.execute(
            "SELECT id FROM Cuisines WHERE name = ?", (cuisine_name,)
        ).fetchone()
        if cuisine_row is not None:
            conn.execute(
                "INSERT OR IGNORE INTO Recipe_Cuisines (recipe_id, cuisine_id) VALUES (?, ?)",
                (recipe_id, cuisine_row[0]),
            )

    conn.commit()

    print("Database initialized successfully.")
