{% extends "base.html" %}
{% block title %}Ingredients & Suppliers{% endblock %}

{% block content %}
<table>
	<caption>Overview of the Ingredients entity.</caption>
	<thead>
		<tr>
			<!-- this for loop will grab the column title data from app.py and translate it to the template -->
			{% for title in column_headers %}
			<th>{{ title }}</th>
			{% endfor %}
		</tr>
	</thead>
	<tbody>
		<tr>
		<!-- this for loop will output the raw value set of ingredients data from app.py -->
		{% for set in sample_values %}
		<tr>
			<!-- lastly, each type of data in the set is added to each row -->
			{% for value in set %}
			<td>{{ value }}</td>
			{% endfor %}
		</tr>
		{% endfor %}
	</tr>
	</tbody>
</table>

<div>
	<form action="#" method="POST">
		{{ ingredient_form.hidden_tag() }}
		<fieldset>
			<legend>Ingredients:</legend>
			<div>
				{{ form.ingredient_id.label }}
				{{ form.ingredient_id }}
			</div>
			<div>
				{{ form.order_date.label }}
				{{ form.order_date }}
			</div>
			<div>
				{{ form.ingredient_name.label }}
				{{ form.ingredient_name }}
			</div>
			<div>
				{{ form.ingredient_cost.label }}
				{{ form.ingredient_cost }}
			</div>
			<div>
				{{ form.order_id.label }}
				{{ form.order_id }}
			</div>
			<div>
				{{ form.submit.label }}
				{{ form.submit }}
			</div>
		</fieldset>
	</form>
</div>
{% endblock %}