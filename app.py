import os
from flask import Flask, render_template, request, url_for, redirect
from forms import EmployeeManagerForm, LocationForm, IngredientsForm, SuppliersForm, OrderForm, Customers, OrdersSearchForm
from db_connector import connect_to_database, execute_query

app = Flask(__name__)

# required to keep sessions secure
# need to create a config file to keep key and DB configs later
app.config['SECRET_KEY'] = '7cd4739b6ecbf78e2fb020b7f663a979'

# dummy data
headers = ['Name', 'Start Date', 'Vacation', 'Managed by', 'Location', "", ""]
data = [
    ['Alex Shin', '10/25/2011', 'Yes', 'Daniel Yu', 'Los Angeles'],
    ['Daniel Yu', '11/11/2004', 'No', 'None', 'Los Angeles'],
    ['John Doe', '1/1/2021', 'No', 'Daniel Yu', 'Los Angeles'],
    ['Jane Doe', '1/1/2021', 'No', 'Daniel Yu', 'Los Angeles']
]

location_headers = ['City', 'State', 'Zip Code', '', '']
location_data = [
    ['Los Angeles', 'California', '90017'],
    ['Seattle', 'Washington', '98101'],
    ['Austin', 'Texas', '73301'],
    ['New York', 'New York', '10001']
]

# Just some dummy data for Step 3
ingredient_suppliers_h = ["Order Date", "Name", "Cost ($)", "Order ID", "", ""]
ingredient_suppliers_v = ingredient_values = [
    ["2021-01-01", "ground beef", 10, 101],
    ["2021-01-02", "buns", 5, 102],
    ["2021-01-03", "tomatoes", 5, 103],
    ["2021-01-04", "onions", 2, 104],
    ["2021-01-05", "ground beef", 10, 105],
    ["2021-01-06", "ketchup", 2, 106]
]

suppliers_headers = ["Name", "", ""]
suppliers_values = ["Johnson Ville", "Meat Industry", "Lettuce Factory"]

ingredients_suppliers_headers = ["Ingredient", "Supplier", "", ""]
ingredients_suppliers_values = [
    ["Ground Beef", "Johnson Ville"],
    ["Ground Beef", "Meat Industry"]
]

orders_customers_h = ["Date", "Customer ID", "Sales Amount ($)", "First Name", "Last Name", "E-mail", "Phone Number",
                      "", ""]
orders_customers_v = [
    ["2021-01-01", 500001, 10, "Daniel", "Yu", "danielyu@osu.com", "808-254-1999"],
    ["2021-01-02", 500001, 15, "Daniel", "Yu", "danielyu@osu.com", "808-254-1999"],
    ["2021-01-03", 500003, 20, "Alex", "Shin", "alexshin@osu.com", "702-153-0211"],
    ["2021-01-06", 500003, 110, "Alex", "Shin", "alexshin@osu.com", "702-153-0211"],
    ["2021-01-07", 500003, 220, "Alex", "Shin", "alexshin@osu.com", "702-153-0211"],
    ["2021-01-08", 500003, 27, "Alex", "Shin", "alexshin@osu.com", "702-153-0211"],
    ["2021-01-09", 500003, 38.70, "Alex", "Shin", "alexshin@osu.com", "702-153-0211"]
]

customer_headers = ["First Name", "Last Name", "E-mail", "Phone Number", "Location", "", ""]
customer_values = [
    ["Daniel", "Yu", "danielyu@osu.com", "808-254-1999", "Los Angeles"],
    ["Alex", "Shin", "alexshin@osu.com", "702-153-0211", "Los Angeles"]
]


# route for the homepage (root) is defined, but it's html is just the base
@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')


def validator(data_list):
    all_valid = True

    for value in data_list:
        if value is None:
            all_valid = False

    return all_valid


