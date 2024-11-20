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
	docker exec -it dev-spark-master-1 spark-submit --master spark://172.18.0.2:7077 spark/jobs/spark_analysis.py