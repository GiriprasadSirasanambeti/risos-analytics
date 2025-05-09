import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')  #set the backend to Agg (non-GUI)
import matplotlib.pyplot as plt
import os
import shutil
import tempfile
from flask import Flask, render_template

app = Flask(__name__)

#Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'risos.db')
CHART_PATH = os.path.join(BASE_DIR, 'static', 'sales_chart.png')

def analyze_sales():
    """Analyze sales data and generate a bar chart."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT product_id, qty, timestamp FROM sales", conn)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        total_sales = df.groupby('product_id')['qty'].sum()

        # Generate bar chart in a temporary file
        plt.figure()
        total_sales.plot(kind='bar', title="Sales by Product")
        plt.xlabel("Product ID")
        plt.ylabel("Units Sold")
        temp_file = os.path.join(tempfile.gettempdir(), "sales_chart.png")
        plt.savefig(temp_file)
        plt.close()

        # Ensure the static directory exists and move the file
        os.makedirs(os.path.dirname(CHART_PATH), exist_ok=True)
        shutil.move(temp_file, CHART_PATH)

        conn.close()
        return total_sales.to_dict()    # Return as dict for rendering
    except Exception as e:
        print(f"Error Generating chart: {e}")
        if 'conn' in locals():
            conn.close()
        return None

@app.route('/')
def index():
    """Render the homepage with sales analysis."""
    total_sales = analyze_sales()
    if total_sales is None:
        return "Error analyzing sales data", 500
    return render_template('index.html', total_sales=total_sales)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5001)),debug=False)