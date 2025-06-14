from graphviz import Digraph
import string

# Clase para generar nombres únicos de estado
global_estado_factory = None
class EstadoFactory:
    def __init__(self):
        self.contador = 0

    def nuevo(self):
        nombre = f"q{self.contador}"
        self.contador += 1
        return nombre

# Clase para representar un AF
class AF:
    def __init__(self):
        global global_estado_factory
        if global_estado_factory is None:
            global_estado_factory = EstadoFactory()

        self.estados = set()
        self.transiciones = []  # (origen, simbolo, destino)
        self.inicial = None
        self.finales = set()

    def nuevo_estado(self):
        nuevo = global_estado_factory.nuevo()
        self.estados.add(nuevo)
        return nuevo

    @staticmethod
    def simbolo(simbolo):
        af = AF()
        i = af.nuevo_estado()
        f = af.nuevo_estado()
        af.inicial = i
        af.finales = {f}
        af.transiciones.append((i, simbolo, f))
        return af

    def unir(self, otro):
        af = AF()
        af.estados.update(self.estados)
        af.estados.update(otro.estados)
        af.transiciones.extend(self.transiciones)
        af.transiciones.extend(otro.transiciones)

        # El estado inicial es el de la primera alternativa
        af.inicial = self.inicial
        # El estado final es el de la segunda alternativa
        af.finales = otro.finales

        # Conectamos el estado inicial con el inicial del otro autómata mediante epsilon
        af.transiciones.append((af.inicial, 'ε', otro.inicial))
        # Conectamos los estados finales de self con los finales de otro mediante epsilon
        for fin in self.finales:
            for fin_otro in otro.finales:
                af.transiciones.append((fin, 'ε', fin_otro))

        return af

    def concatenar(self, otro):
        af = AF()
        af.estados.update(self.estados)
        af.estados.update(otro.estados)
        af.transiciones.extend(self.transiciones)
        af.transiciones.extend(otro.transiciones)

        for fin in self.finales:
            af.transiciones.append((fin, 'ε', otro.inicial))

        af.inicial = self.inicial
        af.finales = otro.finales
        return af

    def estrella(self):
        af = AF()
        i = af.nuevo_estado()
        f = af.nuevo_estado()
        af.inicial = i
        af.finales = {f}

        af.estados.update(self.estados)
        af.transiciones.extend(self.transiciones)

        af.transiciones.append((i, 'ε', self.inicial))
        af.transiciones.append((i, 'ε', f))

        for fin in self.finales:
            af.transiciones.append((fin, 'ε', self.inicial))
            af.transiciones.append((fin, 'ε', f))

        return af

    def graficar(self, nombre="AF"):
        dot = Digraph()
        dot.attr(rankdir='LR')

        dot.node('', shape='none')
        for estado in self.estados:
            if estado in self.finales:
                dot.node(estado, shape='doublecircle')
            else:
                dot.node(estado)

        dot.edge('', self.inicial)

        for (o, a, d) in self.transiciones:
            dot.edge(o, d, label=a)

        dot.render(nombre, view=True, format='png')


# Parser simple para expresiones regulares con +, *, () y concatenación implícita
def parsear(exp):
    def prioridad(op):
        if op == '*': return 3
        if op == '.': return 2
        if op == '+': return 1
        return 0

    # Insertar '.' para concatenación explícita
    def insertar_concatenacion(exp):
        nueva = ''
        for i in range(len(exp)):
            nueva += exp[i]
            if i+1 < len(exp):
                if (exp[i] in string.ascii_letters or exp[i] == ')' or exp[i] == '*') and (exp[i+1] in string.ascii_letters or exp[i+1] == '('):
                    nueva += '.'
        return nueva

    salida = []
    operadores = []
    exp = insertar_concatenacion(exp)

    for c in exp:
        if c in string.ascii_letters:
            salida.append(AF.simbolo(c))
        elif c == '(':
            operadores.append(c)
        elif c == ')':
            while operadores and operadores[-1] != '(':
                aplicar_operador(salida, operadores.pop())
            operadores.pop()
        elif c in ['+', '.', '*']:
            while operadores and prioridad(operadores[-1]) >= prioridad(c):
                if c != '*':
                    aplicar_operador(salida, operadores.pop())
                else:
                    break
            if c == '*':
                aplicar_operador(salida, c)
            else:
                operadores.append(c)

    while operadores:
        aplicar_operador(salida, operadores.pop())

    return salida[0]

def aplicar_operador(pila, op):
    if op == '*':
        a = pila.pop()
        pila.append(a.estrella())
    else:
        b = pila.pop()
        a = pila.pop()
        if op == '+':
            pila.append(a.unir(b))
        elif op == '.':
            pila.append(a.concatenar(b))


# Ejemplo de uso:
expresion = "(a*b+c)"
af = parsear(expresion)
af.graficar("automa_kleene")