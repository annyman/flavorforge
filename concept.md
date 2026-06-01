**Predictive Match — ranked recipe search:**
--------------------------------------------

SELECT r.name, COUNT(i.name) AS match_count
FROM Recipes r
JOIN Recipe_Ingredients ri ON r.id = ri.recipe_id
JOIN Ingredients i ON ri.ingredient_id = i.id
WHERE LOWER(i.name) IN (?, ?, ?)
GROUP BY r.id
ORDER BY match_count DESC
*Logic*: "Given ingredients I have, which recipes use the most of them?"

**Cultural Fusion — cross-cuisine lookup:**
-------------------------------------------
SELECT r.name
FROM Recipes r
JOIN Recipe_Cuisines rc ON r.id = rc.recipe_id
JOIN Cuisines c ON rc.cuisine_id = c.id
WHERE c.name IN (?, ?)
GROUP BY r.id
HAVING COUNT(DISTINCT c.id) = 2

*Logic*: "Which recipes belong to both cuisines simultaneously?"

**Recipes by Tag — tag-filtered listing:**
------------------------------------------
SELECT r.name
FROM Recipes r
JOIN Recipe_Tags rt ON r.id = rt.recipe_id
JOIN Tags t ON rt.tag_id = t.id
WHERE t.name = ?
ORDER BY r.name

*Logic*: "Show all recipes that have a given tag."

**Recipe Steps — ordered preparation steps:**
---------------------------------------------
SELECT step_number, instruction
FROM Preparation_Steps
WHERE recipe_id = ?
ORDER BY step_number ASC

*Logic*: "Fetch the step-by-step instructions for a recipe in order."

**Add Step — upsert a preparation step:**
-----------------------------------------
INSERT OR REPLACE INTO Preparation_Steps (recipe_id, step_number, instruction)
VALUES (?, ?, ?)

*Logic*: "Insert or replace a step at a given position — handles re-ordering."
