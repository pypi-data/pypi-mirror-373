#!/usr/bin/env python3
from os.path import realpath
from sys import argv, exit
from re import match
try:
    from .core import (bb_to_ansi, decode_selected_escapes, flip,
                       is_active_styles, language, parse_cmd, print,
                       silence_deprecation_warnings, version
    )
except ImportError:
    from core import (bb_to_ansi, decode_selected_escapes, flip,
                      is_active_styles, language, parse_cmd, print,
                      silence_deprecation_warnings, version
    )

def main():
    silence_deprecation_warnings()

    command, flags, string = parse_cmd(argv)

    REAL_FILE = realpath(__file__).split('/')[-1].split('.')[0]

    all_cmd = list(flip(option='tuple'))
    all_cmd.extend(['echof', 'ef'])
    all_cmd.sort()

    if (command == REAL_FILE and not REAL_FILE in all_cmd
            or any(e in flags for e in ('-h', '--help', '--version'))):
        lang = language()

        if '--version' in flags and not '--help' in flags:
            print (f'{command} {version} (bbansi)')
            exit (0)

        manual = {
            'es': {
                'usage': 'Modo de uso: ',
                'option': 'Opciones',
                'ansi': ('  -a, --ansi', 'muestra el código ANSI'),
                'delay': ('  -d [b]N[/b], --delay=[b]N[/b]   ',
                          'Imprime el texto carácter por carácter con '
                          'un retardo de [b]N[/b] segundos.'),
                'nnl': ('  -n, --no-new-line',
                        'no enviar el carácter "salto de línea" al final'),
                'reset': ('  -r, --reset',
                          'restablece todos los estilos aplicados '
                          'al texto al final'),
                'wrap': ('  -w, --wrap',
                         'ajustar el texto para evitar el desbordamiento '
                         'horizontal'),
                'help': ('  -h, --help', 'muestra la ayuda y finaliza'),
                'version': ('  -v, --version',
                         'muestra la versión del programa y finaliza'),
            },
            'en': {
                'usage': 'Usage mode: ',
                'option': 'Options',
                'ansi': ('  -a, --ansi', 'show ANSI code'),
                'delay': ('  -d N, --delay=[b]N[/b]   ',
                          'Prints the text character by character with '
                          'a delay of [b]N[/b] seconds.'),
                'nnl': ('  -n, --no-new-line',
                        'do not output the trailing newline'),
                'reset': ('  -r, --reset',
                          'reset styles and colors in the end of the string'),
                'wrap': ('  -w, --wrap',
                         'wrap text to avoid horizontal overflow'),
                'help': ('  -h, --help', 'display this help and exit'),
                'version': ('  -v, --version',
                         'output version information and exit'),
            }
        }

        escapes = {
            'es': (
                ('\\\\', 'barra invertida'),
                ('\\a', 'alarma BELL'),
                ('\\b', 'espacio-atrás'),
                ('\\c', 'no produce ninguna salida más'),
                ('\\e', 'escape'),
                ('\\f', 'nueva página'),
                ('\\n', 'nueva linea'),
                ('\\r', 'retorno de carro'),
                ('\\t', 'tabular horizontal'),
                ('\\v', 'tabular vertical'),
                ('\\0NNN', 'el byte con valor octal NNN (de 1 a 3 dígitos)'),
                ('\\xHH',
                 'el byte con valor hexadecimal HH (de 1 a 2 dígitos)'),
                ('[[[[', '  apertura de corchete'),
                (']]]]', '  cierre de corchete')
            ),
            'en': (
                ('\\\\', 'backslash'),
                ('\\a', 'alert BELL'),
                ('\\b', 'backspace'),
                ('\\c', 'produce no further output'),
                ('\\e', 'escape'),
                ('\\f', 'form feed'),
                ('\\n', 'new line'),
                ('\\r', 'carriage return'),
                ('\\t', 'horizontal tab'),
                ('\\v', 'vertical tab'),
                ('\\0NNN', 'byte with octal value NNN (1 to 3 digits)'),
                ('\\xHH', 'byte with hexadecimal value HH (1 to 2 digits)'),
                ('[[[[', '  opening square bracket'),
                (']]]]', '  closing square bracket')
            )
        }

        _flags = {
            'es': {
                'b': 'Negrita',
                'd': 'Tenue',
                'i': 'Cursiva',
                'u': 'Subrayado',
                'k': 'Parpadeo',
                'r': 'Modo inverso',
                'h': 'Texto oculto',
                's': 'Tachado'
            },
            'en': {
                'b': 'Bold',
                'd': 'Dim',
                'i': 'Italic',
                'u': 'Unline',
                'k': 'Blink',
                'r': 'Reverse video',
                'h': 'Hidden text',
                's': 'Strike out'
            }
        }

        examples = {
            'es': (
                ('11,20', 'Texto y fondo', '-1,-1'),
                ('202', 'Solo texto', '256'),
                (',27', 'Solo fondo', ',333')
            ),
            'en': (
                ('11,20', 'Text & background', '-1,-1'),
                ('202', 'text-only display', '256'),
                (',27', 'background-only display', ',333')
            )
        }

        ansi_colores = {
            'es': ('Los colores se declaran '
                   '[[[i]fg[/i],[i]bg[/i]]], [[[i]fg[/i]]] o [[,[i]bg[/i]]].'
                   '\n'
                   '[i]fg[/i] y [i]bg[/i] equivalen a la paleta de colores '
                   'ANSI (del 0 al 255 inclusive).\n'
                   'Si [i]fg[/i] y/o [i]bg[/i] no está en ese rango, '
                   'se resetea el color.'),
            'en': ('Colors are declared as [[[i]fg[/i],[i]bg[/i]]], '
                   '[[[i]fg[/i]]] or [[,[i]bg[/i]]].\n'
                   '[i]fg[/i] and [i]bg[/i] refer to the ANSI color palette'
                   '(from 0 to 255 inclusive).\n'
                   'If [i]fg[/i] and/or [i]bg[/i] are outside that'
                   'range, the color is reset.')
        }

        lang = lang if language() in manual.keys() else 'en'
        length = 35 if lang == 'es' else 42

        commands = ('ef', 'capital', 'capitalize', 'invert', 'lower', 'title',
                    'upper')
        keys = list(manual[lang].keys())
        print (f'[b]{manual[lang]["usage"]}[/b]', end='')
        spaces = len(manual[lang]['usage']) * ' '
        for i, cmd in enumerate(commands):
            _str = {
                'es': 'hola MUNDO',
                'en': 'hello WORLD'
            }
            if cmd == 'ef':
                for i, e in enumerate(_flags[lang].items()):
                    k, v = e
                    ef = f'ef [[{k}]]{v}[[/{k}]]'
                    ef = '{:<{width}}'.format(ef, width=length)
                    result_show = f'→ [{k}]{v}[/{k}]'
                    if i == 0:
                        print (ef, result_show)
                    else:
                        print (f'{spaces}{ef} {result_show}')
                for _f, display, _ff in examples[lang]:
                    ef = f'ef [[{_f}]]{display}[[{_ff}]]'
                    ef = '{:<{width}}'.format(ef, width=length)
                    result_show = f'→ [{_f}]{display}[{_ff}]'
                    print (f'{spaces}{ef} {result_show}')
            else:
                _cmd = f'{cmd} {_str[lang]}'
                usage = (
                    '{:<{width}}'.format(_cmd, width=length - 3) +
                         f'→ {flip(_str[lang], cmd)}')
                print (f'{spaces}{usage}')
        print ('\n' + ansi_colores[lang], end='\n\n')
        for k in keys[2:]:
            o, t = manual[lang][k]
            print ('{:<20}'.format(o), t)
        print ('\n' + ('Se reconocen las siguientes secuencias:'
            if lang == 'es' else 'The following sequences are recognized:'))
        for esc, display in escapes[lang]:
            print (' ', '{:<5}'.format(esc), display)
        exit (0)

    string = decode_selected_escapes(string)
    string = bb_to_ansi(string)

    reset = '--reset' in flags and is_active_styles(string)
    _end = '' if '--no-new-line' in flags else '\n'
    is_ansi = '--ansi' in flags

    wrap = '--wrap' in flags

    delay = None
    for e in flags:
        if e[:8] == '--delay=':
            delay = e[8:]

    if command in flip(option='tuple'):
        print (flip(string, command), end=_end, flush=True, delay=delay,
               wrap=wrap, reset=reset, ansi=is_ansi)
    else:
        print (string, end=_end, flush=True, delay=delay, wrap=wrap,
               reset=reset, ansi=is_ansi)

if __name__ == '__main__':
    main()
