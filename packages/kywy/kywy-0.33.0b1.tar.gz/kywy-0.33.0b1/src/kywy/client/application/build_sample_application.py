import pandas as pd
from datetime import date
from ...client.kawa_client import KawaClient
from ...client.kawa_decorators import kawa_tool


def kawa():
    kawa = KawaClient(kawa_api_url='http://localhost:4200')
    kawa.set_api_key(api_key_file='/Users/emmanuel/doc/local-pristine/.key')
    kawa.set_active_workspace_id(workspace_id='75')
    return kawa


def profit_section(page):
    col1 = page.create_section('Profit', 1)
    col1.bar_chart(
        title='Profit and Net Profit per State',
        x='State',
        y=('Profit', 'Net Profit'),
        aggregation=('SUM', 'SUM'),
        color_offset=1,
    )


def raw_data_section(page):
    col = page.create_section('Table', 1)
    col.table('Store Data')


def kpis_section(page):
    col1, col2, col3, col4 = page.create_section('KPIs', 4)
    col1.indicator_chart('Total Profit ($)', 'Profit')
    col2.indicator_chart('Total Sales ($)', 'Sales')
    col3.indicator_chart('Total Quantity', 'Quantity')
    col4.indicator_chart('Avg Discount ($)', 'Discount', 'AVERAGE')


def trends_section(page):
    col1 = page.create_section('Trends', 1)
    col1.line_chart(
        title='Evolution of Profit and Sales ($)',
        x='Order Date',
        y=('Profit', 'Sales'),
        aggregation=('SUM', 'SUM'),
        time_sampling='YEAR_AND_MONTH',
        show_values=False,
        area=True,
        fill_in_temporal_gaps=True,
    )


def breakdowns_section(page):
    col1, col2 = page.create_section('Breakdowns', 2)
    col1.bar_chart(
        title='Shipping delay per Ship Mode (days)',
        x='Ship Mode',
        y='Shipping Delay',
        aggregation='AVERAGE',
        color='Segment',
        show_totals=True,
    )
    col2.bar_chart(
        title='Profit per Sub-Category and Ship Mode ($)',
        x='Sub-Category',
        y='Profit',
        color='Ship Mode',
        show_totals=True,
    )
    col1.bar_chart(
        title='Profit per Year and Segment ($)',
        x='Order Date',
        y='Profit',
        color='Segment',
        time_sampling='YEAR',
        show_values=True,
        show_totals=True,
    )
    col2.bar_chart(
        title='Profit per Year and Ship Mode ($)',
        x='Order Date',
        y='Profit',
        color='Ship Mode',
        time_sampling='YEAR',
        show_values=True,
        show_totals=True,
    )


def pies_section(page):
    col1, col2, col3, col4 = page.create_section('Pies', 4)
    col1.pie_chart(
        title='Quantity per Ship Mode',
        labels='Ship Mode',
        values='Quantity',
        show_values=True,
        show_labels=True,
    )
    col2.pie_chart(
        title='Quantity per Year',
        labels='Order Date',
        values='Quantity',
        show_values=True,
        show_labels=True,
        time_sampling='YEAR',
    )
    col3.pie_chart(
        title='Quantity per Segment',
        labels='Segment',
        values='Quantity',
        show_values=True,
        show_labels=True,
        doughnut=True,
    )
    col4.pie_chart(
        title='Quantity per Category',
        labels='Category',
        values='Quantity',
        show_values=True,
        show_labels=True,
        doughnut=True,
    )


def scatters_section(page):
    col1, col2 = page.create_section('Scatters', 2)

    col1.scatter_chart(
        title='Profit vs. Quantity per City',
        granularity='City',
        x='Profit',
        y='Quantity',
        color='Order ID',
        aggregation_color='COUNT'
    )

    col2.scatter_chart(
        title='Profit vs. Quantity per Customer',
        granularity='Customer Name',
        x='Profit',
        y='Quantity',
        color='Order ID',
        aggregation_color='COUNT'
    )

    col1.scatter_chart(
        title='Profit vs. Quantity per Date',
        granularity='Order Date',
        x='Profit',
        y='Quantity',
        color='Order ID',
        aggregation_color='COUNT'
    )

    col2.scatter_chart(
        title='Profit vs. Quantity per Product',
        granularity='Product Name',
        x='Profit',
        y='Quantity',
        color='Order ID',
        aggregation_color='COUNT'
    )


@kawa_tool(outputs={
    'Row ID': float,
    'Order ID': str,
    'Order Date': date,
    'Ship Date': date,
    'Ship Mode': str,
    'Customer ID': str,
    'Customer Name': str,
    'Segment': str,
    'Country': str,
    'City': str,
    'State': str,
    'Postal Code': str,
    'Region': str,
    'Product ID': str,
    'Category': str,
    'Sub-Category': str,
    'Product Name': str,
    'Sales': float,
    'Quantity': float,
    'Discount': float,
    'Profit': float,
})
def load_store_data():
    url = "https://learn.kawa.ai/readme-assets/store.csv"
    df = pd.read_csv(
        url,
        parse_dates=['Ship Date', 'Order Date'],
        date_format='%Y-%m-%d',
    )
    df['Postal Code'] = df['Postal Code'].astype('string')
    return df


@kawa_tool(outputs={
    'event id': float,
    'event date': date,
    'guest name': str,
    'event type': str,
    'event cost': float,
    'event state': str,
})
def load_events_data():
    url = "https://learn.kawa.ai/readme-assets/events.csv"
    df = pd.read_csv(
        url,
        parse_dates=['event date'],
        date_format='%Y-%m-%d',
    )
    return df


app = kawa().app(
    'Superstore App II',
    sidebar_color="#040506",
    theme='classic1'
)

app.create_ai_agent(
    name='BinaryBard',
    instructions='''
    You are an expert in data analytics. 
    Always answer with as much precision as possible.
    ''',
    color="#040506",
)

store_dataset = app.create_dataset('Store', load_store_data)
event_dataset = app.create_dataset('event', load_events_data)

model = app.create_model(store_dataset)

events_relationship = model.create_relationship(
    name='Event per Customer',
    dataset=event_dataset,
    link={'State': 'event state'},
)
events_relationship.add_column(
    name='event cost',
    aggregation='SUM',
    new_column_name='Cost per State',
)
model.create_metric(
    name='Net Profit',
    formula='SUM("Profit") - SUM("Cost per State")'
)
model.create_metric(
    name='Shipping Delay',
    prompt='How many days between ship date and order date'
)


# Add filters to the application
@kawa_tool(parameters={'state': {'type': str, 'binding': 'State'}})
def value_loader(state):
    print(f'Figuring out the list of Segments for {state}')
    return ['Consumer','Corporate', 'Home Office']


app.create_text_filter('State')
app.create_text_filter('Segment', value_loader=value_loader)

# Build Order Analytics page
orders_page = app.create_page('Orders Analytics')
kpis_section(orders_page)
scatters_section(orders_page)
trends_section(orders_page)
pies_section(orders_page)
breakdowns_section(orders_page)
raw_data_section(orders_page)
profit_section(orders_page)

app.publish()
