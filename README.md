# Sora Union Data Engineer Task

This repo provide a set of preconfigured tools that was used for the Data Enginneer recruitment task:

- Apache Airflow
- Apache Spark
- PostgreSQL DB
- DBT
- Docker & Docker compose
- Cloud Server *(Digital Ocean was used for a part of the task)*

## Usage
- Use the `make` configurations provided [here](Makefile) to deploy the containers and start the services. 
- Run `make help` to view instructions for starting specific containers tailored to different tasks.


###  Data Warehousing & ETL Process
- #### Data warehouse design:
    The schema was designed as a star schema to optimize both analytical queries and operational requirements. The design involved creating `fact` and `dimension` tables from the `Float` and `ClickUp` data, which include the following:
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
    *Client Association*: The `dim_client` table facilitates efficient client-related queries, such as billable hours by client.

>  🚨 Note! :
> The design wasn’t implemented manually; instead, it was done using an automated tool called DBT. DBT is commonly used for data transformations in ELT processes and for building and maintaining data models in both ETL and ELT workflows.

- The dbt models are located in the [dbt_project/models](dbt_project/models) folder, which includes all the model definitions for the fact and dimension tables.

- #### ETL process:
    <img src="static/etl_architecture.png" alt="ELT Architecture" width="600"/>


