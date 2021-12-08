from flask import Flask, request, jsonify
import sympy as sym
from sympy.abc import x
import numpy as np
import matplotlib.pyplot as plt
import preparsing
import random

app = Flask(__name__)
    
@app.route("/api/ode", methods=['POST'])
def ode():
    '''
        Решение обыкновенных диффуров
        
        Принимает параметры:
            equation - уравнение (поддерживается пока только формат F(x, y, y', y'', и. т. д.) = 0) /строка/
            border - граничные условия (необязателен) /массив массивов вида [операнд, число x, правая часть], например, {["y", "0", "1"], ["y'", "0", "0"]}/
            eq_type - тип уравнения (необязателен, пока на функцию не влияет)  /строка/
            n - порядок уравнения (необязателен) /строка с целым числом/
            
        Отправляет в ответ:
            solution - массив выражений, являющихся решениями данного ДУ
            
            либо
            
            err - описание
           
        TO DO:
            * прописать обработку и отправку данных в случае отсутствия решения уравнения
            * добавить отправку переведённых в картинки формул
            
    '''
    
    rez = {}
    
    _id = random.randint(1, 1000)
    print("Получен новый запрос, id="+str(_id))
    req = request.get_json()
    print(req)
    try:
        print("Поехали")
        eq_str = preparsing.preparse(req['equation']) 
        #if n == "":
        #    eq_str = preparsing.preparse(req['equation']) 
        #else:
        #    eq_str = preparsing.preparse(req['equation'], n)
        print("["+str(_id)+"] Выражение успешно переписано: "+eq_str)
        equation = sym.parse_expr(eq_str) 
        print("["+str(_id)+"] Выражение обработано успешно")
        eq_type = req['eq_type']
        borders = {}
        for b in req['border']:
            borders[sym.sympify(b[0]+"("+b[1]+")")] = sym.sympyfy(b[2])
        print("["+str(_id)+"] Граничные условия обработаны успешно")
    
    except NameError:
        rez["err"] = "Ошибка при обработке введённых данных"
        resp = jsonify(rez)
        resp.status_code = 400
        return resp
    
    x = sym.Symbol('x')
    y = sym.Function('y')(x)
    
    try:
        answer = sym.dsolve(equation, y, ics=borders)
    except NameError:
        rez["err"] = "Ошибка во время решения уравнения"
        resp = jsonify(rez)
        resp.status_code = 400
        return resp
    
    rez = {}
    solution = []
    if type(answer) == list:
        for a in answer:
            solution.append(str(a.lhs)+"="+str(a.rhs))
    else:
        solution.append(str(answer.lhs)+"="+str(answer.rhs))
    rez["solution"] = solution
    resp = jsonify(rez)
    resp.status_code = 200
    return resp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)