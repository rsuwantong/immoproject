from flask import render_template, redirect, url_for
from webapp.app import app
from webapp.app.forms import ComputeFeeForm
import pandas as pd
from sqlalchemy import create_engine

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
        #TODO: Compute for other postal codes, too and show in the list if the agency is not too far from the property
        postal_code = form.postal_code.data
        price_keuros = form.price.data/1e3
        breakpoint()
        engine = create_engine('postgresql://postgres:Bohr7411@localhost:5432/immoguru')
        agency_fees = pd.read_sql_query('select * from "agency_fees"', con=engine)
        agency_fees["price_max_keuros"] = agency_fees["price_max_keuros"].fillna(1e9)
        agency_fees_relevant = agency_fees[(agency_fees.postal_code==postal_code) & (agency_fees.price_min_keuros<= price_keuros) & (agency_fees.price_max_keuros> price_keuros)]
        agency_fees_relevant["agency_fee_keuros"] = price_keuros*agency_fees_relevant["agency_rate"]
        agency_fees_relevant["agency_fee_keuros"] = agency_fees_relevant["agency_fee_keuros"].fillna(agency_fees_relevant["agency_fee_min_keuros"])
        agency_fees_relevant["agency_fee_final"] = agency_fees_relevant["agency_fee_keuros"]*1000
        agency_fees_list = agency_fees_relevant[["agency_code", "agency_name", "agency_address", "postal_code", "agency_fee_final"]]
        return redirect(url_for('list_agencies'), agency_fees_list=agency_fees_list, price=form.price.data, address=form.address.data)
    return render_template('compute_fee.html', title="Calcul le frais d'agence", form=form)

@app.route('/list_agencies')
def list_agencies(agency_fees_list, price, address):
    user_property = {"price": price,
                "address": address}
    agency_fees_list.sort_values(by="agency_fee_final",inplace=True)
    agencies = [{'agency_name': x,
            'agency_address': y,
            'agency_fee': z} for x, y, z in zip(agency_fees_list["agency_name"],agency_fees_list["agency_address"],agency_fees_list["agency_fee"] )]

    return render_template('list_agencies.html', title='Agency fees', agencies=agencies, user_property=user_property)