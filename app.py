from flask import Flask, jsonify, request
from flask_cors import CORS
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store user inputs for the first page
first_page_inputs = {}


@app.route('/api/start', methods=['POST'])
def start():
    global first_page_inputs
    data = request.get_json()
    first_page_inputs = {
        'input1': data.get('input1'),
        'input2': data.get('input2')
    }
    return jsonify({'message': 'First page inputs received successfully'})


@app.route('/api/data', methods=['GET'])
def get_data():
    global first_page_inputs

    # Get user input from the first page
    input1 = first_page_inputs.get('input1')
    input2 = first_page_inputs.get('input2')

    # Get user input from the query parameters for the second page
    number1 = request.args.get('number1', type=int)
    number2 = request.args.get('number2', type=int)
    number3 = request.args.get('number3', type=int)
    number4 = request.args.get('number4', type=int)
    string_input = request.args.get('string', type=str)

    # Validate that the sum of percentages is 100 for the second page
    if (number1 + number2 + number3 + number4) != 100:
        return jsonify({'error': 'The sum of percentages must be 100'}), 400

    # Process the percentages to create a pie chart
    percentages = [number1, number2, number3, number4]
    labels = [f'Segment {i}' for i in range(1, 5)]
    plt.pie(percentages, labels=labels, autopct='%1.1f%%', startangle=140, colors=['red', 'green', 'blue', 'yellow'])
    plt.title('Pie Chart of Percentages')

    # Save the plot to a BytesIO object
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.close()

    # Convert the image to base64 for embedding in HTML
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')

    # Construct the response data for the second page
    data = {
        'message': f'Inputs from the first page: {input1}, {input2}',
        'pie_chart': f'data:image/png;base64,{image_base64}'
    }

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
