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

        CREATE TABLE IF NOT EXISTS Tags (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Recipe_Tags (
            recipe_id INTEGER NOT NULL REFERENCES Recipes(id) ON DELETE CASCADE,
            tag_id    INTEGER NOT NULL REFERENCES Tags(id) ON DELETE CASCADE,
            PRIMARY KEY (recipe_id, tag_id)
        );

        CREATE TABLE IF NOT EXISTS Preparation_Steps (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id   INTEGER NOT NULL REFERENCES Recipes(id) ON DELETE CASCADE,
            step_number INTEGER NOT NULL,
            instruction TEXT NOT NULL,
            UNIQUE (recipe_id, step_number)
        );
    """)

    cuisines = ["Italian", "Indian", "Mexican", "Thai"]
    for name in cuisines:
        conn.execute("INSERT OR IGNORE INTO Cuisines (name) VALUES (?)", (name,))

    ingredients = [
        "tomato", "garlic", "onion", "chicken", "cumin",
        "cheese", "pasta", "chili", "olive oil", "garam masala",
        "bell pepper", "mushroom", "yogurt", "lime", "cilantro", "ginger",
        "basil", "broth",
    ]
    for name in ingredients:
        conn.execute("INSERT OR IGNORE INTO Ingredients (name) VALUES (?)", (name,))

    recipes = [
        ("Pasta Pomodoro",       "tomato,garlic,pasta,olive oil",            ("Italian",)),
        ("Chicken Tikka",        "chicken,garlic,garam masala,onion",        ("Indian",)),
        ("Tacos al Carbon",      "chicken,cumin,chili,onion",                ("Mexican",)),
        ("Margherita Base",      "tomato,garlic,cheese,olive oil",           ("Italian",)),
        ("Dal Tadka",            "cumin,garlic,onion,garam masala",          ("Indian",)),
        ("Tandoori Pizza",       "tomato,chicken,cheese,garam masala",       ("Italian","Indian")),
        ("Veggie Supreme",       "tomato,bell pepper,mushroom,garlic",       ("Italian",)),
        ("Butter Chicken",       "chicken,tomato,garam masala,yogurt",       ("Indian",)),
        ("Chicken Tortilla Soup","chicken,tomato,chili,lime,cilantro",       ("Mexican",)),
        ("Tikka Quesadilla",     "chicken,cheese,chili,lime",                ("Mexican","Indian")),
        ("Spicy Thai Basil Chicken","chicken,chili,garlic,onion,basil",      ("Thai",)),
        ("Simple Vegan Salad",   "tomato,olive oil,lime,cilantro",           ("Italian",)),
        ("Ultimate Loaded Pizza","tomato,cheese,olive oil,mushroom,bell pepper,onion,garlic,chicken", ("Italian",)),
        ("Mushroom Broth Soup",  "mushroom,garlic,onion,broth",              ("Italian",)),
        ("Spicy Vegan Curry",    "tomato,onion,garlic,chili,cumin,ginger",   ("Indian",)),
    ]

    for recipe_name, ingredient_str, cuisines in recipes:
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

        for cuisine_name in cuisines:
            cuisine_row = conn.execute(
                "SELECT id FROM Cuisines WHERE name = ?", (cuisine_name,)
            ).fetchone()
            if cuisine_row is not None:
                conn.execute(
                    "INSERT OR IGNORE INTO Recipe_Cuisines (recipe_id, cuisine_id) VALUES (?, ?)",
                    (recipe_id, cuisine_row[0]),
                )

    tags = ["Vegetarian", "High-Protein", "Quick-Prep", "Vegan", "Gluten-Free", "Spicy"]
    for name in tags:
        conn.execute("INSERT OR IGNORE INTO Tags (name) VALUES (?)", (name,))

    recipe_tags = {
        "Pasta Pomodoro":          ["Vegetarian", "Vegan", "Quick-Prep"],
        "Chicken Tikka":           ["High-Protein", "Spicy"],
        "Tacos al Carbon":         ["High-Protein", "Spicy", "Quick-Prep"],
        "Margherita Base":         ["Vegetarian", "Quick-Prep"],
        "Dal Tadka":               ["Vegetarian", "Vegan", "Gluten-Free"],
        "Tandoori Pizza":          ["High-Protein", "Spicy"],
        "Veggie Supreme":          ["Vegetarian", "Vegan", "Gluten-Free"],
        "Butter Chicken":          ["High-Protein", "Gluten-Free"],
        "Chicken Tortilla Soup":   ["High-Protein", "Spicy", "Gluten-Free"],
        "Tikka Quesadilla":        ["High-Protein", "Spicy", "Quick-Prep"],
        "Spicy Thai Basil Chicken":["High-Protein", "Spicy", "Quick-Prep"],
        "Simple Vegan Salad":      ["Vegan", "Vegetarian", "Gluten-Free", "Quick-Prep"],
        "Ultimate Loaded Pizza":   ["High-Protein"],
        "Mushroom Broth Soup":     ["Vegetarian", "Vegan", "Gluten-Free", "Quick-Prep"],
        "Spicy Vegan Curry":       ["Vegan", "Vegetarian", "Spicy", "Gluten-Free"],
    }
    for recipe_name, tag_names in recipe_tags.items():
        recipe_row = conn.execute(
            "SELECT id FROM Recipes WHERE name = ?", (recipe_name,)
        ).fetchone()
        if recipe_row is None:
            continue
        recipe_id = recipe_row[0]
        for tag_name in tag_names:
            tag_row = conn.execute(
                "SELECT id FROM Tags WHERE name = ?", (tag_name,)
            ).fetchone()
            if tag_row is not None:
                conn.execute(
                    "INSERT OR IGNORE INTO Recipe_Tags (recipe_id, tag_id) VALUES (?, ?)",
                    (recipe_id, tag_row[0]),
                )

    preparation_steps = {
        "Pasta Pomodoro": [
            "Bring a large pot of salted water to a boil and cook pasta according to package directions until al dente.",
            "While pasta cooks, heat olive oil in a skillet over medium heat. Add minced garlic and sauté until fragrant.",
            "Add diced tomatoes to the skillet, season with salt, and simmer for 10 minutes.",
            "Toss the drained pasta with the tomato sauce and serve hot.",
        ],
        "Chicken Tikka": [
            "Cut chicken into bite-sized pieces and marinate in yogurt, garam masala, and garlic for at least 1 hour.",
            "Thread chicken onto skewers and grill over medium-high heat until charred and cooked through.",
            "Baste with oil or butter while grilling to keep moist.",
            "Serve hot with sliced onion rings and a squeeze of lemon.",
            "Garnish with fresh cilantro before serving.",
        ],
        "Tacos al Carbon": [
            "Season chicken with cumin, chili powder, garlic, and salt.",
            "Grill chicken over medium-high heat until fully cooked and lightly charred.",
            "Warm tortillas on the grill for 30 seconds per side.",
            "Slice chicken, assemble tacos with onions and your choice of salsa.",
        ],
        "Margherita Base": [
            "Preheat oven to the highest setting (500°F / 260°C) with a pizza stone or baking sheet inside.",
            "Stretch pizza dough into a round and place on a floured peel.",
            "Spread tomato sauce, torn mozzarella, and fresh basil leaves on top. Drizzle with olive oil.",
            "Slide onto the hot stone and bake 8–10 minutes until crust is golden and cheese is bubbling.",
        ],
        "Dal Tadka": [
            "Rinse lentils and boil in water with turmeric until soft and mushy.",
            "In a separate pan, heat ghee or oil. Add cumin seeds, minced garlic, and dried chilies; fry until cumin splutters.",
            "Pour the tadka over the cooked lentils and stir well.",
            "Garnish with cilantro and serve with rice or naan.",
        ],
        "Tandoori Pizza": [
            "Prepare pizza dough and let it rest.",
            "Season chicken pieces with garam masala, yogurt, and chili; grill until cooked.",
            "Stretch dough, spread a thin layer of tomato sauce, and top with mozzarella cheese.",
            "Arrange cooked chicken pieces on top.",
            "Bake at 500°F for 8–10 minutes. Finish with a drizzle of yogurt sauce.",
        ],
        "Veggie Supreme": [
            "Preheat oven to 475°F.",
            "Stretch pizza dough and spread tomato sauce.",
            "Top with sliced bell peppers, mushrooms, and mozzarella cheese.",
            "Bake for 10–12 minutes until crust is crispy and cheese is golden.",
        ],
        "Butter Chicken": [
            "Marinate chicken in yogurt, garam masala, and ginger for 30 minutes.",
            "Grill or broil chicken until charred, then chop into pieces.",
            "In a pan, sauté onion and garlic until soft. Add tomato puree and simmer.",
            "Stir in butter, cream, and garam masala. Add chicken pieces.",
            "Simmer for 10 minutes. Serve with naan or rice.",
        ],
        "Chicken Tortilla Soup": [
            "In a large pot, sauté onion and garlic in oil until soft.",
            "Add diced chicken, tomatoes, chili, and broth. Bring to a boil.",
            "Reduce heat and simmer for 20 minutes.",
            "Stir in lime juice and chopped cilantro.",
            "Serve topped with crispy tortilla strips.",
        ],
        "Tikka Quesadilla": [
            "Season chicken with garam masala and chili; cook in a skillet until done.",
            "Lay a tortilla flat, sprinkle cheese, add chicken, and fold.",
            "Cook on both sides until golden and cheese is melted. Serve with lime wedges.",
        ],
        "Spicy Thai Basil Chicken": [
            "Slice chicken into thin strips and marinate with soy sauce and garlic for 15 minutes.",
            "Heat oil in a wok over high heat. Add chicken and stir-fry until golden.",
            "Toss in sliced chili, onion, and basil leaves. Stir-fry for 2 minutes.",
            "Serve immediately over steamed rice.",
        ],
        "Simple Vegan Salad": [
            "Chop tomatoes and cilantro, combine with lime juice and olive oil. Toss well and serve.",
        ],
        "Ultimate Loaded Pizza": [
            "Preheat oven to 500°F with a pizza stone inside.",
            "Stretch pizza dough into a large round on a floured surface.",
            "Spread tomato sauce evenly over the dough.",
            "Layer sliced mushrooms, bell peppers, onions, and cooked chicken pieces.",
            "Top generously with mozzarella cheese and drizzle with olive oil.",
            "Bake for 10–12 minutes until crust is golden and cheese is bubbling. Let rest 2 minutes before slicing.",
        ],
        "Mushroom Broth Soup": [
            "Sauté sliced mushrooms and minced garlic in olive oil until soft.",
            "Add diced onion and cook until translucent.",
            "Pour in broth, bring to a boil, then simmer for 15 minutes.",
            "Season with salt and pepper. Serve hot.",
        ],
        "Spicy Vegan Curry": [
            "Heat oil in a pot and add cumin seeds until they splutter.",
            "Add diced onion, garlic, and chili. Sauté until onion is golden.",
            "Stir in diced tomatoes, ginger, and curry spices. Cook for 5 minutes.",
            "Add water and simmer for 20 minutes until thickened. Serve with rice.",
        ],
    }
    for recipe_name, steps in preparation_steps.items():
        recipe_row = conn.execute(
            "SELECT id FROM Recipes WHERE name = ?", (recipe_name,)
        ).fetchone()
        if recipe_row is None:
            continue
        recipe_id = recipe_row[0]
        for i, instruction in enumerate(steps, start=1):
            conn.execute(
                "INSERT OR IGNORE INTO Preparation_Steps (recipe_id, step_number, instruction) VALUES (?, ?, ?)",
                (recipe_id, i, instruction),
            )

    conn.commit()

    print("Database initialized successfully.")
