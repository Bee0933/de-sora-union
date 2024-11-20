up-etl:
	# start etl containers -> Postgres & DBT
	docker-compose up -d database dbt

up-airflow:
	# start Airflow containers
	docker-compose -f airflow/docker-compose.yaml up -d

up-spark:
	# start spark containers (cluster)
	docker-compose up -d spark-master spark-worker-1 spark-worker-2 spark-worker-3 spark-worker-4

down-etl:
	# stop ETL containers -> Postgres & DBT
	docker-compose down database dbt

down-airflow:
	# stop Airflow containers
	docker-compose -f airflow/docker-compose.yaml down

down-spark:
	# stop spark containers
	docker-compose down spark-master spark-worker-1 spark-worker-2 spark-worker-3 spark-worker-4

dbt-build:
	# build DBT models on database
	docker compose run dbt build

dbt-compile:
	# compile DBT models to check for errors
	docker compose run dbt compile

dbt-deps:
	# install dependencies required by DBT
	docker compose run dbt deps

spark-job:
	# submit spark job to spark cluster via the master url
	docker exec -it sora-spark-master-1 spark-submit --master spark://172.18.0.2:7077 jobs/spark_analysis.py

help:
	@echo "Available targets:"
	@echo "  up-etl          - Start ETL containers (Postgres & DBT)"
	@echo "  up-airflow      - Start Airflow containers"
	@echo "  up-spark        - Start Spark containers (cluster)"
	@echo "  down-etl        - Stop ETL containers (Postgres & DBT)"
	@echo "  down-airflow    - Stop Airflow containers"
	@echo "  down-spark      - Stop Spark containers"
	@echo "  dbt-build       - Build DBT models on the database"
	@echo "  dbt-compile     - Compile DBT models to check for errors"
	@echo "  dbt-deps        - Install dependencies required by DBT"
	@echo "  spark-job       - Submit Spark job to Spark cluster via master URL"
