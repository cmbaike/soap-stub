from flask import Flask, request, Response
from xml.etree import ElementTree as ET
import uuid

app = Flask(__name__)

# In-memory storage to maintain state
request_status = {}


@app.route('/soap', methods=['POST'])
def handle_soap():

    if 'bomb accept' in request.data.decode('utf-8').lower():
        custom_id = str(uuid.uuid4())
        # Load the static SOAP response from a file
        with open('static_response.xml', 'r') as file:
            response = file.read().replace("{{detectionId}}", custom_id)
        request_status[custom_id] = {"status": "Initiated", "type":"False Positive"}
        return Response(response, mimetype='application/soap+xml')

    if 'bomb reject' in request.data.decode('utf-8').lower():
        custom_id = str(uuid.uuid4())
        # Load the static SOAP response from a file
        with open('static_response.xml', 'r') as file:
            response = file.read().replace("{{detectionId}}", custom_id)
        request_status[custom_id] = {"status": "Initiated", "type":"Real Violation"}
        return Response(response, mimetype='application/soap+xml')



@app.route('/soap/status', methods=['POST'])
def handle_status():
    
    parser = ET.fromstring(request.data.decode('utf-8'))
    namespace={'soap12': 'http://www.w3.org/2003/05/soap-envelope', 'ns':'spyne.workflow.soap'}
    request_custom_id=parser.find(path='.//custom_id',namespaces=namespace).text
    
    if request_custom_id in request_status:
        current_status= request_status[request_custom_id]['status']
        if current_status.lower() == 'initiated':
            with open('check_status.xml', 'r') as file:
              response = file.read().replace("{{status}}", "New")
            request_status[request_custom_id]["status"] =  "New"
            return Response(response, mimetype='application/soap+xml')
        elif current_status.lower() == 'new':
            with open('check_status.xml', 'r') as file:
              response = file.read().replace("{{status}}", "Investigating")
            request_status[request_custom_id]["status"]="Investigating"
            return Response(response, mimetype='application/soap+xml')
        elif current_status.lower() == 'investigating':
            with open('check_status.xml', 'r') as file:
              response = file.read().replace("{{status}}", request_status[request_custom_id]['type'])
            request_status[request_custom_id]["status"] = request_status[request_custom_id]['type']
            return Response(response, mimetype='application/soap+xml')
        else:
            with open('check_status.xml', 'r') as file:
              response = file.read().replace("{{status}}", request_status[request_custom_id]['type'])
            request_status[request_custom_id]["status"] = request_status[request_custom_id]['type']
            return Response(response, mimetype='application/soap+xml')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
