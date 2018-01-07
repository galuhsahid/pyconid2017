from .. import app

@app.template_filter('format_currency')
def format_currency(value):
	value = int(value)
	return "Rp{:,}".format(value).replace(",", ".")
