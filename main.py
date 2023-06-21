from flask import Flask, render_template, redirect, url_for, request, session
import json
import os
from flask_httpauth import HTTPBasicAuth
import datetime
import smtplib
from database import db, populate_table_with_json_data, TableValues, write_table_to_json_file, clear_table_content
from sqlalchemy import inspect

# Load environment variables from .env file
#load_dotenv('.env')

app = Flask(__name__)
db_uri = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db.init_app(app)

with app.app_context():
    #db.create_all()
    #populate_table_with_json_data('table_values.json')
    write_table_to_json_file('output.json')
    VALUES_FILE_PATH = 'output.json'


#ADMIN_USERNAME = os.environ["ADMIN_NAME"]
#ADMIN_PASSWORD = os.environ["UPDATE_PASS"]
#mail_pass = os.environ["PASS_MAIL"]
#middle_email = os.environ["MIDDL_MAIL"]
#to_adr = os.environ["TO_ADDR"]

ADMIN_USERNAME = os.getenv("ADMIN_NAME")
ADMIN_PASSWORD = os.getenv("UPDATE_PASS")
mail_pass = os.getenv("PASS_MAIL")
middle_email = os.getenv("MIDDL_MAIL")
to_adr = os.getenv("TO_ADDR")

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True
    return False


# Check if the values file exists
if os.path.exists(VALUES_FILE_PATH):
    # Read the values from the file
    with open(VALUES_FILE_PATH, 'r') as file:
        table_values = json.load(file)
else:
    # If the file doesn't exist, use the initial values
    table_values = {
        'eur_buy': "4.94",
        'eur_sell': "4.97",
        'usd_buy': "4.50",
        'usd_sell': "4.66",
        'gbp_buy': "5.60",
        'gbp_sell': "5.70",
        'chf_buy': "5.00",
        'chf_sell': "5.20",
        'huf_buy': "1.30",
        'huf_sell': "1.34",
        'sek_buy': "0.415",
        'sek_sell': "0.442",
        'dkk_buy': "0.50",
        'dkk_sell': "0.61",
        'nok_buy': "0.402",
        'nok_sell': "0.433",
        'cad_buy': "4.50",
        'cad_sell': "4.66",
        'aud_buy': "2.93",
        'aud_sell': "3.13",
        'bgn_buy': "2.45",
        'bgn_sell': "2.69",
        'pln_buy': "1.06",
        'pln_sell': "1.18",
        'czk_buy': "0.202",
        'czk_sell': "0.216",
        'try_buy': "0.23",
        'try_sell': "0.293",
        'rsd_buy': "0.04",
        'rsd_sell': "0.0489",
        'uah_buy': "0.05",
        'uah_sell': "0.15",
        'mdl_buy': "0.21",
        'mdl_sell': "0.25",
        'rub_buy': "0.045",
        'rub_sell': "0.075",
        'aed_buy': "1.20",
        'aed_sell': "1.50",
        'ils_buy': "1.20",
        'ils_sell': "1.48"
    }

LAST_UPDATE_FILE_PATH = "last_update.json"


#app.secret_key = os.environ['SCRT_KEY']
app.secret_key = os.getenv('SCRT_KEY')

@app.route('/', methods=["GET", "POST"])
def home():
    # Retrieve the last_update variable from the session
    #last_update = session.get('last_update')

    # Read the last update timestamp from the file
    if os.path.exists(LAST_UPDATE_FILE_PATH):
        with open(LAST_UPDATE_FILE_PATH, 'r') as file:
            last_update_data = json.load(file)
            last_update = last_update_data.get('last_update')
    else:
        last_update = None

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Create the email message
        connection = smtplib.SMTP('smtp.gmail.com')
        connection.starttls()
        connection.login(user=middle_email, password=mail_pass)


        try:
            message_body = f"Name: {name}\nEmail: {email}\n\n{message}"
            connection.sendmail(from_addr=middle_email, to_addrs=to_adr,
                                msg=message_body)
            return render_template('index.html', values=table_values, last_update=last_update)
        except Exception as e:
            print(str(e))
            return 'An error occurred while sending the message.'

    return render_template('index.html', values=table_values, last_update=last_update)


@app.route('/offer')
def offer():
    return render_template('offer.html')


@app.route('/submit', methods=['POST'])
def submit():
    # Process form data here if needed
    return redirect(url_for('index'))


@app.route('/update', methods=['GET', 'POST'])
@auth.login_required
def update():
    if request.method == 'POST':
        # Get the current date and time
        current_datetime = datetime.datetime.now()

        # Add 3 hours to the current datetime
        current_datetime = current_datetime + datetime.timedelta(hours=3)

        # Format the date and time as desired (hh:mm dd.mm.yyyy)
        formatted_datetime = current_datetime.strftime('%H:%M %d.%m.%Y')

        # Iterate over the keys in table_values and update their values from the form data
        for key in table_values.keys():
            table_values[key] = request.form.get(key)

        # Write the updated values to the file
        with open(VALUES_FILE_PATH, 'w') as file:
            json.dump(table_values, file)

        # Clear the table
        clear_table_content()

        # Repopulate the table with the updated 'output.json' file
        populate_table_with_json_data('output.json')

        # Update the session variable with the formatted datetime
        #session['last_update'] = formatted_datetime

        # Write the last update timestamp to the file
        last_update_data = {'last_update': formatted_datetime}
        with open(LAST_UPDATE_FILE_PATH, 'w') as file:
            json.dump(last_update_data, file)

        # Redirect back to the index page
        return redirect('/')

    # Pass the current table_values to the update.html template
    return render_template('update.html', values=table_values)

@auth.error_handler
def unauthorized():
    return auth.authenticate_header()


if __name__ == '__main__':
    app.run()
