import re
from collections import defaultdict
from graphviz import Digraph

class Estado:
    """Representa un estado del autómata"""
    contador = 0
    
    def __init__(self, es_inicial=False, es_final=False):
        Estado.contador += 1
        self.id = Estado.contador
        self.es_inicial = es_inicial
        self.es_final = es_final
    
    def __str__(self):
        return f"q{self.id}"
    
    def __repr__(self):
        return self.__str__()

class AFND:
    """Autómata Finito No Determinístico"""
    
    def __init__(self):
        self.estados = set()
        self.alfabeto = set()
        self.transiciones = defaultdict(lambda: defaultdict(set))  # {estado: {símbolo: {estados}}}
        self.estado_inicial = None
        self.estados_finales = set()
    
    def agregar_estado(self, estado):
        """Agrega un estado al autómata"""
        self.estados.add(estado)
        if estado.es_inicial:
            self.estado_inicial = estado
        if estado.es_final:
            self.estados_finales.add(estado)
    
    def agregar_transicion(self, estado_origen, simbolo, estado_destino):
        """Agrega una transición al autómata"""
        self.transiciones[estado_origen][simbolo].add(estado_destino)
        if simbolo != 'ε':  # Lambda/epsilon no se agrega al alfabeto
            self.alfabeto.add(simbolo)
    
    def visualizar(self, nombre_archivo="automata"):
        """Genera el diagrama del autómata usando Graphviz"""
        dot = Digraph(comment='AFND')
        dot.attr(rankdir='LR')
        
        # Agregar nodo invisible para la flecha inicial
        dot.node('', '', shape='none', width='0', height='0')
        
        # Agregar estados
        for estado in self.estados:
            if estado.es_final:
                dot.node(str(estado), str(estado), shape='doublecircle')
            else:
                dot.node(str(estado), str(estado), shape='circle')
        
        # Flecha inicial
        if self.estado_inicial:
            dot.edge('', str(self.estado_inicial))
        
        # Agregar transiciones
        for estado_origen, transiciones_estado in self.transiciones.items():
            for simbolo, estados_destino in transiciones_estado.items():
                for estado_destino in estados_destino:
                    # Mostrar ε en lugar de 'epsilon' o 'λ'
                    etiqueta = 'ε' if simbolo == 'ε' else simbolo
                    dot.edge(str(estado_origen), str(estado_destino), label=etiqueta)
        
        # Renderizar
        dot.render(nombre_archivo, format='png', cleanup=True)
        print(f"Diagrama guardado como {nombre_archivo}.png")
        return dot

