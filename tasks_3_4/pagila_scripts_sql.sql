-- 1.Вывести количество фильмов в каждой категории, отсортировать по убыванию.
SELECT COUNT(f.title) AS count_film, c.name AS category
FROM film f
INNER JOIN film_category fc ON f.film_id = fc.film_id
INNER JOIN category c on fc.category_id = c.category_id
GROUP BY category
ORDER BY count_film DESC;

-- 2.Вывести 10 актеров, чьи фильмы большего всего арендовали, отсортировать по убыванию.\
SELECT concat(a.first_name,' ',a.last_name) AS full_name, COUNT(r.rental_id) AS rent_amount
FROM actor a
INNER JOIN film_actor fa on a.actor_id = fa.actor_id
INNER JOIN film f on f.film_id = fa.film_id
INNER JOIN inventory i on f.film_id = i.film_id
INNER JOIN rental r on i.inventory_id = r.inventory_id
GROUP BY full_name
ORDER BY rent_amount DESC
LIMIT 10;

-- 3.Вывести категорию фильмов, на которую потратили больше всего денег. 
SELECT c.name AS category, 
SUM(f.rental_rate * f.rental_duration) as spent -- не уверена на счет показателя, может вместо этого произведения нужно SUM(f.replacement_cost), но смысл запроса не изменится, если нужный показатель в этой таблице.
FROM category c
INNER JOIN film_category fc on c.category_id = fc.category_id
INNER JOIN film f on f.film_id = fc.film_id
GROUP BY category
ORDER BY spent DESC
LIMIT 1

-- 4.Вывести названия фильмов, которых нет в inventory.
SELECT f.title as film
FROM film f 
LEFT JOIN inventory i ON f.film_id = i.film_id
WHERE i.film_id IS NULL

--5.Вывести топ 3 актеров, которые больше всего появлялись в фильмах в категории “Children”. Если у нескольких актеров одинаковое кол-во фильмов, вывести всех..
WITH CTE AS (
    SELECT CONCAT(a.first_name, ' ', a.last_name) AS full_name,
COUNT(f.film_id) AS count_film
FROM actor a
INNER JOIN film_actor fa on a.actor_id = fa.actor_id
INNER JOIN film f on f.film_id = fa.film_id
INNER JOIN film_category fc on f.film_id = fc.film_id
INNER JOIN category c on c.category_id = fc.category_id
WHERE c.name = 'Children'
GROUP BY full_name
ORDER BY count_film DESC) 
	SELECT full_name, count_film
FROM CTE
ORDER BY count_film DESC
FETCH NEXT 3 ROWS WITH TIES;

--6.Вывести города с количеством активных и неактивных клиентов (активный — customer.active = 1). Отсортировать по количеству неактивных клиентов по убыванию.
SELECT ct.city AS city, 
SUM(CASE WHEN c.active = 1 THEN 1  
ELSE 0 END) AS active_customers,
SUM(CASE WHEN c.active = 0 THEN 1  
ELSE 0 END) AS inactive_customers
FROM city ct 
INNER JOIN address a ON ct.city_id = a.city_id
INNER JOIN customer c ON a.address_id = c.address_id
GROUP BY city
ORDER BY inactive_customers DESC


--7.Вывести категорию фильмов, у которой самое большое кол-во часов суммарной аренды в городах (customer.address_id в этом city), и которые начинаются на букву “a”. 
--То же самое сделать для городов в которых есть символ “-”. Написать все в одном запросе.
WITH CTE as (
SELECT ct.city, c.address_id,
cat.name as category,
sum(date_part('day', r.return_date::timestamp - r.rental_date::timestamp)*24+
      date_part('hour', r.return_date::timestamp - r.rental_date::timestamp)) as rental_hours_sum
FROM category cat
INNER JOIN film_category fc ON cat.category_id = fc.category_id
INNER JOIN film f ON fc.film_id = f.film_id
INNER JOIN inventory i ON f.film_id = i.film_id
INNER JOIN rental r ON i.inventory_id = r.inventory_id
INNER JOIN customer c ON r.customer_id = c.customer_id
INNER JOIN address a ON c.address_id = a.address_id
INNER JOIN city ct ON a.city_id = ct.city_id
WHERE ct.city LIKE 'a%' or ct.city LIKE '%-%'
GROUP BY ct.city, c.address_id,
category order by rental_hours_sum desc)
SELECT category, city, rental_hours_sum
FROM 
(
SELECT category, city, rental_hours_sum, 
MAX(rental_hours_sum) OVER () as rental_hours_MAX
FROM CTE
WHERE city LIKE '%-%'
) r
WHERE rental_hours_sum=rental_hours_MAX 
UNION ALL 
SELECT category, city, rental_hours_sum
FROM 
(
SELECT category, city, rental_hours_sum, 
MAX(rental_hours_sum) OVER () as rental_hours_MAX
FROM CTE
WHERE city LIKE 'a%'
) t
WHERE rental_hours_sum=rental_hours_MAX 