{% for quick_note in data.quick_note_list.list_of_quick_note -%}
<!--BEGIN {% for name, value in quick_note %}{{name}}={% if value is integer %}{{value}}{% else %}"{{value}}"{% endif %} {% endfor %}-->
# {{quick_note.title}}
{{quick_note.text}}
<!--END-->

{% endfor %}
