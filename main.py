from flask import Flask, jsonify, render_template, request, url_for, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# @app.route('/', methods=["POST", "GET"])
# def main():
#     if request.method == 'POST': #if submitted data
#         #store name and education level
#         user = request.form['nm']
#         level = request.form['education'] 
#         return redirect(url_for('display', usr=user, edu=level)) #redirect to display function, but pass stored variables
#     else:
#         return render_template('home.html')
    
# @app.route('/<usr>')
# def display(usr): #name as paramater
#     selected_option = request.args.get('edu') #recieve edu variable 
#     return render_template("start.html", usr=usr, selected_option=selected_option)

@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.get_json()
    name = data.get('name')
    education = data.get('education')

    print(f"Name: {name}, Education Level: {education}")

    return jsonify({
        "message": "Form submitted",
        "submitted_data": data
    })

if __name__ == '__main__':
    app.run(debug=True)