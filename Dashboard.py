import os
import re

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine


def fetch_data_from_postgresql(connection_url: str, query: str) -> pd.DataFrame:
	"""Fetch data from PostgreSQL using the provided SQL query."""
	engine = create_engine(connection_url)
	try:
		return pd.read_sql_query(query, engine)
	finally:
		engine.dispose()


def _validate_identifier(identifier: str) -> bool:
	"""Allow only SQL identifiers like schema.table or column_name."""
	pattern = r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$"
	return bool(re.match(pattern, identifier))


def _quote_identifier(identifier: str) -> str:
	"""Quote dot-separated SQL identifiers safely."""
	return ".".join(f'"{part}"' for part in identifier.split("."))


def _build_connection_url(
	host: str,
	port: int,
	database: str,
	username: str,
	password: str,
) -> str:
	return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"


def main() -> None:
	st.set_page_config(page_title="PostgreSQL Bar Chart Dashboard", layout="wide")
	st.title("PostgreSQL Dashboard - 4 Bar Charts")

	st.sidebar.header("PostgreSQL Connection")
	host = st.sidebar.text_input("Host", value=os.getenv("PGHOST", "localhost"))
	port = st.sidebar.number_input(
		"Port",
		min_value=1,
		max_value=65535,
		value=int(os.getenv("PGPORT", "5432")),
	)
	database = st.sidebar.text_input("Database", value=os.getenv("PGDATABASE", "postgres"))
	username = st.sidebar.text_input("Username", value=os.getenv("PGUSER", "postgres"))
	password = st.sidebar.text_input("Password", value=os.getenv("PGPASSWORD", ""), type="password")

	st.sidebar.header("Dataset")
	table_name = st.sidebar.text_input("Table (schema.table)", value="public.sales")
	category_column = st.sidebar.text_input("Category Column", value="category")
	value_column = st.sidebar.text_input("Value Column (numeric)", value="amount")
	top_n = st.sidebar.slider("Top N", min_value=5, max_value=30, value=10)

	load_data = st.sidebar.button("Load Data")

	st.caption(
		"Set PostgreSQL connection details and table/column names, then click 'Load Data'"
	)

	if not load_data:
		return

	if not all([host, database, username, table_name, category_column, value_column]):
		st.error("Please complete all required fields.")
		return

	identifiers = [table_name, category_column, value_column]
	if not all(_validate_identifier(item) for item in identifiers):
		st.error("Invalid table/column names. Use only letters, numbers, underscores, and optional schema prefixes.")
		return

	quoted_table = _quote_identifier(table_name)
	quoted_category = _quote_identifier(category_column)
	quoted_value = _quote_identifier(value_column)

	query = f"""
		SELECT {quoted_category} AS category, {quoted_value} AS value
		FROM {quoted_table}
		WHERE {quoted_category} IS NOT NULL AND {quoted_value} IS NOT NULL
	"""

	connection_url = _build_connection_url(host, int(port), database, username, password)

	try:
		data = fetch_data_from_postgresql(connection_url, query)
	except Exception as exc:
		st.error(f"Failed to load data from PostgreSQL: {exc}")
		return

	if data.empty:
		st.warning("No data found for the selected table/columns.")
		return

	data["value"] = pd.to_numeric(data["value"], errors="coerce")
	data = data.dropna(subset=["value", "category"])

	if data.empty:
		st.warning("No numeric values found in the selected value column.")
		return

	sum_df = (
		data.groupby("category", as_index=False)["value"]
		.sum()
		.sort_values("value", ascending=False)
		.head(top_n)
	)
	avg_df = (
		data.groupby("category", as_index=False)["value"]
		.mean()
		.sort_values("value", ascending=False)
		.head(top_n)
	)
	count_df = (
		data.groupby("category", as_index=False)["value"]
		.count()
		.rename(columns={"value": "count"})
		.sort_values("count", ascending=False)
		.head(top_n)
	)
	min_df = (
		data.groupby("category", as_index=False)["value"]
		.min()
		.sort_values("value", ascending=False)
		.head(top_n)
	)

	st.subheader("Data Preview")
	st.dataframe(data.head(100), use_container_width=True)

	col1, col2 = st.columns(2)
	with col1:
		fig1 = px.bar(
			sum_df,
			x="category",
			y="value",
			title="Chart 1: Total Value by Category",
		)
		st.plotly_chart(fig1, use_container_width=True)

	with col2:
		fig2 = px.bar(
			avg_df,
			x="category",
			y="value",
			title="Chart 2: Average Value by Category",
		)
		st.plotly_chart(fig2, use_container_width=True)

	col3, col4 = st.columns(2)
	with col3:
		fig3 = px.bar(
			count_df,
			x="category",
			y="count",
			title="Chart 3: Record Count by Category",
		)
		st.plotly_chart(fig3, use_container_width=True)

	with col4:
		fig4 = px.bar(
			min_df,
			x="category",
			y="value",
			title="Chart 4: Minimum Value by Category",
		)
		st.plotly_chart(fig4, use_container_width=True)


if __name__ == "__main__":
	main()
