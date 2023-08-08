from flask import Flask, render_template, redirect, url_for, request
import json
import os
from flask_httpauth import HTTPBasicAuth
import datetime
from database import db, populate_table_with_json_data, TableValues, write_table_to_json_file, clear_table_content
import urllib.parse

# Load environment variables from .env file
# load_dotenv('.env')

# ADMIN_USERNAME = os.environ["ADMIN_NAME"]
# ADMIN_PASSWORD = os.environ["UPDATE_PASS"]
# mail_pass = os.environ["PASS_MAIL"]
# middle_email = os.environ["MIDDL_MAIL"]
# to_adr = os.environ["TO_ADDR"]
# mail_pass = os.getenv("PASS_MAIL")
# middle_email = os.getenv("MIDDL_MAIL")
# to_adr = os.getenv("TO_ADDR")
# mail_pass = os.getenv("PASS_MAIL")
# middle_email = os.getenv("MIDDL_MAIL")
# to_adr = os.getenv("TO_ADDR")
# app.secret_key = os.environ['SCRT_KEY']
# Retrieve the last_update variable from the session
# last_update = session.get('last_update')

# name = request.form['name']
# email = request.form['email']
# message = request.form['message']


# msg = Message(name, email = middle_email, recipients = to_adr)
# msg.body = message
# mail.send(msg)
# Create the email message
# connection = smtplib.SMTP('smtp.gmail.com')
# connection.starttls()
# connection.login(user=middle_email, password=mail_pass)


# try:
# message_body = f"Name: {name}\nEmail: {email}\n\n{message}"
# connection.sendmail(from_addr=middle_email, to_addrs=to_adr,
# msg=message_body)
# return render_template('index.html', values=table_values, last_update=last_update)
# except Exception as e:
# print(str(e))
# return 'An error occurred while sending the message.'

# Update the session variable with the formatted datetime
# session['last_update'] = formatted_datetime

# @app.route('/offer')
# def offer():
#    return render_template('offer.html')


app = Flask(__name__)
db_uri = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db.init_app(app)

with app.app_context():
    db.create_all()
    populate_table_with_json_data('table_values.json')
    write_table_to_json_file('output.json')
    VALUES_FILE_PATH = 'output.json'

ADMIN_USERNAME = os.getenv("ADMIN_NAME")
ADMIN_PASSWORD = os.getenv("UPDATE_PASS")

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
        'eur_buy': "X",
        'eur_sell': "X",
        'usd_buy': "X",
        'usd_sell': "X",
        'gbp_buy': "X",
        'gbp_sell': "X",
        'chf_buy': "X",
        'chf_sell': "X",
        'huf_buy': "X",
        'huf_sell': "X",
        'sek_buy': "X",
        'sek_sell': "X",
        'dkk_buy': "X",
        'dkk_sell': "X",
        'nok_buy': "X",
        'nok_sell': "X",
        'cad_buy': "X",
        'cad_sell': "X",
        'aud_buy': "X",
        'aud_sell': "X",
        'bgn_buy': "X",
        'bgn_sell': "X",
        'pln_buy': "X",
        'pln_sell': "X",
        'czk_buy': "X",
        'czk_sell': "X",
        'try_buy': "X",
        'try_sell': "X",
        'rsd_buy': "X",
        'rsd_sell': "X",
        'uah_buy': "X",
        'uah_sell': "X",
        'mdl_buy': "X",
        'mdl_sell': "X",
        'rub_buy': "X",
        'rub_sell': "X",
        'aed_buy': "X",
        'aed_sell': "X",
        'ils_buy': "X",
        'ils_sell': "X"
    }

LAST_UPDATE_FILE_PATH = "last_update.json"

app.secret_key = os.getenv('SCRT_KEY')


@app.route('/', methods=["GET", "POST"])
def home():
    # Read the last update timestamp from the file
    if os.path.exists(LAST_UPDATE_FILE_PATH):
        with open(LAST_UPDATE_FILE_PATH, 'r') as file:
            last_update_data = json.load(file)
            last_update = last_update_data.get('last_update')
    else:
        last_update = None

    if request.method == 'POST':
        email_message = request.form.get('message')
        email_address = "lhunor@protonmail.com"
        email_subject = request.form.get('subject')

        # Properly encode parameters using urllib.parse
        encoded_email_message = urllib.parse.quote(email_message)
        encoded_email_subject = urllib.parse.quote(email_subject)

        mailto_link = f"mailto:{email_address}?subject={encoded_email_subject}&body={encoded_email_message}"
        return redirect(mailto_link)

    return render_template('index.html', values=table_values, last_update=last_update)


@app.route('/submit', methods=['POST'])
def submit():
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
