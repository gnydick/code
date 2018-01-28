-- Capital cities
SELECT b.name AS name, a.name AS country, population, food
FROM countries AS a, cities AS b, foods AS c
WHERE capital = b.name AND b.population > 800 AND b.name = c.name