class AlgoritmoKleene:
    """Implementa el algoritmo de Kleene para convertir ER a AFND"""
    
    def __init__(self):
        self.reset_contador_estados()
    
    def reset_contador_estados(self):
        """Reinicia el contador de estados"""
        Estado.contador = 0
    
    def automata_simbolo(self, simbolo):
        """Crea un AFND básico para un símbolo"""
        afnd = AFND()
        
        q_inicial = Estado(es_inicial=True)
        q_final = Estado(es_final=True)
        
        afnd.agregar_estado(q_inicial)
        afnd.agregar_estado(q_final)
        afnd.agregar_transicion(q_inicial, simbolo, q_final)
        
        return afnd
    
    def automata_epsilon(self):
        """Crea un AFND que acepta la cadena vacía (epsilon)"""
        afnd = AFND()
        
        q_inicial = Estado(es_inicial=True, es_final=True)
        afnd.agregar_estado(q_inicial)
        
        return afnd
    
    def concatenacion(self, afnd1, afnd2):
        """Concatenación de dos AFND"""
        afnd_resultado = AFND()
        
        # Agregar todos los estados de ambos autómatas
        for estado in afnd1.estados:
            afnd_resultado.agregar_estado(estado)
        for estado in afnd2.estados:
            afnd_resultado.agregar_estado(estado)
        
        # Copiar transiciones
        for estado_origen, transiciones in afnd1.transiciones.items():
            for simbolo, estados_destino in transiciones.items():
                for estado_destino in estados_destino:
                    afnd_resultado.agregar_transicion(estado_origen, simbolo, estado_destino)
        
        for estado_origen, transiciones in afnd2.transiciones.items():
            for simbolo, estados_destino in transiciones.items():
                for estado_destino in estados_destino:
                    afnd_resultado.agregar_transicion(estado_origen, simbolo, estado_destino)
        
        # Conectar estados finales de afnd1 con inicial de afnd2 mediante epsilon
        for estado_final in afnd1.estados_finales:
            estado_final.es_final = False  # Ya no es final
            afnd_resultado.agregar_transicion(estado_final, 'ε', afnd2.estado_inicial)
        
        # El estado inicial es el de afnd1, los finales son los de afnd2
        afnd_resultado.estado_inicial = afnd1.estado_inicial
        afnd_resultado.estados_finales = afnd2.estados_finales.copy()
        
        return afnd_resultado
    
    def union(self, afnd1, afnd2):
        """Unión de dos AFND"""
        afnd_resultado = AFND()
        
        # Crear nuevos estados inicial y final
        nuevo_inicial = Estado(es_inicial=True)
        nuevo_final = Estado(es_final=True)
        
        afnd_resultado.agregar_estado(nuevo_inicial)
        afnd_resultado.agregar_estado(nuevo_final)
        
        # Agregar estados de ambos autómatas (ya no son iniciales ni finales)
        for estado in afnd1.estados:
            estado.es_inicial = False
            estado.es_final = False
            afnd_resultado.agregar_estado(estado)
        
        for estado in afnd2.estados:
            estado.es_inicial = False
            estado.es_final = False
            afnd_resultado.agregar_estado(estado)
        
        # Copiar transiciones
        for estado_origen, transiciones in afnd1.transiciones.items():
            for simbolo, estados_destino in transiciones.items():
                for estado_destino in estados_destino:
                    afnd_resultado.agregar_transicion(estado_origen, simbolo, estado_destino)
        
        for estado_origen, transiciones in afnd2.transiciones.items():
            for simbolo, estados_destino in transiciones.items():
                for estado_destino in estados_destino:
                    afnd_resultado.agregar_transicion(estado_origen, simbolo, estado_destino)
        
        # Conectar nuevo inicial con iniciales anteriores
        afnd_resultado.agregar_transicion(nuevo_inicial, 'ε', afnd1.estado_inicial)
        afnd_resultado.agregar_transicion(nuevo_inicial, 'ε', afnd2.estado_inicial)
        
        # Conectar finales anteriores con nuevo final
        for estado_final in afnd1.estados_finales:
            afnd_resultado.agregar_transicion(estado_final, 'ε', nuevo_final)
        for estado_final in afnd2.estados_finales:
            afnd_resultado.agregar_transicion(estado_final, 'ε', nuevo_final)
        
        return afnd_resultado
    
    def clausura_kleene(self, afnd):
        """Clausura de Kleene de un AFND"""
        afnd_resultado = AFND()
        
        # Crear nuevos estados inicial y final
        nuevo_inicial = Estado(es_inicial=True)
        nuevo_final = Estado(es_final=True)
        
        afnd_resultado.agregar_estado(nuevo_inicial)
        afnd_resultado.agregar_estado(nuevo_final)
        
        # Agregar estados del autómata original
        for estado in afnd.estados:
            estado.es_inicial = False
            estado.es_final = False
            afnd_resultado.agregar_estado(estado)
        
        # Copiar transiciones
        for estado_origen, transiciones in afnd.transiciones.items():
            for simbolo, estados_destino in transiciones.items():
                for estado_destino in estados_destino:
                    afnd_resultado.agregar_transicion(estado_origen, simbolo, estado_destino)
        
        # Transiciones epsilon para la clausura
        # 1. Del nuevo inicial al inicial original
        afnd_resultado.agregar_transicion(nuevo_inicial, 'ε', afnd.estado_inicial)
        
        # 2. Del nuevo inicial al nuevo final (cadena vacía)
        afnd_resultado.agregar_transicion(nuevo_inicial, 'ε', nuevo_final)
        
        # 3. De los finales originales al nuevo final
        for estado_final in afnd.estados_finales:
            afnd_resultado.agregar_transicion(estado_final, 'ε', nuevo_final)
        
        # 4. De los finales originales al inicial original (repetición)
        for estado_final in afnd.estados_finales:
            afnd_resultado.agregar_transicion(estado_final, 'ε', afnd.estado_inicial)
        
        return afnd_resultado

