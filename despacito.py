#!/usr/bin/env python3
# coding: utf-8

"""
COMPILADOR DEL LENGUAJE DE PROGRAMACIÓN DESPACITO

Copyright (c) 2019, Alejandro Santos <alejolp@gmail.com>
Todos los derechos reservados.

Este programa se encuentra publicado bajo la licencia BSD,
disponible en el archivo LICENSE.txt del directorio raíz.

La última versión del código fuente se encuentra en GitHub:

    https://github.com/Despacito-Lang/Despacito

Autor: 
    Alejandro SANTOS <ALEJOLP@gmail.com>
    http://www.ALEJOLP.com.ar/ 

Este compilador se encuentra libre de expresiones regulares.
"""

import os, sys, pprint

# FIXME: letras con ácéntós, letras en otros alfabetos? (динозавр)
LETRAS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITOS = "0123456789"
LETRAS_DIGITOS_ETC = LETRAS + DIGITOS + "_"
SIMBOLOS_PROHIBIDOS = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

ESPACIOS = " \r\n\t"
COMILLA1 = '"'
COMILLA2 = "'"
SIMBOLOS1 = "(),"
OP1 = "=="  # FIXME: buscar otro nombre para esto...
AY = 'ay'   # commentarios

# FIXME: No lo necesito por ahora.
"""
OPERADORES = {
    '(': None,
    ')': None,
    ',': None,
    '==': None,
}
"""

PALABRAS_CLAVE = {
    'despacito': None,      # program
    'mirada': None,         # function
    'suave': None,          # FIXME: ni idea, pero me gusta la palabra
    'conmigo': None,          # :
    'acuerdate': None,      # var
    'bailar': None,         # begin
    'es': None,             # =
    'mientras': None,       # while
    'pasito': None,         # for
    'quiero': None,         # if
    'sino': None,           # elif/else

    'respirar': None,       # pass

    #'nada': None,           # None

    'menor': None,          # <
    'mayor': None,          # >
    #'mayorigual': None,     # >=
    #'menorigual': None,     # <=
    'igual': None,          # ==
    'no': None,             # !

    'mas': None,            # +
    'menos': None,          # -
    'por': None,            # *
    'div': None,            # //
    'mod': None,            # %

    # FIXME: faltan los operadores booleanos y binarios (<<, >>, &, etc)
}

T_PALABRA_CLAVE     = 'T_PALABRA_CLAVE'
T_INDENT            = 'T_INDENT'
T_DEDENT            = 'T_DEDENT'
T_AY                = 'T_AY'
T_NAME              = 'T_NAME'
T_NUMERO            = 'T_NUMERO'
T_CADENA            = 'T_CADENA'
T_SIMBOLO           = 'T_SIMBOLO'
T_OP1               = 'T_PALABRA_CLAVE' # FIXME!
T_NUEVALINEA           = 'T_NUEVALINEA'

MSG_REPETIR_NOMBRES = "No se pueden repetir nombres de miradas, parametros ni variables"
MSG_SIMBOLOS_PROHIBIDOS = "El simbolo no es parte del lenguaje DESPACITO, los operadores son mas, menos, por, div."


class LexerException(Exception):
    pass

class ParserException(Exception):
    pass

