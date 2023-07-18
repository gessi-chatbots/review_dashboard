from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os, json

#Spacy
from spacy import displacy

app = Flask(__name__)
with open('config.json') as config_file:
    app.secret_key = json.load(config_file)['secret_key']

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login view for redirection

# User model
class User(UserMixin):
    def __init__(self, user_id, password):
        self.id = user_id
        self.password = password

    @classmethod
    def get(cls, user_id):
        # Replace this with your own logic to retrieve user from database
        with open('users.json') as users_file:
            users = json.load(users_file)

            if user_id in users:
                return User(user_id, users[user_id])
        
        return None

    def verify_password(self, password):
        # Replace this with your own password verification logic
        return password == self.password

# User login function
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Sample data for the table rows
reviews = ["Best running tracker out there",
           "It has a flexible session timer",
           "Call rings but nothing happens",
           "Best habit tracker out there!",
           "I also have some checklists for various tasks"
           ]

features = [["running","tracker"],
            ["timer"],
            ["call"],
            ["habit tracker"],
            ["checklists"]
            ]

count = 0
clicked_buttons = [None]*len(features[0])

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        form_responses = request.form.to_dict()

        next_button = request.form.get('next')
        previous_button = request.form.get('previous')

        if next_button is not None and (not form_responses or len(form_responses)-2 != len(features[count])):
            return render_template('index.html', review=reviews[count], features=features[count],error_message='Please select an option for each extracted feature.', count = count)

        handle_form_submission(form_responses, next_button, previous_button)

    if count < len(reviews):
        return render_template('index.html', review=reviews[count], features=features[count], count = count)
    else:
        return render_template('end.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global count, clicked_buttons
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        user = User.get(user_id)
        if user and user.verify_password(password):
            login_user(user)
            count = 0
            clicked_buttons = [None]*len(features[0])
            return redirect(url_for('index'))

        # Invalid credentials, show error message
        error_message = 'Invalid username or password'

    else:   
        error_message = 'Unexpected error'

    return render_template('login.html', error_message=error_message)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def handle_form_submission(form_responses, next_button, previous_button):
    global count

    # New features
    new_features = form_responses['new-features'].split(os.linesep)

    # Extracted features marked as confirmed are true positives
    #TODO 

    # Extracted features marked as rejected are false positives
    #TODO

    # New features not extracted are false negatives
    fn = len(new_features)

    print(form_responses)
    session[str(count)] = {'extracted_features': {}, 'new_features': form_responses['new-features']}
    #TODO extracted features mapping
    for key in form_responses:
        if 'feature-' in key:
            session[str(count)]['extracted_features'][key] = form_responses[key]
    print(session[str(count)])

    if next_button is not None:
        count += 1
    elif previous_button is not None:
        count -= 1

if __name__ == '__main__':
    app.run(debug=True)