from flask_sqlalchemy import SQLAlchemy
import json


db = SQLAlchemy()


class TableValues(db.Model):
    key = db.Column(db.String, primary_key=True)
    value = db.Column(db.String, nullable=False)


def populate_table_with_json_data(json_data):
    with open(json_data, 'r') as file:
        json_data = json.load(file)


    for key, value in json_data.items():
        table_entry = TableValues(key=key, value=value)
        db.session.add(table_entry)
    db.session.commit()

def write_table_to_json_file(file_path):
    # Query the table to retrieve all rows
    table_rows = TableValues.query.all()

    # Create a dictionary to store the values
    values_dict = {}

    # Iterate over the table rows and populate the dictionary
    for row in table_rows:
        values_dict[row.key] = row.value

    # Write the dictionary to the JSON file
    with open(file_path, 'w') as file:
        json.dump(values_dict, file)