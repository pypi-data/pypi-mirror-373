{% macro run_hooks(hooks, inside_transaction=True) %}
    {% for hook in hooks  %}
        {% if not inside_transaction and loop.first %}
            {% call statement(auto_begin=False) %}
                commit;
            {% endcall %}
        {% endif %}
        {% set rendered = render(hook.get('sql')) | trim %}
        {% if (rendered | length) > 0 %}
            {% call statement(auto_begin=inside_transaction) %}
                {{ rendered }}
            {% endcall %}
        {% endif %}
    {% endfor %}
{% endmacro %}