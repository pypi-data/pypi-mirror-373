#!/usr/bin/env python3
from builtins import input as py_input
from builtins import print as py_print
from locale import Error, LC_ALL, setlocale
from shutil import get_terminal_size
from os.path import realpath
from pathlib import Path
from sys import argv, exit, __stdout__, stdout
from re import compile, match, search, split, sub
from warnings import filterwarnings
from time import sleep

def silence_deprecation_warnings():
    """Desactiva DeprecationWarning y FutureWarning en todo el programa."""
    filterwarnings("ignore", category=DeprecationWarning)
    filterwarnings("ignore", category=FutureWarning)

def language ():
    try:
        return setlocale(LC_ALL, '')[:2]
    except Error as e:
        return 'en'

def parse_bbcode(string, is_escape_square=True):
    pattern = (
        r'(\[\[|\]\]|'             # corchete escapado
        r'\[-?\d+(?:,-?\d+)?\]|'   # [n] o [n,m]
        r'\[,?-?\d+\]|'            # [,m] o [, -m]
        r'\[\]|'                   # []
        r'\[/?\w+\])'              # [tag] o [/tag]
    )
    tokens = split(pattern, string)
    result = []

    for token in tokens:
        if not token:
            continue
        if token == '[[' and is_escape_square:
            result.append('[')
        elif token == ']]' and is_escape_square:
            result.append(']')
        else:
            result.append(token)

    return result

def list_bbcode_to_ansi(array):
    STYLE_MAP = {
        'b': ('1', '22'), 'd': ('2', '22'), 'i': ('3', '23'),
        'u': ('4', '24'), 'k': ('5', '25'), 'r': ('7', '27'),
        'h': ('8', '28'), 's': ('9', '29')
    }

    for i, e in enumerate(array):
        arrow = e[0] + e[-1]
        if len(e) > 1:
            is_close = 1 if e[1] == '/' else 0
        if arrow == '[]':
            if e in ('[]', '[/]'):
                array[i] = '\x1b[0m'
            while True:
                if search(r'\[/?[bdiukrhs]+\]', e):
                    style = '\x1b['
                    for f in e[1+is_close:-1]:
                        style = f'{style}{STYLE_MAP[f][is_close]};'
                    array[i] = style[:-1] + 'm'
                    break
                elif any(_flag in e for _flag in list('bdiukrhs')):
                    style = ''
                    for char in e[1+is_close:-1]:
                        if char in 'bdiukrhs':
                            style = style + char
                    e = f'[{style}]' if is_close == 0 else f'[/{style}]'
                elif search(r'\[(-?\d+)?(,-?\d+)?\]', e):
                    colors = e[1:-1].split(',')
                    color = [int(x) if x.isdecimal() else x for x in colors]
                    if (search(r'\[-?\d+,-?\d+\]', e)):
                        fg, bg = color
                        try:
                            if fg in range(256) and bg in range(256):
                                array[i] = f'\x1b[38;5;{fg};48;5;{bg}m'
                            elif not fg in range(256) and bg in range(256):
                                array[i] = f'\x1b[39;48;5;{bg}m'
                            elif fg in range(256) and not bg in range(256):
                                array[i] = f'\x1b[38;5;{fg};49m'
                            else:
                                array[i] = '\x1b[39;49m'
                        except TypeError:
                            pass
                    if search(r'\[-?\d+\]', e):
                        fg = int(color[0])
                        array[i] = (
                                f'\x1b[38;5;{fg}m' if -1 < fg < 256
                                else '\x1b[39m'
                                )
                    if search(r'\[,-?\d+\]', e):
                        bg = int(color[1])
                        array[i] = (
                                f'\x1b[48;5;{bg}m' if -1 < bg < 256
                                else '\x1b[49m'
                                )
                    break
                elif not all(_flag in e for _flag in list('bdiukrhs')):
                    array[i] = ''
                    break
                else:
                    break
    return array

