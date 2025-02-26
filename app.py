from flask import Flask, render_template, request, Response 
import sqlite3


app = Flask(__name__)


sqliteConnection = sqlite3.connect('sql.db')
cursor = sqliteConnection.cursor()
print('DB init')


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

def retirement_summary(nestEgg,rate,salary,contributed,currentAge,retirementAge,
                      salaryIncrease,incomeActiveYears,incomeInActiveYears):
    # Calculate the total amount of money saved by the time of retirement
    totalSaved = nestEgg
    contributed_amount = salary * (contributed/100)
    yearly_saving = []
    final_salary = salary
    for i in range(currentAge, retirementAge):
        beginning = totalSaved
        totalSaved += totalSaved * (rate/100)
        totalSaved += contributed_amount

        withdrawn = 0
        final_salary += final_salary * (salaryIncrease/100)
        yearly_saving.append({
            "Age": i,
            "Beginning Balance": round(beginning,0),
            "Contribution": round(contributed_amount,0),
            "Withdrawn": withdrawn,
            "Ending Balance": round(totalSaved,0)
        })
        
        contributed_amount += contributed_amount * (salaryIncrease/100)

    for i in range(retirementAge,100):
        beginning = totalSaved
        contributed_amount = 0
        if i <= 85:
            withdrawn = final_salary * incomeActiveYears /100
        else:
            withdrawn = final_salary * incomeInActiveYears /100

        totalSaved = totalSaved + totalSaved * (rate/100) - withdrawn

        if totalSaved < 0:
            totalSaved = 0

        yearly_saving.append({
            "Age": i,
            "Beginning Balance": round(beginning,0),
            "Contribution": contributed_amount,
            "Withdrawn": round(withdrawn,0),
            "Ending Balance": round(totalSaved,0)
        })

        if totalSaved == 0:
            break

    return yearly_saving


@app.route('/calculate',methods=['POST'])
def calculate():
    # Get the input values from the form
    nestEgg = int(request.form['nestEgg'])
    rate = float(request.form['rate'])
    salary = int(request.form['salary'])
    contributed = float(request.form['contributed'])
    currentAge = int(request.form['currentAge'])
    retirementAge = int(request.form['retirementAge'])
    salaryIncrease = float(request.form['salaryIncrease'])
    incomeActiveYears = int(request.form['incomeActiveYears'])
    incomeInActiveYears = int(request.form['incomeInactiveYears'])

    totalSaved = retirement_saving(nestEgg,rate,salary,contributed,currentAge,retirementAge,
                      salaryIncrease)
    
    yearly_summary = retirement_summary(nestEgg,rate,salary,contributed,currentAge,retirementAge,
                      salaryIncrease,incomeActiveYears,incomeInActiveYears)
    
    return render_template('retirement.html', totalSaved=f"${totalSaved:,.0f}",
                               nestEgg=nestEgg, rate=rate, salary=salary, contributed=contributed, 
                               currentAge=currentAge, retirementAge=retirementAge, salaryIncrease=salaryIncrease, 
                               incomeActiveYears = incomeActiveYears, incomeInActiveYears = incomeInActiveYears, 
                            yearly_summary = yearly_summary)


if __name__=='__main__':
    app.run(debug=True)