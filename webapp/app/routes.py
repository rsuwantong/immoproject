from flask import render_template, redirect, url_for
from webapp.app import app
from webapp.app.forms import ComputeFeeForm
@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Rata'}
    posts = [
        {
            'author': {'username': 'We'},
            'body': 'Find the best agency fee for your property'
        },
        {
            'author': {'username': 'We'},
            'body': 'Estimate the price of your property'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/compute_fee', methods=['GET', 'POST'])
def compute_fee():
    form = ComputeFeeForm()
    if form.validate_on_submit():
        return redirect(url_for('list_agencies'))
    return render_template('compute_fee.html', title="Calcul le frais d'agence", form=form)

@app.route('/list_agencies')
def list_agencies():
    user = {'username': 'Rata'}
    agencies = [
        {
            'properties': {'name': 'Agency A', 'address': "Agency A's address"},
            'fee': 10000
        },
        {
            'properties': {'name': 'Agency B', 'address': "Agency B's address"},
            'fee': 20000
        },
    ]
    return render_template('list_agencies.html', title='Agency fees', user=user, agencies=agencies)