def group_ansi_codes(element_list):
    """
    Junta los códigos de escape ANSI que están uno al lado del otro en una lista.

    Args:
        element_list (list): Una lista de strings.

    Returns:
        list: Una nueva lista con los códigos ANSI adyacentes agrupados.
    """
    # Este es el patrón para detectar un código ANSI, que empieza con '\x1b[' y termina con 'm'.
    # Lo compilamos para que sea más rápido.
    ansi_pattern = compile(r'\x1b\[.*?m')

    new_list = []
    # Usamos un set para guardar los índices de los elementos que ya agrupamos.
    # Así, evitamos procesarlos dos veces.
    processed_indices = set()

    # Recorremos la lista con un índice para tener control.
    for i, current_element in enumerate(element_list):
        # Si este elemento ya lo procesamos en una agrupación anterior, lo saltamos.
        if i in processed_indices:
            continue

        # Chequeamos si el elemento actual es un código ANSI.
        if ansi_pattern.match(current_element):
            # Si es un código, lo guardamos y buscamos los siguientes.
            grouped_code = current_element
            # Iteramos desde el siguiente elemento para encontrar más códigos ANSI.
            for j in range(i + 1, len(element_list)):
                if ansi_pattern.match(element_list[j]):
                    # Si el siguiente también es un código, lo concatenamos y guardamos su índice.
                    grouped_code += element_list[j]
                    processed_indices.add(j)
                else:
                    # Si encontramos un elemento que no es ANSI, rompemos el bucle interno.
                    break
            # Agregamos el código agrupado a la nueva lista.
            new_list.append(grouped_code)
        else:
            # Si no es un código ANSI, lo agregamos tal cual a la nueva lista.
            new_list.append(current_element)

    is_ansi = lambda s: search(r'\x1b\[[0-9;]+m', s)
    new_list = (
            [x.replace('m\x1b[', ';') if is_ansi(x) else x for x in new_list]
            )

    return new_list

def bb_to_ansi (string:str, option:str='', separate:str='',
                is_escape_square=False):
    array = parse_bbcode(string, is_escape_square)
    array = list_bbcode_to_ansi(array)
    #array = group_ansi_codes(array)
    string = separate.join(array)
    return flip(string, option) if len(option) > 0 else string

