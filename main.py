from flask import Flask, request, jsonify
import sympy as sym
import numpy as np
import matplotlib.pyplot as plt
import preparsing
import random
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret'
app.config['CORS_HEADERS'] = 'Content-Type'
    
@app.route("/api/ode", methods=['POST'])
def ode():
    '''
        Решение обыкновенных диффуров
        
        Принимает параметры:
            equation - уравнение (поддерживается пока только формат F(x, y, y', y'', и. т. д.) = 0) /строка/
            border - граничные условия (необязателен) /массив массивов вида [операнд, число x, правая часть], например, {["y", "0", "1"], ["y'", "0", "0"]}/
            
        Отправляет в ответ:
            solution - массив выражений, являющихся решениями данного ДУ
            
            либо
            
            err - описание
           
            
    '''
    
    
    rez = {}
    
    _id = random.randint(1, 1000)
    print("Получен новый запрос, id="+str(_id))
    req = request.get_json(force=True)
    print("["+str(_id)+"] "+str(request.get_data()))
    print(req)
    try:
        print("Поехали")
        
        eq_str = preparsing.preparse(req['equation']) 
        equation = sym.parse_expr(eq_str)
        print("["+str(_id)+"] Выражение успешно переписано: "+eq_str)
        print("["+str(_id)+"] Выражение обработано успешно")
        borders = {}
        if req['border'] != []:
            for b in req['border']:
                if b[0] == "y":
                    borders[sym.sympify(b[0]+"("+b[1]+")")] = sym.sympify(b[2])
                elif b[0] == "y'":
                    borders[sym.sympify(b[0][0]+"(x).diff(x).subs(x, "+b[1]+")")] = sym.sympify(b[2])
        print("["+str(_id)+"] Граничные условия обработаны успешно")
    
    except (NameError, IndexError):
        print("["+str(_id)+"] Ошибка при обработке введённых данных")
        rez["err"] = "Ошибка при обработке введённых данных"
        resp = jsonify(rez)
        resp.status_code = 400
        return resp
    
    x = sym.Symbol('x')
    y = sym.Function('y')(x)
    
    
    try:
        if borders == {}:
            print("Нет")
            answer = sym.dsolve(equation, y) #, ics=borders)
        else:
            print("Есть")
            answer = sym.dsolve(equation, y, ics=borders)
    except (NameError, IndexError):
        print("["+str(_id)+"] Ошибка во время решения уравнения")
        rez["err"] = "Ошибка во время решения уравнения"
        resp = jsonify(rez)
        resp.status_code = 400
        return resp
    except ValueError:
        rez["solution"] = ["Нет решения"]
        resp = jsonify(rez)
        resp.status_code = 200
        print("["+str(_id)+"] Уравнение успешно решено")
        print("["+str(_id)+"] Решения отправлены клиенту")
        return resp
    
    print(sym.classify_ode(equation))
    
    print("["+str(_id)+"] Уравнение успешно решено")
    
    rez = {}
    solution = []
    if type(answer) == list:
        for a in answer:
            solution.append(preparsing.postparse(str(a.lhs))+" = "+preparsing.postparse(str(a.rhs)))
    else:
        solution.append(preparsing.postparse(str(answer.lhs))+" = "+preparsing.postparse(str(answer.rhs)))
    rez["solution"] = solution
    resp = jsonify(rez)
    resp.status_code = 200
    print("["+str(_id)+"] Решения отправлены клиенту")
    return resp

@app.route("/api/sode", methods=['POST'])
def sode():
    '''
        Решение систем ОДУ
        
        Принимает параметры:
            equations - уравнение (поддерживается пока только формат F(x, y, y', y'', и. т. д.) = 0) /массив строк/
            border - граничные условия (необязателен) /массив массивов вида [операнд, число x, правая часть], например, {["y", "0", "1"], ["y'", "0", "0"]}/
            
        Отправляет в ответ:
            solution - массив выражений, являющихся решениями данного ДУ
            
            либо
            
            err - описание
            
    '''
    rez = {}

    _id = random.randint(1, 1000)
    print("Получен новый запрос, id="+str(_id))
    req = request.get_json()
    
    t = sym.Symbol('t')
    x = sym.Function('x')(t)
    y = sym.Function('y')(t)
    
    try:
        print("Поехали")
        
        eqs_str = req['equations']
        eqs = []
        for e in eqs_str:
            eqs.append(sym.parse_expr(preparsing.preparse(e, mode='sode'))) 
        print("["+str(_id)+"] Выражения обработаны и переписаны успешно")
        borders = {}
        if req['border'] != []:
        
            for b in req['border']:
                if b[0] == "y" or b[0] == "x":
                    borders[sym.sympify(b[0]+"("+b[1]+")")] = sym.sympify(b[2])
                elif b[0] == "y'" or b[0] == "x'":
                    borders[sym.sympify(b[0][0]+"(t).diff(t).subs(t, "+b[1]+")")] = sym.sympify(b[2])
    
    except (NameError, IndexError):
        print("["+str(_id)+"] Ошибка при обработке введённых данных")
        rez["err"] = "Ошибка при обработке введённых данных"
        resp = jsonify(rez)
        resp.status_code = 400
        return resp
    

    try:
        if borders == {}:
            answer = sym.dsolve(eqs, [x, y]) 
        else:
            answer = sym.dsolve(eqs, [x, y], ics=borders)
    except (NameError, IndexError, NotImplementedError):
        print("["+str(_id)+"] Ошибка во время решения системы")
        rez["err"] = "Ошибка во время решения уравнения"
        resp = jsonify(rez)
        resp.status_code = 400
        return resp
    except ValueError:
        rez["solution"] = ["Нет решения"]
        resp = jsonify(rez)
        resp.status_code = 200
        print("["+str(_id)+"] Уравнение успешно решено")
        print("["+str(_id)+"] Решения отправлены клиенту")
        return resp
    
    print("["+str(_id)+"] Система успешно решена")
    
    rez = {}
    solution = []
    solution = []
    if type(answer) == list:
        for a in answer:
            solution.append(preparsing.postparse(str(a.lhs))+" = "+preparsing.postparse(str(a.rhs)))
    else:
        solution.append(preparsing.postparse(str(answer.lhs))+" = "+preparsing.postparse(str(answer.rhs)))
    rez["solution"] = solution
    resp = jsonify(rez)
    resp.status_code = 200
    print("["+str(_id)+"] Решения отправлены клиенту")
    return resp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
