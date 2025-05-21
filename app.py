import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
DATA_PATH = 'data/large_covid_data.csv'
PLOTS_DIR = 'static/plots'
os.makedirs(PLOTS_DIR, exist_ok=True)

def save_plot(fig, filename):
    filepath = os.path.join(PLOTS_DIR, filename)
    fig.savefig(filepath, bbox_inches='tight')
    plt.close(fig)
    return '/' + filepath.replace('\\', '/')

@app.route('/')
def dashboard():
    df = pd.read_csv(DATA_PATH)
    df['Active'] = df['Confirmed'] - df['Deaths'] - df['Recovered']
    country_list = sorted(df['Country'].unique())
    selected_country = request.args.get('country')

    if selected_country and selected_country in country_list:
        df_country = df[df['Country'] == selected_country]
    else:
        df_country = df

    latest = df_country.groupby('Country').agg({
        'Confirmed': 'sum',
        'Deaths': 'sum',
        'Recovered': 'sum',
        'Active': 'sum'
    }).reset_index()

    total_confirmed = latest['Confirmed'].sum()
    total_deaths = latest['Deaths'].sum()
    total_recovered = latest['Recovered'].sum()

    def line_plot(data, column, title):
        fig, ax = plt.subplots(figsize=(6,4))
        data.groupby('Date')[column].sum().plot(ax=ax)
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel(column)
        return fig

    def bar_plot(data):
        fig, ax = plt.subplots(figsize=(6,4))
        data.plot.bar(x='Country', y='Confirmed', ax=ax, color='orange')
        ax.set_title('Confirmed Cases by Country')
        ax.set_ylabel('Confirmed')
        ax.set_xlabel('Country')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return fig

    def pie_plot(data):
        fig, ax = plt.subplots(figsize=(6,6))
        ax.pie(data['Active'], labels=data['Country'], autopct='%1.1f%%', startangle=140)
        ax.set_title('Active Cases Distribution')
        return fig

    plots = {
        'confirmed': save_plot(line_plot(df_country, 'Confirmed', 'Confirmed Cases Over Time'), 'confirmed.png'),
        'deaths': save_plot(line_plot(df_country, 'Deaths', 'Deaths Over Time'), 'deaths.png'),
        'recovered': save_plot(line_plot(df_country, 'Recovered', 'Recovered Over Time'), 'recovered.png'),
        'active': save_plot(line_plot(df_country, 'Active', 'Active Cases Over Time'), 'active.png'),
        'bar': save_plot(bar_plot(latest), 'bar.png'),
        'pie': save_plot(pie_plot(latest), 'pie.png'),
    }

    return render_template(
        'index.html',  # your html file name
        country_list=country_list,
        selected_country=selected_country,
        total_confirmed=total_confirmed,
        total_deaths=total_deaths,
        total_recovered=total_recovered,
        plots=plots,
        countries=latest.to_dict(orient='records')
    )

if __name__ == '__main__':
    app.run(debug=True)
