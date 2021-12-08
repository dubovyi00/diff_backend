def preparse(string, n=""):
	# определяем, какого порядка ДУ, если не определено пользователем
    if n == "":
        n = 0
        current = 0
        isThere = False
        for s in string:
            if s == "'":
                if not isThere:
                    isThere = True
                    
                current += 1
                    
            else:
                if isThere:
                    isThere = False
                    if current > n:
                        
                        n = current
                    current = 0

        if current > n:
            n = current

    #print("Порядок: "+str(n))
    
    #обрабатываем все игреки на предмет того, что они функции
    whereIs = []
    for i, si in enumerate(string):
        if si == 'y':
            whereIs.append(i)
    print(whereIs)
    align = 0
    for w in whereIs:
        newstr = string[:w+1+align] + "(x)" + string[w+align+1:]
        print(newstr)
        string = newstr
        align += 3
    
    #обрабатываем знаки производных
    for col in range(n, 0, -1):
        print("'")
        string = string.replace("'" * col, ".diff(x"+",x"*(col-1)+")")
    
    return string