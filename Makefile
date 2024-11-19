up-etl:
	docker-compose up -d database dbt

up-airflow:
	docker-compose -f airflow/docker-compose.yaml up -d

up-spark:
	docker-compose up -d spark-master spark-worker-1 spark-worker-2 spark-worker-3 spark-worker-4

down-etl:
	docker-compose down database dbt

down-airflow:
	docker-compose -f airflow/docker-compose.yaml down

down-spark:
	docker-compose down spark-master spark-worker-1 spark-worker-2 spark-worker-3 spark-worker-4

dbt-build:
	docker compose run dbt build

dbt-compile:
	docker compose run dbt compile

dbt-deps:
	docker compose run dbt deps