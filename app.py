# Flask dedicated file
from flask import Flask, request, render_template, send_file, redirect, send_from_directory, url_for
import os

from application import Application
from data import locations

app = Flask(__name__, template_folder='templates', static_folder='static')

# Instantiate the application state/managers
web_app = Application()

# Set folders based on Flask app context
web_app.map_folder = os.path.join(app.root_path, 'cached maps')
web_app.favicon_directory = os.path.join(app.root_path, 'static')
os.makedirs(web_app.map_folder, exist_ok=True)


# Route for favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(web_app.favicon_directory, 'favicon.ico')


# Route to get the live location
@app.route('/get_location', methods=['POST'])
def get_location():
    data = request.get_json()
    user_location = data.get('location')
    web_app.start_latitude = user_location['latitude']
    web_app.start_longitude = user_location['longitude']
    web_app.live_location = True
    return ('', 204)


# Route to set the users start and destination positions
@app.route('/set', methods=['POST'])
def set_location():
    web_app.start_name = request.form['location']
    web_app.destination_name = request.form['destination']

    if web_app.start_name == '':
        # Live location mode
        destination_coordinates = web_app.location_manager.get_coordinates(web_app.destination_name)
        web_app.destination_latitude, web_app.destination_longitude = destination_coordinates
        return redirect('/Mymap')
    else:
        start_coordinates = web_app.location_manager.get_coordinates(web_app.start_name)
        web_app.start_latitude, web_app.start_longitude = start_coordinates

        destination_coordinates = web_app.location_manager.get_coordinates(web_app.destination_name)
        web_app.destination_latitude, web_app.destination_longitude = destination_coordinates
        return redirect('/Mymap')


# Home route
@app.route('/')
def home():
    web_app.file_manager.delete_old_map_files(web_app.map_folder)
    return render_template('home.html')


# Location route
@app.route('/location')
def location():
    return render_template('Geo.html', locations=locations)


# Show map with every point route
@app.route('/wholemap')
def whole_map():
    return render_template('wholeMap.html')


# Map route
@app.route('/Mymap')
def my_map():
    # Generate map and return filename
    html_filename = web_app.map_manager.generate_map(
        web_app.start_latitude,
        web_app.start_longitude,
        web_app.destination_latitude,
        web_app.destination_longitude,
        use_live_location=web_app.live_location,
        speed_kmh=web_app.speed,
        result_html_initial=web_app.result,
        start_name=web_app.start_name,
        destination_name=web_app.destination_name,
        map_folder=web_app.map_folder,
        navbar_template_path=os.path.join('templates', 'navbar.html'),
    )
    web_app.html_filename = html_filename
    # Reset live location flag after generating the map
    web_app.live_location = False
    return redirect(url_for('show_map', html_filename=web_app.html_filename))


# Route to show the map
@app.route('/<html_filename>')
def show_map(html_filename):
    web_app.file_manager.delete_old_map_files(web_app.map_folder)
    return send_file(os.path.join(web_app.map_folder, f'{html_filename}'))


# Error handlers
@app.errorhandler(404)
def not_found_error(e):
    app.logger.error(f'Page not found: {getattr(e, "description", "")}, status code: {getattr(e, "code", 404)}')
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f'Internal server error: {getattr(e, "description", "")}, status code: {getattr(e, "code", 500)}')
    return render_template('500.html'), 500


# Start the Flask web app on all interfaces
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, debug=True)
    # ssl_context=("cert.pem", "privkey.pem")