# Sora Union Data Engineer Task

This repo provides a set of preconfigured tools that was used for the Data Engineer recruitment task:

- Apache Airflow
- Apache Spark
- PostgreSQL DB
- DBT

Other tools required
- Docker & Docker compose
- DBeaver (*or any DB management tool of choice*)
- Cloud Server *(Digital Ocean was used for a part of the task)*

## Usage
- Use the `make` configurations provided [here](Makefile) to deploy the containers and start the services. 
- Run `make help` to view instructions for starting specific containers tailored to different tasks.


###  1. Data Warehousing & ETL Process
- #### Data warehouse design:
    <!-- The schema was designed as a star schema to optimize both analytical queries and operational requirements. The design involved creating `fact` and `dimension` tables from the `Float` and `ClickUp` data, which include the following:
    - `fact_project_activity`; which corresponds to individual activities related to a project
    - `dim_client`; contains client-specific information
    - `dim_project`; contains details about projects
    - `dim_role`; contains roles associated with team members or tasks 
    - `dim_task`; tracks task-related information
    - `dim_team_member`; contains data about team members
    - `dim_date`; provides temporal context for activities <br>

- The fact table contains measurable data and serves as the central component of the star schema. This allows for the aggregation and analysis of metrics such as total hours worked on a project or task, hours billed to a client, and team performance by role or time period.

    fact `fact_project_activity` table columns:
    Activity ID (PK), Team Member ID (FK), Project ID (FK), Role ID (FK), Client ID (FK), Task ID (FK), Date ID (FK), Hours, Billable, Note

- The dimension tables provide descriptive attributes, or context, for fact data in a star schema which allow for categorization,   filtering, and grouping of data during analysis
    
    dimension tables columns:
    - `dim_client`: Client ID (PK), Client Name
    - `dim_project`: Project ID (PK), Client ID (FK), Project Name, Project Start Date, Project End Date
    - `dim_role`: Role ID (PK), Role Name
    - `dim_task`: Task ID (PK), Task Name
    - `dim_team_member`: Team Member ID (PK): Role ID (FK): Team Member Name
    - `dim_date`, Date ID (PK), Date, Year, Month, Month Name, Day, Weekday ISO, Weekday Name, Quarter, Is Weekend

- key design features <br>
    *Star Schema*: The design uses a star schema with a central fact table connected to dimension tables for easy navigation and optimized OLAP queries. <br>
    *Measurable and Descriptive Data*: The `fact_project_activity` table stores measurable values, while dimension tables provide descriptive context. <br>
    *Time-Based Analysis*: The `dim_date` is a generated dimension that supports temporal analysis like tracking hours worked or monthly trends. <br>
    *Role-Based Analysis*: The `dim_role` and `dim_team_member` tables enable analysis by roles and team member contributions. <br>
    *Task and Project Hierarchies*: The `dim_task` and `dim_project` tables allow both granular task-level and high-level project analysis. <br>
    *Client Association*: The `dim_client` table facilitates efficient client-related queries, such as billable hours by client. -->

>  🚨 Note! :
> The design wasn’t implemented manually; instead, it was done using an automated tool called DBT. DBT is commonly used for data transformations in ELT processes and for building and maintaining data models in both ETL and ELT workflows.

- The dbt models are located in the [dbt_project/models](dbt_project/models) folder, which includes all the model definitions for the fact and dimension tables.

- materilaization used for models
    src_ data (ephrmeral materialization) --> dim & fact data  (table materilazation) <br>

    The ephemeral materialization is used for temporary, intermediate transformations that don't need to be stored permanently, helping to keep the pipeline lightweight and efficient. <br>

    The table materialization is used for final models that need to be stored persistently in the data warehouse for analysis and reporting <br>

