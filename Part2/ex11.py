def calculate(a, operator, b):
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        return a / b
    else:
        return "Invalid operator"
print(calculate(10, "+", 10))
print(calculate(10, "-", 10))
print(calculate(10, "*", 10))
print(calculate(10, "/", 10))