@app.route("/employees-locations", methods=['GET', 'POST'])
def employees_locations():
    db_connection = connect_to_database()
    employee_manager_form = EmployeeManagerForm(request.form)
    location_form = LocationForm(request.form)

    if request.method == 'POST':
        first_name = employee_manager_form.first_name.data
        last_name = employee_manager_form.last_name.data
        start_date = employee_manager_form.start_date.data

        if employee_manager_form.status.data is True:
            status = "vacation"
        else:
            status = "active"

        manager = employee_manager_form.manager.data

        if manager is True:
            managed_by = None
        else:
            managed_by_query = "SELECT manager_id FROM Managers WHERE first_name = %s;"
            managed_by_result = execute_query(db_connection, managed_by_query, str(employee_manager_form.managed_by.data)).fetchall()
            managed_by = managed_by_result
        
        store_query = "SELECT store_id FROM Locations WHERE city = %s;"
        store_result = execute_query(db_connection, store_query, str(employee_manager_form.store.data)).fetchall() 
        store = store_result
        
        city = location_form.city.data
        state = location_form.state.data
        zip_code = location_form.zip_code.data

        # employees_managers
        if managed_by is not None:
            employee_input_data = (first_name, last_name, start_date, status, managed_by, store)
            employee_input_query = "INSERT INTO Employees (first_name, last_name, start_date, status, emp_manager_id, emp_store_id) \
                                VALUES (%s, %s, %s, %s, %s, %s);"
        else:
            employee_input_data = (first_name, last_name, start_date, status, store)
            employee_input_query = "INSERT INTO Employees (first_name, last_name, start_date, status, emp_store_id) \
                                VALUES (%s, %s, %s, %s, %s);"

        manager_input_data = None
        if manager is True:
            manager_input_data = (first_name, last_name, status, store)
            manager_input_query = "INSERT INTO Managers (first_name, last_name, status, manager_store_id) \
                                   VALUES (%s, %s, %s, %s);"

        # locations
        location_input_data = (city, state, zip_code)
        location_input_query = "INSERT INTO Locations (city, state, zip_code) \
                                VALUES (%s, %s, %s);"

        if validator(location_input_data):
            execute_query(db_connection, location_input_query, location_input_data)
            db_connection.commit()

        if validator(employee_input_data):
            execute_query(db_connection, employee_input_query, employee_input_data)
            if manager_input_data is not None:
                execute_query(db_connection, manager_input_query, manager_input_data)

            db_connection.commit()
        return redirect(url_for("employees_locations"))    

    # for GET requests
    # employees
    employees_managers_query = "SELECT \
                                    CONCAT(Employees.first_name, ' ', Employees.last_name) AS Name, \
                                    Employees.start_date, Employees.status, \
                                    CONCAT(Managers.first_name, ' ', Managers.last_name) AS ManagedBy, \
	                                Locations.city \
                                FROM Employees \
                                LEFT JOIN Managers ON Managers.manager_id = Employees.emp_manager_id \
                                LEFT JOIN Locations ON Locations.store_id = Employees.emp_store_id \
                                ORDER BY start_date;"
    employees_managers_results = execute_query(db_connection, employees_managers_query).fetchall()

    # locations
    location_query = "SELECT city, state, zip_code FROM Locations;" 
    location_results = execute_query(db_connection, location_query).fetchall()

    # dropdowns
    managed_by_name_query = "SELECT first_name FROM Managers;"
    managed_by_name_results = execute_query(db_connection, managed_by_name_query).fetchall()
    managed_by_choices = []

    for choices in managed_by_name_results:
        managed_by_choices.append(choices[0])

    employee_manager_form.managed_by.choices += managed_by_choices
    
    store_city_query = "SELECT city FROM Locations;"
    store_city_results = execute_query(db_connection, store_city_query).fetchall()
    store_city_choices = []

    for choices in store_city_results:
        store_city_choices.append(choices[0])

    employee_manager_form.store.choices = store_city_choices


    return render_template('employees_locations.html', headers=headers, data=employees_managers_results, location_headers=location_headers,
                           location_data=location_results, emp_man_form=employee_manager_form, loc_form=location_form)


