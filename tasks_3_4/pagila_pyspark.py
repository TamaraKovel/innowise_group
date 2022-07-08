#!/usr/bin/env python
# coding: utf-8

# In[199]:


import findspark
findspark.init()


# In[200]:


import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import Row
import pyspark.sql.functions as F
from pyspark.sql.functions import *
from pyspark.sql.window import Window


spark = SparkSession.builder.config("spark.jars", "C:\Spark\spark-3.3.0-bin-hadoop2\jars\postgresql-42.2.5.jar")     .master("local").appName("PySpark_Postgres_test").getOrCreate()

film = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "film")     .option("user", "postgres").option("password", "123456").load()
film_category = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "film_category")     .option("user", "postgres").option("password", "123456").load()
category = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "category")     .option("user", "postgres").option("password", "123456").load()
actor = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "actor")     .option("user", "postgres").option("password", "123456").load()
address = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "address")     .option("user", "postgres").option("password", "123456").load()
city = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "city")     .option("user", "postgres").option("password", "123456").load()
country = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "country")     .option("user", "postgres").option("password", "123456").load()
customer = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "customer")     .option("user", "postgres").option("password", "123456").load()
film_actor = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "film_actor")     .option("user", "postgres").option("password", "123456").load()
inventory = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "inventory")     .option("user", "postgres").option("password", "123456").load()
payment = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "payment")     .option("user", "postgres").option("password", "123456").load()
rental = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "rental")     .option("user", "postgres").option("password", "123456").load()
staff = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "staff")     .option("user", "postgres").option("password", "123456").load()
store = spark.read.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/pagila")     .option("driver", "org.postgresql.Driver").option("dbtable", "store")     .option("user", "postgres").option("password", "123456").load()


# 1.Вывести количество фильмов в каждой категории, отсортировать по убыванию.
# SELECT COUNT(f.title) AS count_film, c.name AS category
# FROM film f
# INNER JOIN film_category fc ON f.film_id = fc.film_id
# INNER JOIN category c on fc.category_id = c.category_id
# GROUP BY category
# ORDER BY count_film DESC;

# In[228]:


count_film = (
film.join(film_category, film.film_id == film_category.film_id, 'inner')
    .join(category, film_category.category_id == category.category_id, 'inner').select('name','title')
).groupby('name').count().orderBy(F.col("count").desc().show()


# 2.Вывести 10 актеров, чьи фильмы большего всего арендовали, отсортировать по убыванию

# In[227]:


full_actor = (
    actor.withColumn('full_name', 
                    F.concat(F.col('first_name'),F.lit(' '), F.col('last_name')))
)
count_actor = (
 full_actor.join(film_actor, full_actor.actor_id == film_actor.actor_id, 'inner')
	.join(film, film_actor.film_id == film.film_id)
	.join(inventory, film.film_id == inventory.film_id, 'inner')
	.join(rental, inventory.inventory_id == rental.inventory_id).select('full_name','rental_id')
).groupby('full_name').count().orderBy(F.col("count").desc()).show(10)


# 3.Вывести категорию фильмов, на которую потратили больше всего денег. 

# In[226]:


film_spent = (
    film.withColumn('spent', F.col('rental_rate') * F.col('rental_duration'))
)
df = (
	category.join(film_category, category.category_id == film_category.category_id)
	.join(film_spent, film_category.film_id == film_spent.film_id).select('name', 'spent')
).groupBy('name').sum('spent').orderBy(F.sum('spent').desc()).show()


# 4.Вывести названия фильмов, которых нет в inventory.

# In[225]:


inventory1 = inventory.withColumnRenamed("film_id", "inventory_film_id")
join_f_i = (
    film.join(inventory1, film.film_id == inventory1.inventory_film_id, 'left')
    .filter('inventory_film_id IS NULL')
    .select('title')
).show()


# 5.Вывести топ 3 актеров, которые больше всего появлялись в фильмах в категории “Children”. 
# Если у нескольких актеров одинаковое кол-во фильмов, вывести всех.

# In[224]:


film1 = film.withColumnRenamed("film_id", "film_film_id")
top_actor = (
 full_actor.join(film_actor, full_actor.actor_id == film_actor.actor_id, 'inner')
	.join(film1, film_actor.film_id == film1.film_film_id, 'inner')
	.join(film_category, film1.film_film_id == film_category.film_id, 'inner')
	.join(category, film_category.category_id == category.category_id, 'inner')
	.filter('name = "Children"')
).groupby('full_name').count().orderBy(F.col("count").desc())
windowSpec = Window.orderBy(F.desc("count"))
top_actor = top_actor.withColumn("dense_rank", F.dense_rank().over(windowSpec))
top_actor.where(top_actor.dense_rank <= 3).show()


# 6.Вывести города с количеством активных и неактивных клиентов (активный — customer.active = 1). Отсортировать по количеству неактивных клиентов по убыванию.

# In[221]:


active_city = (
 city.join(address, city.city_id == address.city_id, 'inner')
	.join(customer, address.address_id == customer.address_id, 'inner')
)
active_city1 = (
    active_city.groupBy("city").agg(F.sum(F.when(active_city.active == 1, 1).otherwise(0)).alias('active_customers'),
    F.sum(F.when(active_city.active == 0, 1).otherwise(0)).alias('inactive_customers')) 
    .orderBy('inactive_customers', ascending=False)
).show()


# 7.Вывести категорию фильмов, у которой самое большое кол-во часов суммарной аренды в городах (customer.address_id в этом city), и которые начинаются на букву “a”. То же самое сделать для городов в которых есть символ “-”. Написать все в одном запросе.

# In[220]:


customer1 = customer.withColumnRenamed("address_id", "c_address_id")
cte = (
category.join(film_category, category.category_id == film_category.category_id)
.join(film, film_category.film_id == film.film_id)
.join(inventory, film.film_id == inventory.film_id)
.join(rental, inventory.inventory_id == rental.inventory_id)
.join(customer1, rental.customer_id == customer1.c_address_id)
.join(address, customer1.c_address_id == address.address_id)
.join(city, address.city_id == city.city_id)
.filter((F.col('city').like('a%') | F.col('city').like('%-%')))
)
cte1 = (
    cte.groupby('city', 'c_address_id', 'name')
    .agg(F.sum(((F.unix_timestamp(cte.return_date) - F.unix_timestamp(cte.rental_date))/3600)).alias('rental_hours_sum'))
    .orderBy('rental_hours_sum', ascending=False)
)
df1 = cte1.select(F.col('name'),F.col('city'), F.col('rental_hours_sum'))
windowSpec = Window.orderBy(F.desc('city'))
c1 = (
    df1.withColumn("max", F.max(F.col('rental_hours_sum')).over(windowSpec))
    .filter((F.col('city').like('a%')
)))
windowSpec = Window.orderBy(F.desc('city'))
c2 = (
    df1.withColumn("max", F.max(F.col('rental_hours_sum')).over(windowSpec))
    .filter((F.col('city').like('%-%')
)))
unionAllDF = c1.unionAll(c2)
all = (
    unionAllDF.select(F.col('name'),F.col('city'), F.col('rental_hours_sum'))
    .filter(F.col('rental_hours_sum') == F.col('max'))

).show()