def flip (string='', option=''):
    """
    Toma un string con códigos de escape ANSI y lo retorna modificado
    según la opción, conservando los códigos de escape.
    Los caracteres de control (como tabuladores o saltos de línea) son tratados como espacios
    para la lógica de capitalización en 'title' y 'capitalize'.

    Args:
        string (str): El string de entrada.
        option (str): La opción de formato ('capitalize', 'title', o 'upper').

    Returns:
        str: El string modificado con los códigos de escape intactos.
    """

    LANG = language()

    # Función para invertir entre minúsculas y mayúsculas.
    invert = lambda s: s.upper() if s.islower() else s.lower()

    err = {
            'es': (f'{option} es opción incorrecta.\n'
            '¿Quiso decir: '
            '\'c\', \'i\', \'l\', \'t\', \'u\', \'capital\', \'capitalize\', '
            '\'inverti\', \'lower\', \'title\' o \'upper\'?'),
            'en': (f'Unknown option {option}.\n'
            'Did you mean one of: '
            '\'c\', \'i\', \'l\', \'t\', \'u\', \'capital\', \'capitalize\', '
            '\'inverti\', \'lower\', \'title\' or \'upper\'?'),
            }

    LANG = 'en' if not LANG in err.keys() else LANG

    option = option.lower()

    option = 'capitalize' if option == 'capital' else option

    if len(option) == 1 or option == 'tuple':
        options = {
                'c': 'capitalize',
                'i': 'invert',
                'l': 'lower',
                't': 'title',
                'u': 'upper'
                }
        try:
            option = options[option]
        except KeyError:
            pass

    # Patrón para dividir el string en segmentos de texto, códigos ANSI y caracteres de espacio.
    # Captura los códigos ANSI (\x1b[...m) y cualquier carácter de espacio (\s+ para uno o más).
    p = r'(\x1b\[.*?m|\s+)'

    # Divide el string. split mantiene los delimitadores si están en un grupo de captura.
    # Esto nos da una lista como [texto, delimitador, texto, delimitador, ...]
    segs = split(p, string) # Usamos 'string' aquí

    # Filtra las cadenas vacías que puedan resultar de la división (ej., si la cadena empieza/termina con un delimitador)
    segs = [seg for seg in segs if seg is not None and seg != '']

    res_list = []

    if option == 'upper': # Usamos 'option' aquí
        # Para 'upper', simplemente convertimos los segmentos de texto a mayúsculas.
        for seg in segs:
            # Si es un código ANSI o un espacio en blanco, lo añadimos tal cual.
            # De lo contrario, convertimos el texto a mayúsculas.
            if match(p, seg):
                res_list.append(seg)
            else:
                res_list.append(seg.upper())
        return "".join(res_list)

    elif option == 'capitalize': # Usamos 'option' aquí
        # Para 'capitalize', obtenemos el texto "puro" (sin ANSI, sin espacios como separadores),
        # le aplicamos .capitalize() y luego mapeamos los cambios de vuelta.

        # Construye una cadena que contenga solo los caracteres de texto reales, en su orden original.
        pure_t = ''.join([seg for seg in segs if not match(p, seg)])
        for i, char in enumerate(pure_t):
            if char.isalpha():
                trans_pure_t = (
                    pure_t[:i] + char.upper() + pure_t[i + 1:].lower()
                )
                break

        curr_pure_t_idx = 0
        for seg in segs:
            if match(p, seg):
                res_list.append(seg) # Mantiene ANSI/espacios en blanco tal cual
            else: # Es un segmento de texto
                seg_len = len(seg)
                # Toma la porción correspondiente de la cadena de texto pura transformada
                res_list.append(
                    trans_pure_t[curr_pure_t_idx : curr_pure_t_idx + seg_len]
                )
                curr_pure_t_idx += seg_len
        return "".join(res_list)

    elif option == 'title': # Usamos 'option' aquí
        """
        Emula str.title() pero:
          - Preserva códigos ANSI intactos.
          - Usa como separadores cualquier caracter no alfabético (excepto ANSI).
        """
        # Dividimos el string en bloques: texto normal y códigos ANSI
        ansi_pattern = compile(r'\x1b\[[0-9;]*m')
        parts = ansi_pattern.split(string)
        ansi_codes = ansi_pattern.findall(string)

        result = []
        for i, part in enumerate(parts):
            word = []
            capitalize_next = True

            for char in part:
                if char.isalpha():
                    if capitalize_next:
                        word.append(char.upper())
                        capitalize_next = False
                    else:
                        word.append(char.lower())
                else:
                    word.append(char)
                    capitalize_next = True  # nuevo separador → próxima letra va en mayúscula
            result.append("".join(word))

            # reinyectar el ANSI correspondiente (si existe)
            if i < len(ansi_codes):
                result.append(ansi_codes[i])

        return "".join(result)

    elif option == 'invert':
        # Para 'invert', obtenemos el texto "puro" (sin ANSI, sin espacios como separadores),
        # le aplicamos la función invert a cada carácter y luego mapeamos los cambios de vuelta.

        # Construye una cadena que contenga solo los caracteres de texto reales.
        pure_t = "".join([seg for seg in segs if not match(p, seg)])

        # Aplica la función invert a cada carácter del texto puro
        trans_pure_t_chars = [invert(char) for char in pure_t]
        trans_pure_t = "".join(trans_pure_t_chars)

        curr_pure_t_idx = 0
        for seg in segs: # ¡Este bucle faltaba!
            if match(p, seg):
                res_list.append(seg) # Mantiene ANSI/espacios en blanco tal cual
            else: # Es un segmento de texto
                seg_len = len(seg)
                # Toma la porción correspondiente de la cadena de texto pura transformada
                res_list.append(
                    trans_pure_t[curr_pure_t_idx : curr_pure_t_idx + seg_len]
                )
                curr_pure_t_idx += seg_len
        return "".join(res_list)

    elif option == 'lower':
        return string.lower()

    elif option == 'tuple':
        options['c1'] = 'capital'
        return options.values()

    else:
        raise ValueError(err[LANG])