def LexerDespacito(f):
    lexemas = []
    pila = []

    for linea in f:
        linea = linea.rstrip(ESPACIOS)
        #print(linea)

        i = 0
        lexemas_linea = []
        inicio_linea = True

        while i < len(linea):
            #print(i)

            if inicio_linea and linea[i] not in ESPACIOS:
                inicio_linea = False

                while len(pila) > 0:
                    lexemas_linea.append((T_DEDENT, None))
                    pila.pop(-1)

            if linea[i] in ESPACIOS:
                j = i
                while i < len(linea) and linea[i] in ESPACIOS:
                    i = i + 1
                if inicio_linea:
                    inicio_linea = False
                    token_tam = i - j
                    if (len(pila) == 0) or (pila[-1] < token_tam):
                        pila.append(token_tam)
                        lexemas_linea.append((T_INDENT, token_tam))
                    elif len(pila) > 0:
                        while len(pila) > 0 and pila[-1] > token_tam:
                            lexemas_linea.append((T_DEDENT, None))
                            pila.pop(-1)

            elif linea[i] in LETRAS:
                j = i
                while i < len(linea) and linea[i] in LETRAS_DIGITOS_ETC:
                    i = i + 1
                token = linea[j:i] # 'amuleto?'
                if token.lower() == AY:
                    # Comentarios empiezan con el simbolo 'ay'
                    # while len(lexemas_linea) and lexemas_linea[-1][0] == T_INDENT:
                    #     lexemas_linea.pop(-1)
                    i = len(linea)
                elif token.lower() in PALABRAS_CLAVE:
                    lexemas_linea.append((T_PALABRA_CLAVE, token.lower())) # , PALABRAS_CLAVE[token.lower()]
                else:
                    lexemas_linea.append((T_NAME, token))

            elif linea[i] in DIGITOS:
                j = i 
                while i < len(linea) and linea[i] in DIGITOS:
                    i = i + 1
                token = linea[j:i]
                lexemas_linea.append((T_NUMERO, token))

            elif linea[i] == COMILLA1 or linea[i] == COMILLA2:
                cual = linea[i]
                j = i
                i = i + 1
                while i < len(linea) and linea[i] != cual:
                    if linea[i] == '\\':
                        i = i + 1
                    i = i + 1
                if i < len(linea) and linea[i] == cual:
                    i = i + 1
                else:
                    assert False
                token = linea[j:i]
                lexemas_linea.append((T_CADENA, token))

            elif linea[i] in SIMBOLOS1:
                token = linea[i]
                lexemas_linea.append((T_SIMBOLO, token))
                i = i + 1

            elif False and linea[i] == OP1[0]:
                # FIXME: Lo ideal seria armar un Trie
                j = i
                k = 0

                while i < len(linea) and k < len(OP1) and linea[i] == OP1[k]:
                    i = i + 1
                    k = k + 1

                if (k) == len(OP1):
                    token = linea[j:i]
                    lexemas_linea.append((T_OP1, token))
                else:
                    assert False, (j, i, k, linea)

            elif linea[i] in SIMBOLOS_PROHIBIDOS:
                assert False, MSG_SIMBOLOS_PROHIBIDOS

            else:
                assert False, (i, linea)

        if len(lexemas_linea) > 0:
            lexemas.extend(lexemas_linea)
            lexemas.append((T_NUEVALINEA, None))

    while len(pila) > 0:
        lexemas.append((T_DEDENT, None))
        pila.pop(-1)

    return lexemas

"""
- FIXME: falta la identacion!

Gramatica (EBNF): 
-----------------

    FIXME!

"""

