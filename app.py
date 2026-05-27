import sqlite3
from flask import Flask, request, render_template, render_template_string

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("flavorforge.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/add_recipe", methods=["POST"])
def add_recipe():
    recipe_name = request.form.get("recipe_name", "").strip()
    ingredients = request.form.getlist("ingredients[]")
    cuisine = request.form.get("cuisine", "").strip()

    conn = get_db_connection()
    try:
        cur = conn.execute(
            "INSERT INTO Recipes (name, instructions) VALUES (?, ?)",
            (recipe_name, ""),
        )
        recipe_id = cur.lastrowid

        for ing in ingredients:
            ing = ing.strip()
            if not ing:
                continue
            conn.execute("INSERT OR IGNORE INTO Ingredients (name) VALUES (?)", (ing,))
            row = conn.execute(
                "SELECT id FROM Ingredients WHERE name = ?", (ing,)
            ).fetchone()
            if row is not None:
                conn.execute(
                    "INSERT OR IGNORE INTO Recipe_Ingredients (recipe_id, ingredient_id) VALUES (?, ?)",
                    (recipe_id, row[0]),
                )

        if cuisine:
            conn.execute("INSERT OR IGNORE INTO Cuisines (name) VALUES (?)", (cuisine,))
            row = conn.execute(
                "SELECT id FROM Cuisines WHERE name = ?", (cuisine,)
            ).fetchone()
            if row is not None:
                conn.execute(
                    "INSERT OR IGNORE INTO Recipe_Cuisines (recipe_id, cuisine_id) VALUES (?, ?)",
                    (recipe_id, row[0]),
                )

        conn.commit()
    finally:
        conn.close()

    return render_template_string(
        "<tr><td>{{ name }}</td><td>Added</td></tr>", name=recipe_name
    )


@app.route("/predictive_match", methods=["POST"])
def predictive_match():
    ingredients = request.form.getlist("ingredients[]")
    cleaned = []
    for ing in ingredients:
        ing = ing.strip().lower()
        if ing:
            cleaned.append(ing)

    if not cleaned:
        return render_template_string("<li>No matching recipes found.</li>")

    placeholders = ",".join("?" for _ in cleaned)
    sql = f"""
        SELECT r.name, COUNT(i.name) as match_count
        FROM Recipes r
        JOIN Recipe_Ingredients ri ON r.id = ri.recipe_id
        JOIN Ingredients i ON ri.ingredient_id = i.id
        WHERE LOWER(i.name) IN ({placeholders})
        GROUP BY r.id
        ORDER BY match_count DESC
    """

    conn = get_db_connection()
    try:
        rows = conn.execute(sql, cleaned).fetchall()
    finally:
        conn.close()

    if not rows:
        return render_template_string("<li>No matching recipes found.</li>")

    items = "".join(
        f"<li>{row['name']} — {row['match_count']} ingredients matched</li>"
        for row in rows
    )
    return render_template_string("<ul>{{ items|safe }}</ul>", items=items)


@app.route("/cultural_fusion", methods=["POST"])
def cultural_fusion():
    cuisine_a = request.form.get("cuisine_a", "").strip()
    cuisine_b = request.form.get("cuisine_b", "").strip()

    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT r.name
            FROM Recipes r
            JOIN Recipe_Cuisines rc ON r.id = rc.recipe_id
            JOIN Cuisines c ON rc.cuisine_id = c.id
            WHERE c.name IN (?, ?)
            GROUP BY r.id
            HAVING COUNT(DISTINCT c.id) = 2
            """,
            (cuisine_a, cuisine_b),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return render_template_string(
            "<p>No fusion recipes found for these two cuisines.</p>"
        )

    items = "".join(f"<li>{row['name']}</li>" for row in rows)
    return render_template_string(
        "<div><strong>Fusion: {{ a }} + {{ b }}</strong><ul>{{ items|safe }}</ul></div>",
        a=cuisine_a,
        b=cuisine_b,
        items=items,
    )


@app.route("/list_recipes", methods=["GET"])
def list_recipes():
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT r.id, r.name,
                   GROUP_CONCAT(DISTINCT i.name) AS ingredients,
                   GROUP_CONCAT(DISTINCT c.name) AS cuisines
            FROM Recipes r
            LEFT JOIN Recipe_Ingredients ri ON r.id = ri.recipe_id
            LEFT JOIN Ingredients i ON ri.ingredient_id = i.id
            LEFT JOIN Recipe_Cuisines rc ON r.id = rc.recipe_id
            LEFT JOIN Cuisines c ON rc.cuisine_id = c.id
            GROUP BY r.id
            ORDER BY r.name
        """).fetchall()
    finally:
        conn.close()

    if not rows:
        return render_template_string("<p>No recipes yet.</p>")

    items = "".join(
        "<tr>"
        f"<td>{row['name']}</td>"
        f"<td>{row['ingredients'] or ''}</td>"
        f"<td>{row['cuisines'] or ''}</td>"
        "</tr>"
        for row in rows
    )
    return render_template_string(
        "<table><thead><tr><th>Name</th><th>Ingredients</th><th>Cuisines</th></tr></thead>"
        "<tbody>{{ items|safe }}</tbody></table>",
        items=items,
    )


if __name__ == "__main__":
    app.run(debug=False)
