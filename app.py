from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os, json, csv
import datetime

#Spacy
from spacy import displacy

app = Flask(__name__)
with open('config.json') as config_file:
    json_file = json.load(config_file)
    app.secret_key = json_file['secret_key']
    reviews_file_path = json_file['reviews_file_path']

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login view for redirection

# User model
class User(UserMixin):
    def __init__(self, user_id, password, start, end, current):
        self.id = user_id
        self.password = password
        self.start = start
        self.end = end
        self.current = current

    @classmethod
    def get(cls, user_id):
        # Replace this with your own logic to retrieve user from database
        with open('users.json') as users_file:
            users = json.load(users_file)

            for user in users:
                if user_id == user['id']:
                    return User(user['id'], user['password'], user['start'], user['end'], user['current'])
        
        return None

    def verify_password(self, password):
        # Replace this with your own password verification logic
        return password == self.password
    
    def inc_current(self):
        self.current += 1
        with open('users.json') as users_file:
            users = json.load(users_file)

        for user in users:
            if user['id'] == self.id:
                user['current'] = self.current

        with open('users.json', 'w') as json_file:
            json.dump(users, json_file, indent=4)

# User login function
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        form_responses = request.form.to_dict()

        next_button = request.form.get('next')
        #previous_button = request.form.get('previous')

        if next_button is not None and (not form_responses or len(form_responses)-2 != len(session['reviews'][current_user.current]['features'])):
            return render_template('index.html', app=session['reviews'][current_user.current]['app_name'], package=session['reviews'][current_user.current]['package_name'], review=session['reviews'][current_user.current]['review'], features=session['reviews'][current_user.current]['features'], error_message='Please select an option for each extracted feature.', count = current_user.current, total = current_user.end - current_user.start)

        #handle_form_submission(form_responses, next_button, previous_button)
        handle_form_submission(form_responses, next_button)

    if current_user.current < len(session['reviews']):
        return render_template('index.html', app=session['reviews'][current_user.current]['app_name'], package=session['reviews'][current_user.current]['package_name'], review=session['reviews'][current_user.current]['review'], features=session['reviews'][current_user.current]['features'], count = current_user.current, total = current_user.end - current_user.start)
    else:
        return render_template('end.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global clicked_buttons, reviews

    error_message = ""

    if request.method == 'POST':

        # At log in we load the reviews, not before
        with open(reviews_file_path, 'r', newline='\n', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')

            reviews = []

            for row in csv_reader:
                reviews.append({'app_name': row[0], 'package_name': row[1], 'review': row[2], 'features': row[3].split(', ')})

        clicked_buttons = [None]*len(reviews[0]['features'])


        # Then we process the user

        user_id = request.form.get('user_id')
        password = request.form.get('password')
        user = User.get(user_id)
        if user and user.verify_password(password):
            session['reviews'] = reviews[user.start:user.end]
            clicked_buttons = [None]*len(session['reviews'][0]['features'])
            login_user(user)
            return redirect(url_for('index'))

        # Invalid credentials, show error message
        error_message = 'Invalid username or password'

    #else:   
    #    error_message = 'Unexpected error'

    return render_template('login.html', error_message=error_message)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#def handle_form_submission(form_responses, next_button, previous_button):
def handle_form_submission(form_responses, next_button):

    # Confirmed features
    session['reviews'][current_user.current]['evaluated_features'] = []
    for key in form_responses:
        if 'feature-' in key:
            index = int(key.split('-')[1])-1
            if form_responses[key] == 'confirm':
                session['reviews'][current_user.current]['evaluated_features'].append(session['reviews'][current_user.current]['features'][index])

    # New features
    new_features = form_responses['new-features'].split(os.linesep)
    if len(new_features) > 0 and new_features[0] != "":
        session['reviews'][current_user.current]['evaluated_features'].extend(new_features)

    # Save current answers
    # Define the JSON file path
    json_file_path = 'data/responses/responses-' + current_user.id + '.json'

    # Check if the JSON file exists
    if os.path.exists(json_file_path):
        # If the file exists, load the existing JSON data
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
    else:
        # If the file doesn't exist, initialize an empty list
        data = []

    # Append the new array to the existing data
    data.append(session['reviews'][current_user.current])

    # Save the updated data back to the JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    if next_button is not None:
        current_user.inc_current()

if __name__ == '__main__':
    app.run(debug=True)