# route for the ingredients & suppliers page
@app.route("/ingredients-suppliers", methods=["GET", "POST"])
def ingredients_suppliers():
    db_connection = connect_to_database()


    ingredient_form = IngredientsForm()
    supplier_form = SuppliersForm()

    # for POST requests
    if request.method == 'POST':
        order_date = ingredient_form.order_date.data
        ingredient_name = ingredient_form.ingredient_name.data
        ingredient_cost = ingredient_form.ingredient_cost.data
        supplier = ingredient_form.supplier.data
        order_id = ingredient_form.order_id.data

        # grab user's input from add new Ingredient form, and INSERT into the db
        ingredients_input_data = (order_date, ingredient_name, ingredient_cost, order_id)
        ingredient_input_query = "INSERT INTO Ingredients (order_date, ingredient_name, ingredient_cost, order_num) " \
                                 "VALUES (%s, %s, %s, %s);"

        supplier_name = supplier_form.supplier_name.data
        supplier_input_data = (supplier_name,)

        supplier_input_query = "INSERT INTO Suppliers (supplier_name) VALUES (%s);"
        get_supplier_id_query = "SELECT supplier_id FROM `Suppliers` WHERE supplier_name = (%s)"
        get_supplier_id_results = execute_query(db_connection, get_supplier_id_query, (supplier,)).fetchall()

        if validator(ingredients_input_data) is True:
            execute_query(db_connection, ingredient_input_query, ingredients_input_data)

            # get latest ingredient ID, that was just created
            get_ingredient_id_query = "SELECT ingredient_id FROM `Ingredients` ORDER BY ingredient_id DESC LIMIT 1"
            get_ingredient_id_results = execute_query(db_connection, get_ingredient_id_query).fetchall()

            # add ingredient_id and supplier_id to the Ingredients_Suppliers intersection table, to establish a M:M relationship
            add_ingredient_supplier_IDs = "INSERT INTO Ingredients_Suppliers (ing_id, sup_id) VALUES (%s, %s)"
            IDs_parsed = (get_ingredient_id_results[0][0], get_supplier_id_results[0][0])

            execute_query(db_connection, add_ingredient_supplier_IDs, IDs_parsed)

            db_connection.commit()

        elif validator(supplier_input_data) is True:
            execute_query(db_connection, supplier_input_query, supplier_input_data)

            db_connection.commit()

        return redirect(url_for('ingredients_suppliers'))

    # for GET requests
    ingredients_query = "SELECT order_date, ingredient_name, ingredient_cost, order_num FROM `Ingredients`;"
    suppliers_query = "SELECT supplier_name FROM Suppliers;"
    ingredients_suppliers_query = "SELECT ingredient_name, supplier_name FROM `Ingredients` \
            INNER JOIN Ingredients_Suppliers ON Ingredients_Suppliers.ing_id = Ingredients.ingredient_id \
            INNER JOIN Suppliers ON Suppliers.supplier_id = Ingredients_Suppliers.sup_id \
            ORDER BY ingredient_name;"

    supplier_results_parsed = []
    supplier_choices = []
    order_id_choices = []
    ingredients_supplied_choices = []

    # select suppliers, order_id, and ingredients from the db
    supplier_choices_query = "SELECT supplier_name FROM `Suppliers`;"
    order_id_query = "SELECT order_id FROM `Orders`;"
    ingredients_supplied_query = "SELECT ingredient_name FROM `Ingredients`;"

    # execute the above select queries and retrieve the data
    ingredient_results = execute_query(db_connection, ingredients_query).fetchall()
    suppliers_results = execute_query(db_connection, suppliers_query).fetchall()
    ingredients_suppliers_results = execute_query(db_connection, ingredients_supplied_query).fetchall()

    supplier_choices_results = execute_query(db_connection, supplier_choices_query).fetchall()
    ingredients_supplied_results = execute_query(db_connection, ingredients_supplied_query).fetchall()
    order_id_results = execute_query(db_connection, order_id_query).fetchall()

    # the data retrieved from the db are a tuple of tuples, here we take each individual tuple and add to a list (to
    # get a list of all items)
    for choices in order_id_results:
        order_id_choices.append(choices[0])

    for choices in supplier_choices_results:
        supplier_choices.append(choices[0])

    for choices in ingredients_supplied_results:
        ingredients_supplied_choices.append(choices[0])

    for supplier in suppliers_results:
        supplier_results_parsed.append(supplier[0])

    # from the list of items, assign them to each Form's choices option
    ingredient_form.supplier.choices = supplier_choices
    ingredient_form.order_id.choices = order_id_choices
    supplier_form.ingredients_supplied.choices = ingredients_supplied_choices

    return render_template("ingredients_suppliers.html", title='Add/Edit/Delete Ingredients & Suppliers',
                           ingredient_form=ingredient_form,
                           ingredients_suppliers_headers=ingredients_suppliers_headers,
                           ingredients_suppliers_values=ingredients_suppliers_values,
                           suppliers_headers=suppliers_headers, suppliers_values=supplier_results_parsed,
                           supplier_form=supplier_form, ingredient_suppliers_h=ingredient_suppliers_h,
                           ingredient_suppliers_v=ingredient_results
                           )





