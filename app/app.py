import streamlit as st
import pandas as pd
import statsmodels.api as sm
import plotly.express as px

def load_css():
	file_name = ".streamlit/style.css"
	with open(file_name) as file:
		styles = file.read()
		st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)

def load_fama_french_5_factor_rets():
	df = pd.read_csv("data/fama_french_5_factor_rets.csv", header=0, index_col=0)
	df.index = pd.to_datetime(df.index)
	df.index = df.index.to_period('M')
	return df
	
def load_yahoo_rets(series_rf):
	df = pd.read_csv("data/yahoo_rets.csv", header=0, index_col=0)
	df.subtract(series_rf, axis=0)
	df.index = pd.to_datetime(df.index)
	df.index = df.index.to_period('M')
	return df

def regress(dependent_variable, explanatory_variables):
	# Create safe copies
	explanatory_variables = explanatory_variables.copy()
	dependent_variable = dependent_variable.copy()

	# Add Alpha scalar
	explanatory_variables.insert(0, "Alpha", 1)

	# Drop any na rows
	dependent_variable.dropna(inplace=True)
	mask = dependent_variable.index
	explanatory_variables = explanatory_variables.loc[mask]
	
	# Run model
	lm = sm.OLS(dependent_variable, explanatory_variables).fit()
	return lm

def draw_factors_graph(df, container):
	chart_container = container.container()

	# Year Selector
	min = int(df.index.year.min())
	max = int(df.index.year.max())
	selected_years = container.slider(label="Select Years", min_value=min, max_value=max, value=(min, max), key="5FG")
	
	mask = (df.index.year >= selected_years[0]) & (df.index.year <= selected_years[1])
	df = df.loc[mask]

	# Create Chart
	df.index = df.index.map(str)
	fig = px.line(df, x=df.index, y=df.columns, color_discrete_sequence=px.colors.qualitative.Antique)
	fig.layout.yaxis.tickformat = ".1%"
	fig.update_layout(
		title="Factor Returns vs Time",
		title_x=0.5,
		legend_title_text="Factor",
		xaxis_title="Date",
		yaxis_title="Monthly Returns"
	)

	# Draw Chart & Return
	chart_container.plotly_chart(fig, use_container_width=True)

def draw_stock_graph(df, stock, container):
	chart_container = container.container()

	# Year Selector
	min = int(df.index.year.min())
	max = int(df.index.year.max())
	selected_years = container.slider(label="Select Years", min_value=min, max_value=max, value=(min, max), key="SG")
	
	mask = (df.index.year >= selected_years[0]) & (df.index.year <= selected_years[1])
	df = df.loc[mask]

	# Create Chart
	df.index = df.index.map(str)
	fig = px.line(df, x=df.index, y=df[stock], color_discrete_sequence=px.colors.qualitative.Antique)
	fig.layout.yaxis.tickformat = ".1%"
	fig.update_layout(
		title=f"{stock} Returns vs Time",
		title_x=0.5,
		legend_title_text="Stock",
		xaxis_title="Date",
		yaxis_title="Monthly Returns"
	)

	# Draw Chart & Return
	chart_container.plotly_chart(fig, use_container_width=True)

def main():
	# Init
	st.set_page_config(layout="wide")
	load_css()

	# Load data
	df_fama_french = load_fama_french_5_factor_rets()
	df_yahoo = load_yahoo_rets(df_fama_french["RF"])

	# Header
	st.markdown("<h1 style='text-align: center;'>Fama-French 5 Factor Model</h1>", unsafe_allow_html=True)
	fama_french_5_factor_equation = """
		<div style="text-align: center;font-size: 20px;font-family: math;">
        	R<sub>it</sub> — RF<sub>t</sub> = &alpha;<sub>i</sub> + &beta;<sub>i</sub>(RM<sub>t</sub> — RF<sub>t</sub>) + s<sub>i</sub>SMB<sub>t</sub> + h<sub>i</sub>HML<sub>t</sub> + r<sub>i</sub>RMW<sub>t</sub> + c<sub>i</sub>CMA<sub>t</sub>
		</div>
        """
	st.markdown(fama_french_5_factor_equation, unsafe_allow_html=True)

	# User input
	min_value = -20.0
	max_value = 20.0
	step = 0.1

	container_model = st.container()
	cols_top_model = container_model.columns(3)
	container_result = cols_top_model[1].container()

	selected_stock = cols_top_model[1].selectbox("Please select a stock for price prediction", df_yahoo.columns)
	Mkt_minus_RF = container_model.slider("Mkt-RF (Market)", min_value=min_value, max_value=max_value, value=0.0, step=step, format="%.1f%%")

	cols = container_model.columns(2)
	SMB = cols[0].slider("SMB (Size)", min_value=min_value, max_value=max_value, value=0.0, step=step, format="%.1f%%")
	RMW = cols[0].slider("RMW (Profitability)", min_value=min_value, max_value=max_value, value=0.0, step=step, format="%.1f%%")
	HML = cols[1].slider("HML (Value)", min_value=min_value, max_value=max_value, value=0.0, step=step, format="%.1f%%")
	CMA = cols[1].slider("CMA (Investment)", min_value=min_value, max_value=max_value, value=0.0, step=step, format="%.1f%%")

	Mkt_minus_RF /= 100
	SMB /= 100
	RMW /= 100
	HML /= 100
	CMA /= 100

	# Run model
	factors = ["Mkt-RF", "SMB", "HML", "RMW", "CMA"]
	results = regress(df_yahoo[selected_stock], df_fama_french.loc[:,factors]).params
	ret_minus_rf = results["Alpha"] + (results["Mkt-RF"]*Mkt_minus_RF) + (results["SMB"]*SMB) + (results["HML"]*HML) + (results["RMW"]*RMW) + (results["CMA"]*CMA)

	# Display results
	ret_minus_rf = round(ret_minus_rf*100, 1)
	ret_minus_rf += 0 # Convert -0.0 to 0.0
	
	border_colour = "green"
	if ret_minus_rf < 0: border_colour = "red"

	result_text = f"""
		<p style="border: 3px solid {border_colour};text-align: center;font-size: 20px;font-family: math;">
			R<sub>it</sub> — RF<sub>t</sub> = {ret_minus_rf}%
		</p>
	"""
	container_result.markdown(result_text, unsafe_allow_html=True)

	# Draw graphs
	cols = st.columns(2)
	draw_factors_graph(df_fama_french, cols[0])
	draw_stock_graph(df_yahoo, selected_stock, cols[1])

if __name__ == "__main__":
	main()