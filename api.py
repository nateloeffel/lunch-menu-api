from flask import Flask, jsonify
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re
from flask_cors import CORS  # Import the CORS library

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

def extract_number_id(input_string):
    match = re.search(r'\d+', input_string)
    return match.group() if match else None

def get_lunch_menu():
    current_date = datetime.now().strftime("%m/%d")
    url = "https://www.nutritics.com/menu/ma1135"
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "Failed to retrieve main menu page"}, 500

    soup = BeautifulSoup(response.content, 'html.parser')
    menu_div = None
    for div in soup.find_all("div", class_='menu'):
        span = div.find("span", class_='title')
        if span and current_date in span.text:
            menu_div = div
            break

    if not menu_div:
        return {"error": "No menu found for today's date"}, 404

    menu_id = extract_number_id(menu_div.get("id"))
    if not menu_id:
        return {"error": "Failed to extract menu ID"}, 500

    menu_url = f"https://www.nutritics.com/menu/ma1135/{menu_id}"
    response = requests.get(menu_url)
    if response.status_code != 200:
        return {"error": "Failed to retrieve menu details"}, 500

    soup = BeautifulSoup(response.content, 'html.parser')
    results_div = soup.find('div', id='results')

    if results_div:
        child_divs = results_div.find_all('div', recursive=False)
        if len(child_divs) >= 2:
            first_data_name = child_divs[0].get('data-name')
            second_data_name = child_divs[1].get('data-name')
            return {
                "first_data_name": first_data_name,
                "second_data_name": second_data_name
            }
        else:
            return {"error": "Less than two menu items found for today's date"}, 404
    else:
        return {"error": "No menu data found"}, 404

@app.route('/lunch', methods=['GET'])
def lunch():
    return jsonify(get_lunch_menu())

if __name__ == '__main__':
    app.run(port=5001, debug=True)
