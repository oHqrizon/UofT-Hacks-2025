from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def main():
    if request.method == 'POST': #if submitted data
        #store name and education level
        user = request.form['nm']
        level = request.form['education'] 
        return redirect(url_for('display', usr=user, edu=level)) #redirect to display function, but pass stored variables
    else:
        return render_template('home.html')
    
@app.route('/<usr>')
def display(usr): #name as paramater
    selected_option = request.args.get('edu') #recieve edu variable 
    return f'<h1>Welcome {usr}! Your education is {selected_option} level.</h1>'  

if __name__ == '__main__':
    app.run(debug=True)