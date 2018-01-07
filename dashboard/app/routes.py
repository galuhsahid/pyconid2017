from app import app
from flask.json import jsonify
import json
from flask import request, render_template
import pandas as pd

from predict import get_prediction
from data import get_data
from graph import display_fb_shares

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/details')
def details():
	# 1. Get the campaign link
	# 2. Collect the data based on the given link
	# 3. Predict the donation
	# 4. Display the graph, result, stats, etc.

	campaign = request.args.get('campaign', None)
	response = get_data(campaign)
	data = json.loads(response)

	# Remove collected_amt from our data
	# because we don't need it for the model
	df_input = pd.DataFrame([data]).drop(['collected_amt'], axis=1)
	prediction = get_prediction(df_input)

	data['campaign'] = campaign
	data['prediction'] = prediction

	# Add is funded
	if (int(data['prediction']) < int(data['donation_target_amt']) ):
		data['is_funded'] = False
	else:
		data['is_funded'] = True

	# Get graph
	target = int(data['donation_target_amt'])
	fb_shares = display_fb_shares(target)

	return render_template('details.html',
						campaign=campaign,
						data=data,
						fb_shares=fb_shares
						)
			