class ParserDespacito:
    def __init__(self, lexemas):
        self.lexemas = lexemas
        self.pos = 0

    def get_sig_tok(self):
        t = self.lexemas[self.pos]
        self.pos = self.pos + 1
        return t 

    def tok(self, tok_tipo=None, tok_val=None):
        t = self.get_sig_tok()
        if tok_tipo is not None and t[0] != tok_tipo:
            raise ParserException("tok_tipo {} != {}".format(tok_tipo, t[0]))
        if tok_val is not None and t[1] != tok_val:
            raise ParserException("tok_val {} != {}".format(tok_val, t[1]))

        #print("tok: {} {} -> {} {}".format(tok_tipo, tok_val, t[0], t[1]))

        return t

    def parse_programa(self):
        i = self.pos
        L = []
        
        L.append(self.parse_encabezado())

        try:
            while True:
                i = self.pos
                n = self.parse_mirada()
                L.append(n)
        except ParserException:
            self.pos = i

        try:
            while True:
                i = self.pos
                n = self.parse_acuerdate()
                L.append(n)
        except ParserException:
            self.pos = i

        L.append(self.parse_bailar())

        return ('programa', L)

    def parse_encabezado(self):
        i = self.pos
        L = []
        L.append(self.tok(T_PALABRA_CLAVE, 'despacito'))
        L.append(self.tok(T_NAME))
        L.append(self.tok(T_NUEVALINEA))

        return ('encabezado', L)

    def parse_defvariable(self):
        i = self.pos
        L = []
        L.append(self.tok(T_NAME))
        L.append(self.tok(T_PALABRA_CLAVE, 'conmigo'))
        L.append(self.parse_tipodedatos())
        return ('defvariable', L)

    def parse_acuerdate(self):
        i = self.pos
        L = []
        L.append(self.tok(T_PALABRA_CLAVE, 'acuerdate'))
        L.append(self.tok(T_NUEVALINEA))
        L.append(self.tok(T_INDENT))

        try:
            while True:
                i = self.pos
                M = []
                M.append(self.parse_defvariable())
                M.append(self.tok(T_NUEVALINEA))
                L.extend(M)
        except ParserException:
            self.pos = i 

        L.append(self.tok(T_DEDENT))
        return ('acuerdate', L)

    def parse_tipodedatos(self):
        i = self.pos
        L = []
        L.append(self.tok(T_NAME))
        esarreglo = False

        try:
            i = self.pos
            L.append(self.tok(T_SIMBOLO, '('))
            L.append(self.parse_expr())
            L.append(self.tok(T_SIMBOLO, ')'))
            esarreglo = True
        except ParserException:
            self.pos = i 

        if esarreglo:
            return ('tipodedatos_arreglo', L)
        return ('tipodedatos', L)

    def parse_mirada_param(self):
        i = self.pos 
        L = []
        L.append(self.parse_defvariable())
        return ('mirada_param', L)

    def parse_mirada(self):
        i = self.pos 
        L = []
        L.append(self.tok(T_PALABRA_CLAVE, 'mirada'))
        L.append(self.parse_tipodedatos())
        L.append(self.tok(T_NAME))

        try:
            k = 0
            while True:
                i = self.pos
                M = []
                if k > 0:
                    M.append(self.tok(T_SIMBOLO, ','))
                M.append(self.parse_mirada_param())
                L.extend(M)
                k = k + 1
        except ParserException:
            self.pos = i 
        
        L.append(self.tok(T_NUEVALINEA))

        try:
            i = self.pos 
            L.append(self.parse_acuerdate())
        except ParserException:
            self.pos = i 

        L.append(self.parse_bailar())

        return ('mirada', L)

    def parse_bailar(self):
        i = self.pos
        L = []
        L.append(self.tok(T_PALABRA_CLAVE, 'bailar'))
        L.append(self.tok(T_NUEVALINEA))
        L.append(self.tok(T_INDENT))

        try:
            while True:
                i = self.pos
                L.append(self.parse_sentencia())
        except ParserException:
            self.pos = i 

        L.append(self.tok(T_DEDENT))

        return ('bailar', L)

    def parse_expr(self):
        """
        E: E1
        E1: E2 (OP1 E2)*
        E2: E3 (OP2 E3)*
        E3: A1 (OP3 A1)*
        A1: (E) | S A1 | T
        OP1: igual menor mayor
        OP2: mas menos
        OP3: por div mod
        S: + -        # <<- FIXME!
        T: var | num
        """
        i = self.pos
        L = []

        L.append(self.parse_expr_E2())

        try:
            while True:
                i = self.pos
                M = []
                M.append(self.parse_expr_OP1())
                M.append(self.parse_expr_E2())
                L.extend(M)
        except ParserException:
            self.pos = i

        return ('expr', L)

    def parse_expr_E2(self):
        i = self.pos
        L = []

        L.append(self.parse_expr_E3())

        try:
            while True:
                i = self.pos
                M = []
                M.append(self.parse_expr_OP2())
                M.append(self.parse_expr_E3())
                L.extend(M)
        except ParserException:
            self.pos = i

        return ('expr', L)

    def parse_expr_E3(self):
        i = self.pos
        L = []

        L.append(self.parse_expr_A1())

        try:
            while True:
                i = self.pos
                M = []
                M.append(self.parse_expr_OP3())
                M.append(self.parse_expr_A1())
                L.extend(M)
        except ParserException:
            self.pos = i

        return ('expr', L)

    def parse_expr_OP1(self):
        for k in ['igual', 'menor', 'mayor', ]:
            try:
                i = self.pos
                L = []
                L.append(self.tok(T_PALABRA_CLAVE, k))
                return ('expr', L)
            except ParserException:
                self.pos = i

        raise ParserException()

    def parse_expr_OP2(self):
        for k in ['mas', 'menos',]:
            try:
                i = self.pos
                L = []
                L.append(self.tok(T_PALABRA_CLAVE, k))
                return ('expr', L)
            except ParserException:
                self.pos = i

        raise ParserException()

    def parse_expr_OP3(self):
        for k in ['por', 'div', 'mod']:
            try:
                i = self.pos
                L = []
                L.append(self.tok(T_PALABRA_CLAVE, k))
                return ('expr', L)
            except ParserException:
                self.pos = i

        raise ParserException()

    def parse_expr_A1(self):
        try:
            i = self.pos 
            L = []
            L.append(self.tok(T_SIMBOLO, '('))
            L.append(self.parse_expr())
            L.append(self.tok(T_SIMBOLO, ')'))
            return ('expr', L)
        except ParserException:
            self.pos = i

        try:
            i = self.pos 
            L = []
            L.append(self.parse_expr_T())
            return ('expr', L)
        except ParserException:
            self.pos = i

        raise ParserException()

    def parse_expr_T(self):
        try:
            i = self.pos
            L = []
            L.append(self.parse_cadena())
            return ('expr', L)
        except ParserException:
            self.pos = i

        try:
            i = self.pos
            L = []
            L.append(self.parse_numero())
            return ('expr', L)
        except ParserException:
            self.pos = i

        try:
            i = self.pos
            L = []
            L.append(self.parse_llamada())
            return ('expr', L)
        except ParserException:
            self.pos = i

        try:
            i = self.pos
            L = []
            L.append(self.parse_variable())
            return ('expr', L)
        except ParserException:
            self.pos = i

        raise ParserException()

    def parse_sentencia(self):
        """
        sentencia: asignacion | expr 
        """

        try:
            i = self.pos
            L = []
            L.append(self.parse_mientras())
            #L.append(self.tok(T_NUEVALINEA))
            return ('sentencia', L)
        except ParserException:
            self.pos = i

        try:
            i = self.pos
            L = []
            L.append(self.parse_pasito())
            #L.append(self.tok(T_NUEVALINEA))
            return ('sentencia', L)
        except ParserException:
            self.pos = i

        try:
            i = self.pos
            L = []
            L.append(self.parse_quiero())
            #L.append(self.tok(T_NUEVALINEA))
            return ('sentencia', L)
        except ParserException:
            self.pos = i

        try:
            i = self.pos
            L = []
            L.append(self.parse_asignacion())
            L.append(self.tok(T_NUEVALINEA))
            return ('sentencia', L)
        except ParserException:
            self.pos = i

        try:
            i = self.pos 
            L = []
            L.append(self.parse_expr())
            L.append(self.tok(T_NUEVALINEA))
            return ('sentencia', L)
        except ParserException:
            self.pos = i

        try:
            i = self.pos 
            L = []
            L.append(self.parse_respirar())
            L.append(self.tok(T_NUEVALINEA))
            return ('sentencia', L)
        except ParserException:
            self.pos = i

        try:
            i = self.pos 
            L = []
            L.append(self.tok(T_NUEVALINEA))
            return ('sentencia', L)
        except ParserException:
            self.pos = i

        raise ParserException()

    def parse_respirar(self):
        i = self.pos 
        L = []
        L.append(self.tok(T_PALABRA_CLAVE, 'respirar'))
        return ('respirar', L)

    def parse_mientras(self):
        i = self.pos
        L = []
        L.append(self.tok(T_PALABRA_CLAVE, 'mientras'))
        L.append(self.parse_expr())
        L.append(self.tok(T_NUEVALINEA))
        L.append(self.tok(T_INDENT))

        try:
            while True:
                i = self.pos
                L.append(self.parse_sentencia())
        except ParserException:
            self.pos = i 

        L.append(self.tok(T_DEDENT))
        return ('mientras', L)

    def parse_pasito(self):
        i = self.pos
        L = []
        L.append(self.tok(T_PALABRA_CLAVE, 'pasito'))
        L.append(self.parse_expr())
        L.append(self.tok(T_NUEVALINEA))
        L.append(self.tok(T_INDENT))

        try:
            while True:
                i = self.pos
                L.append(self.parse_sentencia())
        except ParserException:
            self.pos = i 

        L.append(self.tok(T_DEDENT))
        return ('pasito', L)

    def parse_quiero(self):
        i = self.pos
        L = []
        L.append(self.tok(T_PALABRA_CLAVE, 'quiero'))
        L.append(self.parse_expr())
        L.append(self.tok(T_NUEVALINEA))
        L.append(self.tok(T_INDENT))

        try:
            while True:
                i = self.pos
                L.append(self.parse_sentencia())
        except ParserException:
            self.pos = i 

        L.append(self.tok(T_DEDENT))

        try:
            k = 0
            while True:
                i = self.pos
                L.append(self.parse_sino_expr())
                k = k + 1
        except ParserException:
            self.pos = i

        try:
            i = self.pos
            L.append(self.parse_sino())
        except ParserException:
            self.pos = i

        return ('quiero', L)

    def parse_sino_expr(self):
        i = self.pos
        L = []
        L.append(self.tok(T_PALABRA_CLAVE, 'sino'))
        L.append(self.parse_expr())
        L.append(self.tok(T_NUEVALINEA))
        L.append(self.tok(T_INDENT))

        try:
            while True:
                i = self.pos
                L.append(self.parse_sentencia())
        except ParserException:
            self.pos = i 

        L.append(self.tok(T_DEDENT))
        return ('sino_expr', L)

    def parse_sino(self):
        i = self.pos
        L = []
        L.append(self.tok(T_PALABRA_CLAVE, 'sino'))
        L.append(self.tok(T_NUEVALINEA))
        L.append(self.tok(T_INDENT))

        try:
            while True:
                i = self.pos
                L.append(self.parse_sentencia())
        except ParserException:
            self.pos = i 

        L.append(self.tok(T_DEDENT))
        return ('sino', L)

    def parse_cadena(self):
        i = self.pos
        L = []
        L.append(self.tok(T_CADENA))
        return ('cadena', L)

    def parse_numero(self):
        i = self.pos 
        L = []
        L.append(self.tok(T_NUMERO))
        return ('numero', L)

    def parse_variable(self):
        i = self.pos 
        L = []
        L.append(self.tok(T_NAME))
        return ('variable', L)

    def parse_asignacion(self):
        i = self.pos 
        L = []

        # FIXME: No es una 'llamada' sino asignacion de una posicion de arreglo

        try:
            i = self.pos 
            L.append(self.parse_llamada(1))
        except ParserException:
            self.pos = i 

        if len(L) == 0:
            L.append(self.tok(T_NAME))

        L.append(self.tok(T_PALABRA_CLAVE, 'es'))
        L.append(self.parse_expr())

        return ('asignacion', L)

    def parse_llamada(self, max_parametros=10000):
        i = self.pos
        L = []
        L.append(self.tok(T_NAME))
        L.append(self.tok(T_SIMBOLO, '('))

        try:
            k = 0
            while k < max_parametros:
                i = self.pos
                M = []
                if k > 0:
                    M.append(self.tok(T_SIMBOLO, ','))
                M.append(self.parse_expr())
                L.extend(M)
                k = k + 1
        except ParserException:
            self.pos = i 

        L.append(self.tok(T_SIMBOLO, ')'))

        return ('llamada', L)

    def parse(self):
        self.pos = 0
        n = self.parse_programa()
        if self.pos != len(self.lexemas):
            raise ParserException(self.lexemas[self.pos])
        return n