- #### ETL process:
    <!-- <div style="text-align: center;">
        <img src="static/etl_architecture.png" alt="ELT Architecture" width="600"/>
    </div> <br> -->
    <img src="static/etl_architecture.png" alt="ELT Architecture" width="600"/>
    

    Apache Airflow was set up and used to carry out the ETL tasks by connecting to and extracting the Float and ClickUp data from the provided Google Sheets source, based on the sheet ID and name. The data was loaded into a Pandas dataframe, cleaned, wrangled, and then ingested into a PostgreSQL database, which serves as the data warehouse for the task.   

    > Postgres is an operational database (OLTP), which is not ideally suited for analytical workflows. While it is optimized and used by some for analytical processes (OLAP), a better recommendation would be data warehouse solutions like BigQuery or Snowflake 

    The DAG codes for the ETL process are available [here](airflow/dags)

    **usage:** <br>
    setup containers: `make up-etl` & `make up-airflow` to start the required services <br>

    access postgres database with:
    * host: `localhost`
    * port: `5432`
    * user: `admin`
    * password: `Password`
    * database name: `postgres`

    Access the Airflow server at `localhost:8080` using the credentials `airflow:airflow`. The DAGs are set up to run hourly but can also be triggered manually to start the process. <br>

    <img src="static/airflow-dags-shot.png" alt="ELT Architecture" width="600"/>

    The airflow setup requires some variables needs to be added in variables tab on admin menu on the UI
    
    ```bash
        FLOAT_SHEET_ID
        FLOAT_SHEET_NAME
        FLOAT_DWH_TABLE_NAME
        CLICKUP_SHEET_ID 
        CLICKUP_SHEET_NAME
        CLICKUP_DWH_TABLE_NAME 
        POSTGRES_HOST
        POSTGRES_PORT
        POSTGRES_USER
        POSTGRES_PASSWORD 
        POSTGRES_DB
    ```
    <img src="static/airflow-etl-process-shot.png" alt="ELT Architecture" width="600"/>

   Trigger the Airflow DAG to perform the three tasks: downloading, transforming, and ingesting data into the database. The workflow is configured to load the cleaned data into the public schema of the database. <br>

   <img src="static/db-clickup-float-data-shot.png" alt="ELT Architecture" width="600"/>

   build the data models with dbt:
   - `make dbt-deps` to install dependencies required by DBT
   - `make dbt-compile` to compile DBT models to check for errors
   - `make dbt-build` to build DBT models on the database

    <img src="static/dim-fact-tables.png" alt="ELT Architecture" width="600"/> <br>
    
    DBT creates all tables according to the model design in the dev schema and runs tests to ensure data integrity.

    <img src="static/dbt-build-w-tests-shot.png" alt="ELT Architecture" width="600"/> <br>

- ####  Data Integrity and cleanliness:
    To ensure data intergrity and cleanliness I used: 

    -  DBT to enforce data quality during the transformation process by applying generic tests [here](dbt_project/models/schema.yaml), to ensure critical columns meet specified rules like: 
        - `Not Null Tests` on `date, client, project, name` columns
        - `Accepted Values Tests`: Ensure boolean fields like `billable` only contain true or false
        - `Consistency Rules`: Validate logical constraints, such as: `start_date` ≤ `end_date` <br>
    
    - Airflow transformation cleans the data during the ETL process