def ansi_wrap (string:str, width:int=None):
    # Separa ANSI, tabs, espacios y saltos de línea explícitos
    if width is None:
        from shutil import get_terminal_size
        width = get_terminal_size().columns

    # patrones
    pattern = compile(r'(\x1b\[[0-9;]*m|\t| +|\n)')
    p_ansi = compile(r'\x1b\[[0-9;]*m')
    p_spaces = compile(r'\s+')
    # detecta fondos, con o sin foreground: 48;5;Y o 38;5;X;48;5;Y
    p_bg = compile(
        r'(?:\x1b\[[0-9;]*38;5;\d+;48;5;\d+m|\x1b\[[0-9;]*48;5;\d+m)'
    )

    parts = [p for p in pattern.split(string) if p != '']

    new_list = ['']
    c = 0  # contador de ancho visible
    active_bg = ''  # último fondo activo

    for e in parts:
        if p_ansi.fullmatch(e):
            # si es código ANSI
            if p_bg.fullmatch(e):
                active_bg = e
            elif e == '\x1b[49m':  # reset de fondo
                active_bg = ''
            new_list[-1] += e
            continue

        if e == '\t':
            ws = 8 - (c % 8)
            if c + ws > width:
                if active_bg:
                    new_list[-1] += '\x1b[49m'
                new_list.append(active_bg)
                c = 0
            new_list[-1] += ' ' * ws
            c += ws
            continue

        if e == '\n':
            if active_bg:
                new_list[-1] += '\x1b[49m'
            new_list.append(active_bg)
            c = 0
            continue

        if p_spaces.fullmatch(e):
            if c + len(e) > width:
                if active_bg:
                    new_list[-1] += '\x1b[49m'
                new_list.append(active_bg)
                c = 0
            else:
                new_list[-1] += e
                c += len(e)
            continue

        # palabra
        if c + len(e) > width:
            if active_bg:
                new_list[-1] += '\x1b[49m'
            new_list.append(active_bg)
            c = 0
        new_list[-1] += e
        c += len(e)

        # revisar si la palabra termina con un background
        if p_bg.search(e[-20:]):  # chequear últimos 20 chars por seguridad
            match = p_bg.search(e[-20:])
            if match:
                active_bg = match.group()

    # limpiar línea vacía final
    if new_list and new_list[-1] == '':
        new_list = new_list[:-1]

    # quitar TODOS los espacios finales de cada línea,
    # preservando los códigos ANSI al final
    cleaned = []
    for line in new_list:
        line = sub(r' +((?:\x1b\[[0-9;]*m)*)$', r'\1', line)
        cleaned.append(line)

    return '\n'.join(cleaned)

def parse_cmd (command=argv):
    FLAGS = {
        'a': '--ansi',
        'd': r'--delay=[0-9]+(\.[0-9]+)?',
        'h': '--help',
        'n': '--no-new-line',
        'r': '--reset',
        'v': '--version',
        'w': '--wrap'
    }
    ptn_tm = r'[0-9]+(\.[0-9]+)?'

    dict_flags = FLAGS.copy()
    del(dict_flags['d'])

    is_flag = True
    flags_key = dict_flags.keys()
    options = dict_flags.values()
    #pattern_flags = r'-[{}]+'.format(''.join(flags_key))

    flags = []
    text = []
    exist_delay = False
    skip_next = False

    for i, e in  enumerate(command[:]):
        if i == 0:
            continue
        if is_flag:
            if e in options:
                flags.append(e)
            if skip_next:
                skip_next = False
                continue
            elif len(e) > 1 and set(e[1:]).issubset(flags_key):
                for f in e[1:]:
                    flags.append(FLAGS[f])
            elif (
                (match(FLAGS['d'], e) or e == '-d' and i+1 < len(command)
                  and match(ptn_tm, command[i+1])) and not exist_delay
            ):
                if match(FLAGS['d'], e):
                    flags.append(e)
                    exist_delay = True
                elif (
                    e == '-d' and i+1 < len(command) and
                    match(ptn_tm, command[i+1])
                ):
                    flags.append(f'--delay={command[i+1]}')
                    exist_delay = True
                    skip_next = True
            else:
                text.append(e)
                is_flag = False
        else:
            text.append(e)

    flags = sorted(list(set(flags)))

    return (Path(argv[0]).stem, tuple(flags), ' '.join(text))

def is_active_styles(string):
    ANSI_PATTERN = compile(r'\x1b\[([\d;]*)m')

    STATE = {
        'bold': False, 'dim': False, 'italic': False, 'underline': False,
        'blink': False, 'reverse': False, 'hidden': False,
        'strikethrough': False, 'fg': None, 'bg': None,
    }

    # Mapas de activación y desactivación
    ENABLE_MAP = {
        1: 'bold', 2: 'dim', 3: 'italic', 4: 'underline', 5: 'blink',
        7: 'reverse', 8: 'hidden', 9: 'strikethrough',
    }

    DISABLE_MAP = {
        22: ['bold', 'dim'], 23: ['italic'], 24: ['underline'], 25: ['blink'],
        27: ['reverse'], 28: ['hidden'], 29: ['strikethrough'], 39: ['fg'],
        49: ['bg'],
    }

    for match in ANSI_PATTERN.finditer(string):
        raw_codes = match.group(1)
        codes = raw_codes.split(';') if raw_codes else ['0']

        skip = 0
        for i, c in enumerate(codes):
            if skip:
                skip -= 1
                continue

            code = int(c) if c else 0

            if code == 0:
                for key in STATE:
                    STATE[key] = (
                            False if isinstance(STATE[key], bool) else None
                            )
            elif code in ENABLE_MAP:
                STATE[ENABLE_MAP[code]] = True
            elif code in DISABLE_MAP:
                for key in DISABLE_MAP[code]:
                    STATE[key] = ( False
                        if key in STATE and isinstance(STATE[key], bool)
                        else None
                                  )
            elif 30 <= code <= 37 or 90 <= code <= 97:
                STATE['fg'] = code
            elif 40 <= code <= 47 or 100 <= code <= 107:
                STATE['bg'] = code
            elif code == 38:
                if i + 2 < len(codes) and codes[i + 1] == '5':
                    STATE['fg'] = int(codes[i + 2])
                    skip = 2
            elif code == 48:
                if i + 2 < len(codes) and codes[i + 1] == '5':
                    STATE['bg'] = int(codes[i + 2])
                    skip = 2

    return any(
        val is True or (val not in (False, None))
        for val in STATE.values()
    )