TABLA_K_E = {
    'respirar': '/* respirar */',
    'mas': '+',
    'menos': '-',
    'por': '*',
    'div': '/',
    'mod': '%',

    'es': ' = ',

    'menor': '<',
    'mayor': '>',
    'igual': '==',

    'pasito': '',
    'mientras': '',
    'bailar': '',
    'acuerdate': '',
    'mirada': '',
}

class PilaDeDicts:
    def __init__(self):
        self.pila = []
        # FIXME: Para que sea mas prolijo hay que agregar un
        # dict con un contador de keys (k -> n). Quizas tambien
        # un stack por key? No se, la pila no es muy profunda.

    def push(self, elem):
        #pprint.pprint(('pila.push', elem))

        assert type(elem) is dict
        self.pila.append(elem)

    def pop(self):
        #pprint.pprint(('pila.pop', self.pila[-1]))

        return self.pila.pop(-1)

    def get(self, key, default=None):
        for d in reversed(self.pila):
            if key in d:
                return d[key]
        return default

    def __contains__(self, key):
        for d in reversed(self.pila):
            if key in d:
                return True
        return False

class CompiladorDespacito:
    def __init__(self, nodo):
        self.nodo = nodo
        self.idx = 0
        self.pila_de_nodos = []
        self.pila_de_nombres = PilaDeDicts()
        self.lista_de_encabezado = []
        # PROFundidad
        self.prof = 0

    def compilar(self):
        A = self.visitar(self.nodo)
        S = '\n'.join(self.lista_de_encabezado)
        return S + '\n' * 2 + A

    def prox_temp_var_nombre(self):
        i = self.idx
        self.idx += 1
        return "despacito_tmp_{}".format(i) 

    def prox_temp_arreglo_nombre(self, tipodedatos, tamano):
        i = self.idx
        self.idx += 1
        return "despacito_arr_{0}_{1}".format(tipodedatos, i) 

    def visitar_hijos(self, nodo, inicio=0):
        self.pila_de_nodos.append(nodo)

        S = ""
        for i in range(inicio, len(nodo[1])):
            S = S + self.visitar(nodo[1][i])
        S = S + ""

        self.pila_de_nodos.pop(-1)
        return S

    def visitar(self, nodo):
        assert type(nodo) is tuple

        if nodo[0] == T_NUEVALINEA:
            if self.pila_de_nodos[-1][0] in ['sentencia', 'acuerdate']:
                return ";\n"
            return "\n"
            #return "/*W:{} */\n".format((self.pila_de_nodos[-1][0]))
        elif nodo[0] == T_INDENT:
            self.prof = self.prof + 1
            return ""
        elif nodo[0] == T_DEDENT:
            self.prof = self.prof - 1
            return ""
        elif nodo[0] == T_NUMERO:
            return nodo[1]
        elif nodo[0] == T_NAME:
            if nodo[1] == 'firmar':
                return 'printf'
            return nodo[1]
        elif nodo[0] == T_SIMBOLO:
            return nodo[1]
        elif nodo[0] == T_CADENA:
            return nodo[1]
        elif nodo[0] == T_PALABRA_CLAVE:
            if nodo[1] in TABLA_K_E:
                return TABLA_K_E[nodo[1]]
            else:
                return "/* YYY {} */".format(nodo[1])
        elif nodo[0] == 'programa':
            return self.visitar_hijos(nodo)
        elif nodo[0] == 'encabezado':
            S = """/* programa despacito: {0} */
#include <stdio.h>
#include <stdlib.h>

typedef void nada;
typedef int entero;

""".format(
                nodo[1][1][1])
            self.lista_de_encabezado.append(S)
            return ""
        elif nodo[0] == 'bailar':
            if (self.pila_de_nodos[-1][0] == 'programa'):
                S = "int main(int argc, char** argv) {\n"
                S = S + (" " * self.prof) + "(void)argc; (void)argv;"
            else:
                S = "\n".format()

            for i in range(len(nodo[1])): 
                S = S + self.visitar(nodo[1][i])

            if len(self.pila_de_nodos) == 0:
                S = S + (" " * self.prof) + "return 0;\n"
            elif 'mirada' in self.pila_de_nombres:
                mirada = self.pila_de_nombres.get('mirada')
                if mirada['tipodedatos'] != 'nada':
                    S = S + (" " * self.prof) + "return {0};\n".format(mirada['tmp_var_func'])
            S = S + "}\n"
            return S
        elif nodo[0] == 'sentencia':
            S = (" " * self.prof)
            return S + self.visitar_hijos(nodo) 
        elif nodo[0] == 'pasito':
            E = self.visitar(nodo[1][1])
            V = self.prox_temp_var_nombre()

            S = "for (int {0} = {1}; {0} > 0; --{0}) {{\n".format(V, E)
            for i in range(3, len(nodo[1])): 
                S = S + self.visitar(nodo[1][i])
            S = S + (" " * self.prof) + "}\n"
            return S
        elif nodo[0] == 'mientras':
            E = self.visitar(nodo[1][1])

            S = "while ({0}) {{\n".format(E)
            for i in range(3, len(nodo[1])): 
                S = S + self.visitar(nodo[1][i])
            S = S + (" " * self.prof) + "}\n"
            return S
        elif nodo[0] == 'mirada':
            self.pila_de_nodos.append(nodo)

            tipodedatos = self.visitar(nodo[1][1])
            nombre = self.visitar(nodo[1][2])

            assert nombre not in self.pila_de_nombres, MSG_REPETIR_NOMBRES
            assert 'mirada' not in self.pila_de_nombres

            self.pila_de_nombres.push({
                nombre: {
                    'tipo': 'mirada',
                }})

            params = []
            i = 3
            while nodo[1][i][0] != T_NUEVALINEA:
                params.append(self.visitar(nodo[1][i]))
                i = i + 1
            params_str = ', '.join(params)

            mirada = {'nombre': nombre,
                    'tipodedatos': tipodedatos,
                    'tmp_var_func': self.prox_temp_var_nombre(),
                    'params': params,
                    'locales_cant': 0}

            self.pila_de_nombres.push({
                'mirada': mirada})

            S = "{} {} ({}) {{ \n".format(tipodedatos, nombre, params_str)
            
            if tipodedatos != 'nada':
                S = S + "{} {} = 0;".format(tipodedatos, mirada['tmp_var_func'])

            while i < len(nodo[1]): # FIXME: aca hay solamente tres elementos restantes
                S = S + self.visitar(nodo[1][i])
                i = i + 1

            locales_cant = self.pila_de_nombres.get('mirada')['locales_cant']

            # pop del nodo 'mirada'
            self.pila_de_nodos.pop(-1)

            # pop de cada parametro y var local de la mirada, 
            # se les hizo push en defvariable

            for k in range(len(params)):
                self.pila_de_nombres.pop()

            for k in range(locales_cant):
                self.pila_de_nombres.pop()

            self.pila_de_nombres.pop()

            return S
        elif nodo[0] == 'quiero':
            E = self.visitar(nodo[1][1])
            S = "if ({0}) {{\n".format(E)

            i = 2
            while i < len(nodo[1]):
                if nodo[1][i][0] != T_NUEVALINEA:
                    S = S + self.visitar(nodo[1][i])
                i = i + 1

            S = S + (" " * self.prof) + "}\n"
            return S 
        elif nodo[0] == 'sino_expr':
            E = self.visitar(nodo[1][1])
            S = (" " * self.prof) + "}} else if ({0}) {{\n".format(E)

            i = 2
            while i < len(nodo[1]):
                if nodo[1][i][0] != T_NUEVALINEA:
                    S = S + self.visitar(nodo[1][i])
                i = i + 1

            #S = S + "}\n"
            return S 
        elif nodo[0] == 'sino':
            S = (" " * self.prof) + "}} else {{\n".format()

            i = 1
            while i < len(nodo[1]):
                if nodo[1][i][0] != T_NUEVALINEA:
                    S = S + self.visitar(nodo[1][i])
                i = i + 1

            #S = S + "}\n"
            return S 
        elif nodo[0] == 'numero':
            return "({0})".format(self.visitar_hijos(nodo))
        elif nodo[0] == 'cadena':
            return self.visitar_hijos(nodo)
        elif nodo[0] == 'expr':
            if len(nodo[1]) > 1:
                return "({})".format(self.visitar_hijos(nodo))
            return "{}".format(self.visitar_hijos(nodo))
        elif nodo[0] == 'llamada':
            nombre = self.visitar(nodo[1][0]) # T_NAME
            a = self.pila_de_nombres.get(nombre)

            #pprint.pprint((nombre, a))

            if a is not None and a['tipo'] != 'mirada':
                assert len(nodo[1]) == 4
                E = self.visitar(nodo[1][2])

                S = "{0}[{1}]".format(nombre, E)
                return S 
            else:
                return self.visitar_hijos(nodo)
        elif nodo[0] == 'asignacion':
            assert len(nodo[1]) == 3
            if nodo[1][0][0] == T_NAME:
                nombre = self.visitar(nodo[1][0])
                if 'mirada' in self.pila_de_nombres:
                    mirada = self.pila_de_nombres.get('mirada')
                    if nombre == mirada['nombre']:
                        S = "{0} = {1}".format(
                            mirada['tmp_var_func'],
                            self.visitar(nodo[1][2]))
                        return S
            return self.visitar_hijos(nodo)
        elif nodo[0] == 'variable':
            return self.visitar_hijos(nodo)
        elif nodo[0] == 'mirada_param':
            return self.visitar_hijos(nodo)
        elif nodo[0] == 'acuerdate':
            S = self.visitar_hijos(nodo, 2)
            return S
        elif nodo[0] == 'defvariable':
            nombre = self.visitar(nodo[1][0])
            tipodedatos = self.visitar(nodo[1][2])
            nodo_tipodedatos = None

            esarreglo = (nodo[1][2][0] == 'tipodedatos_arreglo')
            esparam = (self.pila_de_nodos[-1][0] == 'mirada_param')

            # pprint.pprint((nombre, esparam))

            assert nombre not in self.pila_de_nombres, MSG_REPETIR_NOMBRES

            self.pila_de_nombres.push({
                nombre: {
                    'tipo': 'defvariable',
                    'tipodedatos': tipodedatos,
                    'esarreglo': esarreglo,
                }})

            # FIXME?
            if 'mirada' in self.pila_de_nombres: # and 'acuerdate' in self.pila_de_nombres:
                mirada = self.pila_de_nombres.get('mirada')
                mirada['locales_cant'] = mirada['locales_cant'] + 1

            if esparam:
                if esarreglo:
                    return "{0} {1}".format(tipodedatos, nombre)
                else:
                    return "{0} {1}".format(tipodedatos, nombre)
            else:
                if esarreglo:
                    return "{0} {1} = {{0}}".format(tipodedatos, nombre)
                else:
                    return "{0} {1} = 0".format(tipodedatos, nombre)
        elif nodo[0] == 'tipodedatos':
            return self.visitar_hijos(nodo)
        elif nodo[0] == 'tipodedatos_arreglo':
            assert len(nodo[1]) == 4, len(nodo[1])

            tipodedatos_real = self.visitar(nodo[1][0])
            tamanoarray = self.visitar(nodo[1][2])
            tipodedatos_temp = self.prox_temp_arreglo_nombre(
                tipodedatos_real, tamanoarray)

            self.lista_de_encabezado.append(
                "typedef {0} {1} [{2}];".format(
                tipodedatos_real,
                tipodedatos_temp,
                tamanoarray))

            return "{0} /* {1} */".format(tipodedatos_temp, tamanoarray)
        elif nodo[0] == 'respirar':
            return '/* respirar */'
        else:
            return """/* FIXME nodo desconocido: {} */\n""".format(
                nodo[0])

def main(argv):
    debug = False
    nombre_de_archivo = argv[1]

    with open(nombre_de_archivo, 'r') as f:
        lexemas = LexerDespacito(f)

    if debug:
        pprint.pprint(lexemas)

    pp = ParserDespacito(lexemas)
    xx = pp.parse()

    if debug:
        pprint.pprint(xx)

    yy = CompiladorDespacito(xx)
    zz = yy.compilar()
    print(zz)

if __name__ == '__main__':
    main(sys.argv)
