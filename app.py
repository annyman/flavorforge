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
    tags = request.form.get("tags", "").strip()
    steps = request.form.get("steps", "").strip()

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

        if tags:
            for tag_name in tags.split(","):
                tag_name = tag_name.strip().title()
                if tag_name:
                    conn.execute("INSERT OR IGNORE INTO Tags (name) VALUES (?)", (tag_name,))
                    tag_row = conn.execute(
                        "SELECT id FROM Tags WHERE name = ?", (tag_name,)
                    ).fetchone()
                    if tag_row is not None:
                        conn.execute(
                            "INSERT OR IGNORE INTO Recipe_Tags (recipe_id, tag_id) VALUES (?, ?)",
                            (recipe_id, tag_row[0]),
                        )

        if steps:
            for i, step_text in enumerate(steps.split("\n"), start=1):
                step_text = step_text.strip()
                if step_text:
                    conn.execute(
                        "INSERT OR IGNORE INTO Preparation_Steps (recipe_id, step_number, instruction) VALUES (?, ?, ?)",
                        (recipe_id, i, step_text),
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


@app.route("/recipes_by_tag", methods=["GET"])
def recipes_by_tag():
    tag = request.args.get("tag", "").strip()

    conn = get_db_connection()
    try:
        if not tag:
            rows = conn.execute("SELECT name FROM Tags ORDER BY name").fetchall()
            if not rows:
                return render_template_string("<p>No tags available.</p>")
            chips = "".join(
                f'<span class="tag-chip" hx-get="/recipes_by_tag?tag={row["name"]}" '
                f'hx-target="#tag-results" hx-swap="innerHTML" '
                f'style="cursor:pointer">{row["name"]}</span> '
                for row in rows
            )
            return render_template_string(
                "<div><strong>All Tags:</strong><br>{{ chips|safe }}</div>",
                chips=chips,
            )

        rows = conn.execute(
            """
            SELECT r.name
            FROM Recipes r
            JOIN Recipe_Tags rt ON r.id = rt.recipe_id
            JOIN Tags t ON rt.tag_id = t.id
            WHERE t.name = ?
            ORDER BY r.name
            """,
            (tag,),
        ).fetchall()

        if not rows:
            return render_template_string(f"<p>No recipes tagged '{tag}'.</p>")

        items = "".join(f"<li>{row['name']}</li>" for row in rows)
        return render_template_string(
            "<div><strong>{{ tag }}</strong><ul>{{ items|safe }}</ul></div>",
            tag=tag,
            items=items,
        )
    finally:
        conn.close()


@app.route("/add_tag", methods=["POST"])
def add_tag():
    recipe_id = request.form.get("recipe_id", "").strip()
    tag_name = request.form.get("tag_name", "").strip()

    if not recipe_id or not tag_name.isdigit():
        return render_template_string("<p class='error'>Valid recipe_id is required.</p>")

    tag_name = tag_name.title()

    conn = get_db_connection()
    try:
        recipe = conn.execute(
            "SELECT id FROM Recipes WHERE id = ?", (int(recipe_id),)
        ).fetchone()
        if recipe is None:
            return render_template_string("<p class='error'>Recipe not found.</p>")

        conn.execute("INSERT OR IGNORE INTO Tags (name) VALUES (?)", (tag_name,))
        tag_row = conn.execute(
            "SELECT id FROM Tags WHERE name = ?", (tag_name,)
        ).fetchone()
        if tag_row is not None:
            conn.execute(
                "INSERT OR IGNORE INTO Recipe_Tags (recipe_id, tag_id) VALUES (?, ?)",
                (int(recipe_id), tag_row[0]),
            )
        conn.commit()
    finally:
        conn.close()

    return render_template_string(
        "<p>Tag '<strong>{{ tag }}</strong>' added to recipe #{{ id }}.</p>",
        tag=tag_name,
        id=recipe_id,
    )


@app.route("/recipe_steps", methods=["GET"])
def recipe_steps():
    recipe_id = request.args.get("recipe_id", "").strip()

    if not recipe_id or not recipe_id.isdigit():
        return render_template_string("<p class='error'>Valid recipe_id is required.</p>")

    conn = get_db_connection()
    try:
        recipe = conn.execute(
            "SELECT id, name FROM Recipes WHERE id = ?", (int(recipe_id),)
        ).fetchone()
        if recipe is None:
            return render_template_string("<p class='error'>Recipe not found.</p>")

        steps = conn.execute(
            "SELECT step_number, instruction FROM Preparation_Steps "
            "WHERE recipe_id = ? ORDER BY step_number ASC",
            (int(recipe_id),),
        ).fetchall()

        if not steps:
            return render_template_string(
                "<p>No steps yet for '{{ name }}'.</p>", name=recipe["name"]
            )

        items = "".join(
            f"<li class='step-item'>{row['instruction']}</li>" for row in steps
        )
        return render_template_string(
            "<div><strong>{{ name }}</strong><ol>{{ items|safe }}</ol></div>",
            name=recipe["name"],
            items=items,
        )
    finally:
        conn.close()


@app.route("/add_step", methods=["POST"])
def add_step():
    recipe_id = request.form.get("recipe_id", "").strip()
    step_number = request.form.get("step_number", "").strip()
    instruction = request.form.get("instruction", "").strip()

    if not recipe_id or not recipe_id.isdigit():
        return render_template_string("<p class='error'>Valid recipe_id is required.</p>")
    if not step_number or not step_number.isdigit():
        return render_template_string("<p class='error'>Valid step_number is required.</p>")
    if not instruction:
        return render_template_string("<p class='error'>Instruction cannot be empty.</p>")

    conn = get_db_connection()
    try:
        recipe = conn.execute(
            "SELECT id FROM Recipes WHERE id = ?", (int(recipe_id),)
        ).fetchone()
        if recipe is None:
            return render_template_string("<p class='error'>Recipe not found.</p>")

        conn.execute(
            "INSERT OR REPLACE INTO Preparation_Steps (recipe_id, step_number, instruction) VALUES (?, ?, ?)",
            (int(recipe_id), int(step_number), instruction),
        )
        conn.commit()

        steps = conn.execute(
            "SELECT step_number, instruction FROM Preparation_Steps "
            "WHERE recipe_id = ? ORDER BY step_number ASC",
            (int(recipe_id),),
        ).fetchall()

        name_row = conn.execute(
            "SELECT name FROM Recipes WHERE id = ?", (int(recipe_id),)
        ).fetchone()
    finally:
        conn.close()

    items = "".join(
        f"<li class='step-item'>{row['instruction']}</li>" for row in steps
    )
    return render_template_string(
        "<div><strong>{{ name }}</strong><ol>{{ items|safe }}</ol></div>",
        name=name_row["name"] if name_row else "Recipe",
        items=items,
    )


if __name__ == "__main__":
    app.run(debug=False)
