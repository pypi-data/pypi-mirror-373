/*
 * Copyright 2021-present StarRocks, Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https:*www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

{% macro starrocks__create_table_as(temporary, relation, sql) -%}
  {%- set sql_header = config.get('sql_header', none) -%}
  {%- set engine = config.get('engine', 'OLAP') -%}
  {%- set indexs = config.get('indexs') -%}

{{ sql_header if sql_header is not none }}

  create table {{ relation.include(database=False) }}
  {%- if indexs is not none -%}
    {%- for index in indexs -%}
      {%- set columns = index.get('columns') -%}
      (
        INDEX idx_{{ columns | replace(" ", "") | replace(",", "_") }} ({{ columns }}) USING BITMAP
      )
    {%- endfor -%}
  {%- endif -%}
  {%- if engine == 'OLAP' -%}
    {{ starrocks__olap_table(True) }}
  {%- else -%}
    {%- set msg -%}
      "ENGINE = {{ engine }}" does not support, currently only supports 'OLAP'
    {%- endset %}
    {{ exceptions.raise_compiler_error(msg) }}
  {%- endif -%}

  as {{ sql }}

{%- endmacro %}

{% materialization table, adapter='starrocks' %}

    {%- set existing_relation = load_cached_relation(this) -%}
    {%- set target_relation = this.incorporate(type='table') %}

    {%- set intermediate_relation =  make_intermediate_relation(target_relation) -%}
    -- the intermediate_relation should not already exist in the database; get_relation
    -- will return None in that case. Otherwise, we get a relation that we can drop
    -- later, before we try to use this name for the current operation
    {%- set preexisting_intermediate_relation = load_cached_relation(intermediate_relation) -%}
    /*
        See ../view/view.sql for more information about this relation.
    */
    {%- set backup_relation_type = 'table' if existing_relation is none else existing_relation.type -%}
    {%- set backup_relation = make_backup_relation(target_relation, backup_relation_type) -%}
    -- as above, the backup_relation should not already exist
    {%- set preexisting_backup_relation = load_cached_relation(backup_relation) -%}
    -- grab current tables grants config for comparision later on
    {% set grant_config = config.get('grants') %}

    -- drop the temp relations if they exist already in the database
    {{ drop_relation_if_exists(preexisting_intermediate_relation) }}
    {{ drop_relation_if_exists(preexisting_backup_relation) }}

    {% if pre_hooks | length > 0 %}
        {{ run_hooks(pre_hooks, inside_transaction=False) }}
    {% endif %}

    -- build model
    {% call statement('main', auto_begin=False) -%}
    {{ get_create_table_as_sql(False, intermediate_relation, sql) }}
    {%- endcall %}

    -- cleanup
    {% if existing_relation is not none %}
    /* Do the equivalent of rename_if_exists. 'existing_relation' could have been dropped
       since the variable was first set. */
    {% set existing_relation = load_cached_relation(existing_relation) %}
    {% if existing_relation is not none %}
    {{ adapter.rename_relation(existing_relation, backup_relation) }}
    {% endif %}
    {% endif %}

    {{ adapter.rename_relation(intermediate_relation, target_relation) }}

    {% do create_indexes(target_relation) %}

    {{ run_hooks(post_hooks, inside_transaction=True) }}

    {% set should_revoke = should_revoke(existing_relation, full_refresh_mode=True) %}
    {% do apply_grants(target_relation, grant_config, should_revoke=should_revoke) %}

    {% do persist_docs(target_relation, model) %}

    -- `COMMIT` happens here
{#    {{ adapter.commit() }}#}

    -- finally, drop the existing/backup relation after the commit
    {{ drop_relation_if_exists(backup_relation) }}

    {% if post_hooks | length > 0 %}
        {{ run_hooks(post_hooks, inside_transaction=False) }}
    {% endif %}

    {{ return({'relations': [target_relation]}) }}
{% endmaterialization %}