def decode_selected_escapes(s: str) -> str:
    """
    Decodifica algunos escapes (\n, \t, \r, \x1b, \033, etc.)
    sin tocar caracteres UTF-8 como ñ o acentos.
    """
    esc_pattern = r'\\(x1b|033|[abcefnrtv])'

    def replacer(m):
        val = m.group(1)
        if val.startswith('x'):
            return chr(int(val[1:], 16))      # hex (ej: \x1b)
        elif val.isdigit():
            return chr(int(val, 8))           # octal (ej: \033)
        else:
            table = {
                'a':'\a','b':'\b','c':'\x03','e':'\x1b','f':'\f',
                'n':'\n','r':'\r','t':'\t','v':'\v'
            }
            return table[val]

    return sub(esc_pattern, replacer, s)

in_ansi = lambda string, boolean: repr(string) if boolean else string

def print (*values,
           sep=' ',
           end='\n',
           file=None,
           flush=False,
           delay=None, # delay sería un número str: /[0-9]+(\.[0-9]+)?/
           wrap=False,
           reset=False,
           ansi=False):

    """
    Función print personalizada con dos opciones extra:
      - reset: agrega \x1b[0m al final para resetear estilos ANSI
      - ansi: muestra los códigos ANSI escapados (repr)
    """

    count_list = len([x for x in values
                      if isinstance(x, (dict, list, set, tuple))])
    # Convertimos todo a str primero (igual que hace print internamente)
    values = sep.join(str(v) for v in values)

    is_escape_square = not ansi

    if count_list == 0:
        values = bb_to_ansi(values, is_escape_square=is_escape_square)

    # Si hay reset, agregamos secuencia de reset
    if reset:
        values += '\x1b[0m'

    # Si ansi=True, mostramos los códigos como texto escapado
    values = in_ansi(values, ansi)

    # Si el destino es un archivo, limpiamos secuencias ANSI
    if file is not None and not ansi:
        values = sub(r'\x1b\[[0-9;]*m', '', values)

    # Escritura en salida (archivo o consola)
    target = file if file is not None else __stdout__

    if wrap:
        values = ansi_wrap(values)

    if delay is not None and float(delay) > 0:
        parts = split(r'(\x1b\[[0-9;]*m)', values)
        for part in parts:
            if not part:
                continue
            if part.startswith("\x1b["):
                target.write(part)  # escape ANSI → de una
            else:
                for m in compile(r'(\s+|.)').finditer(part):
                    token = m.group(0)
                    if token.isspace():
                        target.write(token)  # bloque whitespace → de una
                    else:
                        target.write(token)  # char → con delay
                        if flush:
                            target.flush()
                        sleep(float(delay))
        target.write(end)
        if flush:
            target.flush()
    else:
        target.write(values + end)
        if flush:
            target.flush()

def input(prompt=None):
    """
    Función de entrada personalizada que soporta etiquetas de formato
    en el prompt, usando las mismas reglas que la función 'print'.

    Args:
        prompt (str|None): El mensaje a mostrar al usuario antes de la
                           entrada. Puede contener etiquetas de estilo
                           y secuencias de escape.

    Returns:
        str: La cadena de texto ingresada por el usuario.
    """

    reset = prompt[:2] == 'r '
    prompt = prompt[2:] if reset else prompt

    # Llama a la función print personalizada con el prompt.
    # Usamos end='' para que no agregue un salto de línea después del prompt,
    # y flush=True para que se imprima inmediatamente.
    # La función print ya se encarga de parsear los estilos, escapes
    # y el reseteo final.
    print(prompt, end='', flush=True, reset=reset)

    # Luego, llamamos a la función input original de Python
    # para obtener la entrada del usuario.
    user_input = py_input()
    return user_input

version = '0.1'
