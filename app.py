from flask import Flask, render_template, request, jsonify
import json
import sqlite3
import os
from datetime import datetime, timedelta
import random
from services.location_service import generate_points_around_location

app = Flask(__name__)

def get_db_connection():
    """Create a connection to the SQLite database"""
    db_path = os.path.join(os.path.dirname(__file__), 'addresses.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

@app.route('/')
def welcome():
    """Render the welcome page"""
    return render_template('welcome.html')

@app.route('/form')
def form():
    """Render the form page"""
    return render_template('form.html')

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    """Handle autocomplete requests for addresses"""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Search both full addresses and street names
    cursor.execute(
        """
        SELECT DISTINCT address, latitude, longitude 
        FROM addresses 
        WHERE address LIKE ? OR street LIKE ?
        ORDER BY 
            CASE 
                WHEN address LIKE ? THEN 1
                ELSE 2
            END,
            length(address)
        LIMIT 10
        """, 
        (f"%{query}%", f"%{query}%", f"{query}%")
    )
    
    results = [{'address': row['address'], 'lat': row['latitude'], 'lng': row['longitude']} 
               for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(results)

@app.route('/map', methods=['GET', 'POST'])
def show_map():
    """Process form data and render the map page"""
    if request.method == 'POST':
        # Get form data
        latitude = request.form.get('latitude', '50.7374')  # Default to Bonn
        longitude = request.form.get('longitude', '7.0982')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        # Set defaults if not provided
        if not start_date_str:
            start_date_str = datetime.now().strftime('%Y-%m-%d')
        if not end_date_str:
            end_date_str = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
        # Process the data
        try:
            location_data = generate_points_around_location(
                float(latitude), 
                float(longitude), 
                start_date_str,
                end_date_str
            )
            return render_template('map.html', 
                                  center_lat=latitude, 
                                  center_lng=longitude,
                                  location_data=json.dumps(location_data))
        except Exception as e:
            return render_template('form.html', error=str(e))
    else:
        # If accessed via GET, just show the form
        return render_template('form.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)