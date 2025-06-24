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

    @staticmethod
    def espontaneo():
        """Crea un autómata que acepta solo la cadena vacía"""
        af = AF()
        q = af.nuevo_estado()
        af.inicial = q
        af.finales = {q}  # El mismo estado es inicial y final
        # No se necesitan transiciones
        return af

    @staticmethod
    def vacio():
        """Crea un autómata que no acepta ninguna cadena (lenguaje vacío)"""
        af = AF()
        i = af.nuevo_estado()
        af.inicial = i
        af.finales = set()  # Sin estados finales
        return af

    def unir(self, otro):
        af = AF()
        # Crear nuevo estado inicial
        nuevo_inicial = af.nuevo_estado()
        # Crear nuevo estado final
        nuevo_final = af.nuevo_estado()
        
        # Copiar estados y transiciones de ambos autómatas
        af.estados.update(self.estados)
        af.estados.update(otro.estados)
        af.transiciones.extend(self.transiciones)
        af.transiciones.extend(otro.transiciones)

        # Establecer el nuevo estado inicial y final
        af.inicial = nuevo_inicial
        af.finales = {nuevo_final}

        # Conectar el nuevo estado inicial con los estados iniciales de ambos autómatas
        af.transiciones.append((nuevo_inicial, 'λ', self.inicial))
        af.transiciones.append((nuevo_inicial, 'λ', otro.inicial))
        
        # Conectar todos los estados finales de ambos autómatas al nuevo estado final
        for fin in self.finales:
            af.transiciones.append((fin, 'λ', nuevo_final))
        for fin in otro.finales:
            af.transiciones.append((fin, 'λ', nuevo_final))

        return af

    def concatenar(self, otro):
        af = AF()
        af.estados.update(self.estados)
        af.estados.update(otro.estados)
        af.transiciones.extend(self.transiciones)
        af.transiciones.extend(otro.transiciones)

        for fin in self.finales:
            af.transiciones.append((fin, 'λ', otro.inicial))

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

        af.transiciones.append((i, 'λ', self.inicial))
        af.transiciones.append((i, 'λ', f))

        for fin in self.finales:
            af.transiciones.append((fin, 'λ', self.inicial))
            af.transiciones.append((fin, 'λ', f))

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


# Función para expandir el operador $
def expandir_dolar(exp):
    """Expande expr1$expr2 a (expr1expr1+expr1expr2+expr2expr2)"""
    def extraer_expresion_izquierda(s, pos_dolar):
        """Extrae la expresión completa a la izquierda del $"""
        if pos_dolar == 0:
            return "", 0
        
        # Si termina con ), buscar el ( correspondiente
        if s[pos_dolar - 1] == ')':
            nivel = 1
            i = pos_dolar - 2
            while i >= 0 and nivel > 0:
                if s[i] == ')':
                    nivel += 1
                elif s[i] == '(':
                    nivel -= 1
                i -= 1
            return s[i + 1:pos_dolar], i + 1
        
        # Si termina con *, incluir el símbolo anterior
        elif s[pos_dolar - 1] == '*':
            if pos_dolar >= 2:
                return s[pos_dolar - 2:pos_dolar], pos_dolar - 2
            else:
                return s[pos_dolar - 1:pos_dolar], pos_dolar - 1
        
        # Si es un símbolo simple
        else:
            return s[pos_dolar - 1:pos_dolar], pos_dolar - 1
    
    def extraer_expresion_derecha(s, pos_dolar):
        """Extrae la expresión completa a la derecha del $"""
        if pos_dolar + 1 >= len(s):
            return "", len(s)
        
        inicio = pos_dolar + 1
        
        # Si empieza con (, buscar el ) correspondiente
        if s[inicio] == '(':
            nivel = 1
            i = inicio + 1
            while i < len(s) and nivel > 0:
                if s[i] == '(':
                    nivel += 1
                elif s[i] == ')':
                    nivel -= 1
                i += 1
            # Verificar si después hay *
            if i < len(s) and s[i] == '*':
                return s[inicio:i + 1], i + 1
            else:
                return s[inicio:i], i
        
        # Si es un símbolo simple, verificar si tiene *
        else:
            if inicio + 1 < len(s) and s[inicio + 1] == '*':
                return s[inicio:inicio + 2], inicio + 2
            else:
                return s[inicio:inicio + 1], inicio + 1
    
    resultado = ""
    i = 0
    
    while i < len(exp):
        if exp[i] == '$':
            # Extraer expresiones a ambos lados del $
            expr_izq, inicio_izq = extraer_expresion_izquierda(exp, i)
            expr_der, fin_der = extraer_expresion_derecha(exp, i)
            
            # Construir la expansión
            expansion = f"({expr_izq}{expr_izq}+{expr_izq}{expr_der}+{expr_der}{expr_der})"
            
            # Reemplazar en el resultado
            # Eliminar la expresión izquierda ya procesada
            resultado = resultado[:inicio_izq] if inicio_izq < len(resultado) else resultado
            resultado += expansion
            i = fin_der
        else:
            resultado += exp[i]
            i += 1
    
    return resultado

# Parser simple para expresiones regulares con +, *, () y concatenación implícita
def parsear(exp):
    # Expandir operadores $ antes de parsear
    exp = expandir_dolar(exp)

    # Casos base especiales
    if exp == "":
        return AF.vacio()  # Expresión vacía = lenguaje vacío
    if exp == "λ":
        return AF.espontaneo()  # Solo espontaneo = acepta cadena vacía

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
                if (exp[i] in string.ascii_letters or exp[i] == ')' or exp[i] == '*' or exp[i] == 'λ') and (exp[i+1] in string.ascii_letters or exp[i+1] == '(' or exp[i+1] == 'λ'):
                    nueva += '.'
        return nueva

    salida = []
    operadores = []
    exp = insertar_concatenacion(exp)

    for c in exp:
        if c in string.ascii_letters:
            salida.append(AF.simbolo(c))
        elif c == 'λ':
            salida.append(AF.espontaneo())
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
expresion = "(a*)$(b*)"
af = parsear(expresion)
af.graficar("automa_kleene")