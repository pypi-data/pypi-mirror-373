import mysql.connector
kwargs = {"host": 'global-aliyun-fat-dataplatform-master01', "username": 'root',
          "password": 'root', "database": 'dbt', "port": 9030}

connection = mysql.connector.connect(**kwargs)

sql = f"""
    select
        null as "database",
        tbl.table_name as name,
        tbl.table_schema as "schema",
        case when tbl.table_type = 'BASE TABLE' then 'table'
             when tbl.table_type = 'VIEW' and mv.table_name is null then 'view'
             when tbl.table_type = 'VIEW' and mv.table_name is not null then 'materialized_view'
             when tbl.table_type = 'SYSTEM VIEW' then 'system_view'
             else 'unknown' end as table_type
    from information_schema.tables tbl
             left join (select Name as table_name, Name as TABLE_SCHEMA from mv_infos("database"="dbt")) mv
                       on tbl.TABLE_SCHEMA = mv.TABLE_SCHEMA
                           and tbl.TABLE_NAME = mv.TABLE_NAME
    where tbl.table_schema = 'dbt'
"""

sql = "show databases"
cursor = connection.cursor()
cursor.execute(sql)

fetchall = cursor.fetchall()

print(f"fetchall: {fetchall}")
