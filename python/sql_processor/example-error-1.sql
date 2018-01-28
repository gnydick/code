-- "name" is ambiguous
SELECT name, country, population
FROM countries, cities
WHERE captial = cities.name