@app.route("/orders-customers", methods=["GET", "POST"])
def orders_customers():
    # form objects
    search_customer_form = OrdersSearchForm(request.form)
    order_form = OrderForm(request.form)
    customer_form = Customers(request.form)

    # establish connect to db
    db_connection = connect_to_database()

    # check first if there is a POST request
    if request.method == 'POST':
        # retrieve data for each field from the new Orders form
        date_time = order_form.date_time.data
        sale_amount = order_form.sale_amount.data
        customer_id = order_form.customer_id.data

        # retrieve data for each field from the new Customers form
        first_name = customer_form.first_name.data
        last_name = customer_form.last_name.data
        email = customer_form.email.data
        phone_number = customer_form.phone_number.data
        location = customer_form.location.data

        # place the data in a tuple format
        order_input_data = (date_time, sale_amount, customer_id,)
        customer_input_data = (first_name, last_name, email, phone_number,)

        # query for adding a new Order into the db
        order_input_query = \
            "INSERT INTO Orders (date_time, sale_amount, customer_num) " \
            "VALUES (%s, %s, %s);"

        # query for adding a new Customer into the db
        customer_input_query = \
            "INSERT INTO Customers (first_name, last_name, email, phone_number) " \
            "VALUES (%s, %s, %s, %s);"

        # adding a new Customer also involves adding them to the Customers_Locations intersection table
        # here, we get the location_id based on the location that the user selected
        get_location_id_query = "SELECT store_id FROM `Locations` WHERE city = (%s)"
        get_location_id_results = execute_query(db_connection, get_location_id_query, (location,)).fetchall()

        # once our webpage has two forms present, we need to check which one the user is submitting
        # since the user can only submit one form at any time, the validator() method checks which
        # form has data and returns a boolean value as a result

        if validator(order_input_data) is True:
            # execute the query and commit it to the db for changes to be permanent
            execute_query(db_connection, order_input_query, order_input_data)
            db_connection.commit()

        elif validator(customer_input_data) is True:
            execute_query(db_connection, customer_input_query, customer_input_data)

            # get latest customer_id that was added (just now)
            get_customer_id_query = "SELECT customer_id FROM `Customers` ORDER BY customer_id DESC LIMIT 1"
            get_customer_id_results = execute_query(db_connection, get_customer_id_query).fetchall()

            # add the customer_id and location_id into the intersection table
            add_customer_locations = "INSERT INTO Customers_Locations (customer_fk_id, store_fk_id) VALUES (%s, %s);"
            customer_locations = (get_customer_id_results[0][0], get_location_id_results[0][0],)

            execute_query(db_connection, add_customer_locations, customer_locations)
            db_connection.commit()

        # refresh the page once the form is submitted
        return redirect(url_for('orders_customers'))

    # if the request is not POST, then it must be GET

    # queries for displaying the Orders and Customers 'overview' tables
    orders_query = \
        "SELECT date_time, customer_id, sale_amount, first_name, last_name, email, phone_number FROM `Customers` " \
        "INNER JOIN Orders ON Orders.customer_num = Customers.customer_id ORDER BY date_time;"

    customers_query = \
        "SELECT first_name, last_name, email, phone_number, city AS location FROM `Customers` " \
        "INNER JOIN Customers_Locations ON Customers_Locations.customer_fk_id = Customers.customer_id " \
        "INNER JOIN Locations ON Locations.store_id = Customers_Locations.store_fk_id ORDER BY last_name;"

    # execute the query to retrieve the table data from the db
    order_results = execute_query(db_connection, orders_query).fetchall()
    customer_results = execute_query(db_connection, customers_query).fetchall()

    # in the 'orders-customers' page, when adding a new Order, we need a dropdown menu for existing Customer ID
    # below will select all existing Customer IDs and add them to 'choices' in the dropdown menu
    customer_id_query = "SELECT customer_id FROM Customers;"
    customer_id_results = execute_query(db_connection, customer_id_query).fetchall()
    customer_id_choices = []

    for choices in customer_id_results:
        customer_id_choices.append(choices[0])

    # set the 'choices' option for customer_id for the OrderForm form
    order_form.customer_id.choices = customer_id_choices

    # same idea for the Locations dropdown menu in the new Customer form
    locations_query = "SELECT city FROM Locations;"
    location_results = execute_query(db_connection, locations_query).fetchall()
    location_choices = []

    for choices in location_results:
        location_choices.append(choices[0])

    customer_form.location.choices = location_choices

    # render the webpage with all the data retrieved from the db
    return render_template("orders_customers.html", title='Add/Edit/Delete Orders & Customers',
                           order_form=order_form, customer_form=customer_form,
                           customer_headers=customer_headers, customer_values=customer_results,
                           orders_customers_h=orders_customers_h, orders_customers_v=order_results,
                           search_customer_form=search_customer_form
                           )

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 3001))
#     app.run(port=port, debug=True)