class ParserER:
    """Parser para expresiones regulares usando el algoritmo de Kleene"""
    
    def __init__(self):
        self.kleene = AlgoritmoKleene()
    
    def parsear(self, expresion):
        """Convierte una expresión regular a AFND"""
        self.kleene.reset_contador_estados()
        expresion = expresion.replace(' ', '')  # Eliminar espacios
        return self._parsear_expresion(expresion)
    
    def _parsear_expresion(self, expr):
        """Parsea una expresión completa (maneja unión con |)"""
        if '|' in expr:
            # Encontrar el | de nivel más alto (no dentro de paréntesis)
            nivel = 0
            for i, char in enumerate(expr):
                if char == '(':
                    nivel += 1
                elif char == ')':
                    nivel -= 1
                elif char == '|' and nivel == 0:
                    # Dividir en este punto
                    izq = expr[:i]
                    der = expr[i+1:]
                    afnd_izq = self._parsear_expresion(izq)
                    afnd_der = self._parsear_expresion(der)
                    return self.kleene.union(afnd_izq, afnd_der)
        
        return self._parsear_concatenacion(expr)
    
    def _parsear_concatenacion(self, expr):
        """Parsea concatenación de términos"""
        if not expr:
            return self.kleene.automata_epsilon()
        
        terminos = self._dividir_en_terminos(expr)
        if len(terminos) == 1:
            return self._parsear_termino(terminos[0])
        
        # Concatenar todos los términos
        resultado = self._parsear_termino(terminos[0])
        for termino in terminos[1:]:
            afnd_termino = self._parsear_termino(termino)
            resultado = self.kleene.concatenacion(resultado, afnd_termino)
        
        return resultado
    
    def _dividir_en_terminos(self, expr):
        """Divide la expresión en términos para concatenación"""
        terminos = []
        i = 0
        while i < len(expr):
            if expr[i] == '(':
                # Encontrar el paréntesis de cierre correspondiente
                nivel = 1
                j = i + 1
                while j < len(expr) and nivel > 0:
                    if expr[j] == '(':
                        nivel += 1
                    elif expr[j] == ')':
                        nivel -= 1
                    j += 1
                
                # Agregar el contenido con paréntesis y posible *
                termino = expr[i:j]
                if j < len(expr) and expr[j] == '*':
                    termino += '*'
                    j += 1
                terminos.append(termino)
                i = j
            else:
                # Carácter simple, posiblemente seguido de *
                termino = expr[i]
                if i + 1 < len(expr) and expr[i + 1] == '*':
                    termino += '*'
                    i += 2
                else:
                    i += 1
                terminos.append(termino)
        
        return terminos
    
    def _parsear_termino(self, termino):
        """Parsea un término individual (símbolo, grupo con paréntesis, o con *)"""
        if termino.endswith('*'):
            # Clausura de Kleene
            sub_termino = termino[:-1]
            if sub_termino.startswith('(') and sub_termino.endswith(')'):
                # Quitar paréntesis externos
                sub_expr = sub_termino[1:-1]
                afnd_base = self._parsear_expresion(sub_expr)
            else:
                afnd_base = self.kleene.automata_simbolo(sub_termino)
            
            return self.kleene.clausura_kleene(afnd_base)
        
        elif termino.startswith('(') and termino.endswith(')'):
            # Grupo con paréntesis
            sub_expr = termino[1:-1]
            return self._parsear_expresion(sub_expr)
        
        else:
            # Símbolo simple
            if termino == 'ε' or termino == '':
                return self.kleene.automata_epsilon()
            return self.kleene.automata_simbolo(termino)

def crear_automata_desde_er(expresion_regular):
    """Función principal para crear AFND desde expresión regular"""
    parser = ParserER()
    try:
        afnd = parser.parsear(expresion_regular)
        print(f"AFND creado para la expresión regular: {expresion_regular}")
        return afnd
    except Exception as e:
        print(f"Error al parsear la expresión regular '{expresion_regular}': {e}")
        return None

# ========================================
# AQUÍ ES DONDE CAMBIAS LA EXPRESIÓN REGULAR
# ========================================

if __name__ == "__main__":
    # MODIFICA ESTA LÍNEA CON TU EXPRESIÓN REGULAR
    expresion_regular = "a*b|c"  # ← CAMBIA AQUÍ POR LA EXPRESIÓN QUE QUIERAS
    
    # Crear y visualizar el autómata
    afnd = crear_automata_desde_er(expresion_regular)
    
    if afnd:
        nombre_archivo = f"afnd_{expresion_regular.replace('|', '_union_').replace('*', '_star_').replace('(', '_').replace(')', '_')}"
        afnd.visualizar(nombre_archivo)
        
        # Mostrar información del autómata
        print(f"\nInformación del autómata:")
        print(f"Estados: {len(afnd.estados)}")
        print(f"Alfabeto: {afnd.alfabeto}")
        print(f"Estado inicial: {afnd.estado_inicial}")
        print(f"Estados finales: {afnd.estados_finales}")
    
    print("\n" + "="*50)
    print("EJEMPLOS DE EXPRESIONES REGULARES QUE PUEDES USAR:")
    print("="*50)
    print("• a*b          - Cero o más 'a' seguido de 'b'")
    print("• (a|b)*       - Cualquier combinación de 'a' y 'b'")
    print("• a(b|c)*d     - 'a' seguido de cualquier combinación de 'b' y 'c', terminando en 'd'")
    print("• (ab)*        - Repetición de 'ab'")
    print("• a|b|c        - 'a' o 'b' o 'c'")
    print("• a*b*c*       - Cero o más 'a', luego cero o más 'b', luego cero o más 'c'")
    print("• (a|b)(c|d)   - ('a' o 'b') seguido de ('c' o 'd')")
    print("="*50)