from flask import Flask, render_template, request, Response 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def retirement():
    return render_template('retirement.html')

def retirement_saving(nestEgg,rate,salary,contributed,currentAge,retirementAge,
                      salaryIncrease):
    # Calculate the total amount of money saved by the time of retirement
    totalSaved = nestEgg
    contributed_amount = salary * (contributed/100)
    for i in range(currentAge, retirementAge):
        totalSaved += totalSaved * (rate/100)
        totalSaved += contributed_amount
        contributed_amount += contributed_amount * (salaryIncrease/100)
        
    return totalSaved

def yearly_saving(nestEgg,rate,salary,contributed,currentAge,retirementAge,
                      salaryIncrease,incomeActiveYears,incomeInActiveYears):
    # Calculate the total amount of money saved by the time of retirement
    totalSaved = nestEgg
    contributed_amount = salary * (contributed/100)
    yearly_saving = []
    for i in range(currentAge, retirementAge):
        totalSaved += totalSaved * (rate/100)
        totalSaved += contributed_amount
        contributed_amount += contributed_amount * (salaryIncrease/100)
        yearly_saving.append(
            
        )


@app.route('/calculate',methods=['POST'])
def calculate():
    # Get the input values from the form
    nestEgg = float(request.form['nestEgg'])
    rate = float(request.form['rate'])
    salary = float(request.form['salary'])
    contributed = float(request.form['contributed'])
    currentAge = int(request.form['currentAge'])
    retirementAge = int(request.form['retirementAge'])
    salaryIncrease = float(request.form['salaryIncrease'])
    incomeActiveYears = float(request.form['incomeActiveYears'])
    incomeInActiveYears = float(request.form['incomeInactiveYears'])

    totalSaved = retirement_saving(nestEgg,rate,salary,contributed,currentAge,retirementAge,
                      salaryIncrease)
    
    return render_template('retirement.html', totalSaved=f"${totalSaved:,.2f}",
                               nestEgg=nestEgg, rate=rate, salary=salary, contributed=contributed, 
                               currentAge=currentAge, retirementAge=retirementAge, salaryIncrease=salaryIncrease)


if __name__=='__main__':
    app.run(debug=True)