###  2. Database Query Optimization
- The optimized query and its description are available in this [Jupyter notebook](optimized_query/query.ipynb)

 
###  3.  Big Data Processing with Spark or Hive
- #### Spark process:
- For this task, I used Apache Spark to process and analyze a large dataset of Spark job logs from CUHK Labs, with over 33 million records sourced from the [LogHub repository](https://github.com/logpai/loghub). The dataset contains detailed logs of Spark job executions, which provide insights into various aspects of job performance and resource utilization.

    The spark Job code used can be found in the [spark/jobs/spark_analysis.py](spark/jobs/spark_analysis.py) file

    To run this, I set up a Spark cluster using Docker as the host, with one Spark master and four workers, each having 2 cores and 2 GiB of memory. 

    **usage:** <br>
    setup spark containers: 
    - `make up-spark` to spin up the spark containers 
    - download and extract the logs dataset into the `spark/data` folder <br>
        the extracted file should contain `915` folders with `.log` files within the folders with a total of `3852`  files 

        - **how to:** <br>
          ```bash
            wget "https://zenodo.org/records/8196385/files/Spark.tar.gz?download=1" -O Spark.tar.gz

            tar -xzvf Spark.tar.gz
          ```

    <img src="static/spark-logs-folder-files-shot-2.png" alt="ELT Architecture" width="600"/> <br>

    - submit the spark job to process the files and aggregate the logs data with `spark-job`. This will submit spark job to spark cluster via the master url. The spark code is written to dynamically read all the log files in all the sub folders and parse the 33 mllion worth of records for processing.

    <img src="static/spark-records-processed.png" alt="ELT Architecture" width="600"/> <br>

    >  🚨 Note! :
    > The setup was tested on a cloud server, which is recommended over running it on a local machine. This was done using a DigitalOcean Droplet with the following specs: `8 GB Memory / 2 AMD vCPUs / 100 GB Disk / FRA1 - Ubuntu 24.10 x64` <br>

    The result of the aggregation is shown here: <br>

    <img src="static/spark-job-aggregation-output-shot.png" alt="ELT Architecture" width="600"/> <br>

- #### Approach and Performance Considerations:

    - **Approach:** The code analyzes log data by extracting relevant fields using regular expressions, then aggregating the data by Component and Hour.
        - Data Extraction: Regular expressions was used to parse and extract the various fields from the raw log data
        - Data Cleaning: Missing or empty Date and Time values were handled with default values, and rows with missing Date were filtered out.
        - Timestamp Creation: The Date and Time columns were combined into a Timestamp and the hour was extracted for aggregation.

    - **Performance Considerations:**
        - Adaptive Query Execution: Spark’s adaptive query execution was enabled to optimize the execution plan at runtime
        - Shuffle Partitions: The `shuffle partitions` were set to `16` to balance the workload and improve parallelism.
        - Coalescing: The number of partitions was reduced to `8` using `coalesce` to optimize performance during aggregation, minimizing the overhead of excessive partitions

###  4. Data Modeling Techniques
- ## Data Model Diagrams 
    <img src="static/dim-model.png" alt="ELT Architecture" width="600"/> <br>

    <img src="static/erd.png" alt="ELT Architecture" width="600"/> <br>

- ## Design Decisions
    - **Analytical Purpose**
        The data warehouse schema was designed using a star schema to optimize performance for analytical queries while maintaining simplicity. This approach centers around a fact table and related dimension tables to allow for efficient aggregation and detailed reporting.

        1) The central fact table, fact_project_activity, holds measurable data (e.g., hours worked, billable amounts) and links to dimension tables for descriptive context, such as client, project, role, task, team member, and date.

        2) Fact Table Design: The fact_project_activity table tracks project-related activities with foreign keys referencing dimensions like project, client, role, and time. Metrics such as Hours and Billable facilitate detailed analysis.

        3) The dimension tables include dim_client, which stores client data for related queries; dim_project, providing project details with start and end dates; dim_role, categorizing data by roles for performance analysis; dim_task, enabling task-level tracking; dim_team_member, which tracks team members and their roles; and dim_date, supporting temporal analysis with attributes like year, month, and quarter.

        4) The dim_date enables time-based analysis (e.g., monthly trends), while dim_role and dim_team_member support role- and team-level performance tracking.

        5) Client-Centric Reporting: The dim_client dimension facilitates client-specific analysis, such as tracking billable hours or evaluating performance by client.

    - **Operational Use:**
        The schema follows a normalized relational design optimized for managing and analyzing project-related activities.

        1) Each entity (e.g., Client, Project, Task, Employee, Time Entry) is represented by a separate table to ensure data consistency, prevent redundancy, and maintain referential integrity through foreign key relationships. These relationships enforce data integrity across the schema.

        2) Entity Definitions as `CLIENT`, `PROJECT`, `TASK`, `EMPLOYEE`, and `TIME_ENTRY` store essential data about clients, projects, tasks, employees, and time logs.

        3) This design supports project-level, task-level, and employee productivity analysis for reports on billable hours and other metrics.

        4) Primary keys adopted ensure unique records, while foreign keys maintain relationships between tables for data consistency.

        5) The design is scalable as it supports easy growth as more clients, projects, and logs can be added without impacting the overall structure.

   
