from flask import Flask, render_template, request, Response, jsonify
import sqlite3
import json


app = Flask(__name__)

def connect_db():
    connect = sqlite3.connect("retirement.db")
    cursor = connect.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS Scenarios (
                   id INTEGER PRIMARY KEY,
                   name TEXT NOT NULL,
                   nestEgg REAL,
                   rate REAL,
                   salary INT,
                   contributed REAL,
                   currentAge INT,
                   retirementAge INT,
                   salaryIncrease REAL,
                   incomeActiveYears INT,
                   incomeInactiveYears REAL,
                   totalSaved REAL,
                   ssnEstimate REAL,
                   yearly_summary TEXT)

    """)

    connect.commit()
    connect.close()

connect_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def retirement():
    return render_template('retirement.html')

def ssn(salary, retirementAge, currentAge, salaryIncrease):
    if retirementAge < 62:
        return 0
    
    for year in range(currentAge, retirementAge-1):
        new_salary = round((wage_history[-1] * (1 + salaryIncrease)),2)
        wage_history.append(new_salary)
    
    # Ensure up to 35 years of wage history (pad with zeros if necessary)
    if len(wage_history) < 35:
        wage_history = [0] * (35 - len(wage_history)) + wage_history

    # Select highest available earning years (up to 35)
    top_earnings = sorted(wage_history, reverse=True)[:35]

    # Compute AIME (Average Indexed Monthly Earnings)
    AIME = sum(top_earnings)  / (420)  # Monthly earnings average

    # Bend points for PIA calculation (adjusted dynamically if needed)
    bend_point_1 = 1226  # First bend point (monthly)
    bend_point_2 = 7391  # Second bend point (monthly)

    # Compute PIA (Primary Insurance Amount) - monthly benefit at full retirement age
    if AIME <= bend_point_1:
        PIA = 0.9 * AIME
    elif AIME <= bend_point_2:
        PIA = 0.9 * bend_point_1 + 0.32 * (AIME - bend_point_1)
    else:
        PIA = 0.9 * bend_point_1 + 0.32 * (bend_point_2 - bend_point_1) + 0.15 * (AIME - bend_point_2)
    
    # Reduction for early claiming (if before full retirement age)
    months_early = (67 - retirementAge) * 12
    
    if months_early > 36:
        reduction = (36 * (5/9) + (months_early - 36) * (5/12)) / 100
    else:
        reduction = (months_early * (5/9)) / 100
    
    # Apply reduction for early claiming
    ssa_income_monthly = PIA * (1 - reduction)
    
    # Convert to annual income
    ssa_income_annual = ssa_income_monthly * 12

    return ssa_income_annual
        

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
    # Chart for yearly income
    age_retirement = []
    income_retirement = []
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
            "endingBalance": round(totalSaved,0)
        })
        
        contributed_amount += contributed_amount * (salaryIncrease/100)

    for i in range(retirementAge,100):
        age_retirement.append(i)
        beginning = totalSaved
        contributed_amount = 0
        if i <= 85:
            withdrawn = final_salary * incomeActiveYears /100
        else:
            withdrawn = final_salary * incomeInActiveYears /100
        
        income_retirement.append(withdrawn)

        totalSaved = totalSaved + totalSaved * (rate/100) - withdrawn

        if totalSaved < 0:
            totalSaved = 0

        yearly_saving.append({
            "Age": i,
            "Beginning Balance": round(beginning,0),
            "Contribution": contributed_amount,
            "Withdrawn": round(withdrawn,0),
            "endingBalance": round(totalSaved,0)
        })

        if totalSaved == 0:
            break

    return yearly_saving, age_retirement, income_retirement


@app.route('/calculate',methods=['POST'])
def calculate():
    # Get the input values from the form
    name = request.form['name']
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
    
    yearly_summary,age_retirement, income_retirement = retirement_summary(nestEgg,rate,salary,contributed,currentAge,retirementAge,
                      salaryIncrease,incomeActiveYears,incomeInActiveYears)
    
    # Save to Database
    conn = sqlite3.connect("retirement.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scenarios (name, nestEgg, rate, salary, contributed, currentAge, retirementAge, salaryIncrease, incomeActiveYears, incomeInactiveYears, yearly_summary) VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                   (name, nestEgg, rate, salary, contributed, currentAge, retirementAge, salaryIncrease, incomeActiveYears, incomeInActiveYears, json.dumps(yearly_summary)))
    conn.commit()
    conn.close()
    
    return render_template('retirement.html', totalSaved=f"${totalSaved:,.0f}",
                               nestEgg=nestEgg, rate=rate, salary=salary, contributed=contributed, 
                               currentAge=currentAge, retirementAge=retirementAge, salaryIncrease=salaryIncrease, 
                               incomeActiveYears = incomeActiveYears, incomeInActiveYears = incomeInActiveYears, 
                            yearly_summary = yearly_summary, age_retirement = age_retirement, income_retirement = income_retirement)

    # return jsonify({"total_savings": round(totalSaved, 2), "yearly_data": yearly_summary})


if __name__=='__main__':
    app.run(debug=True)