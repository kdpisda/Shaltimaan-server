from flask import Flask, render_template, request, jsonify
import atexit
import os
import json
import requests
from bs4 import BeautifulSoup as soup

app = Flask(__name__)

db_name = 'mydb'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/',methods=['GET'])
def home():
    return "Shaktimaan Server :-) Coded with love by Kuldeep Pisda, Mayank Chourasia and Vinay Khobragade"

@app.route('/api/get_jobs',methods=['GET'])
def get_job():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    city = request.args.get('city')
    skill = request.args.get('skill')
    my_url = 'https://www.naukri.com/'
    my_url = my_url + str(skill)+'-jobs-in-' + str(city)
    result = requests.get(my_url, headers=headers)
    page_soup = soup(result.content.decode(),"html.parser")
    containers = page_soup.findAll("div",{"itemtype":"http://schema.org/JobPosting"})
    jobs = []
    for container in containers:
        try:
            x = container.findAll("li",{"class":"desig"})
            designation = x[0].text
            x = container.findAll("span",{"class":"exp"})
            experience = x[0].text
            x = container.findAll("span",{"class":"loc"})
            location = x[0].text
            x = container.findAll("span",{"class":"desc"})
            skills = x[0].text
            x = container.findAll("span",{"class":"date"})
            days_ago = x[0].text
        except:
            continue
        x = {}
        x["designation"] = designation
        x["experience"] = experience
        x["location"] = location
        x["skills"] = skills
        x["days_ago"] = days_ago
        jobs.append(x)

    return jsonify(jobs)

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
