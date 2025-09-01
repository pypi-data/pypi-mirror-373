# BBANSI

Module with custom print and input functions that convert **pseudo-BBCode** into **ANSI escape codes**. It also includes a flip function that improves the standard string methods (`.capitalize()`, `.lower()`, `.title()`, and `.upper()`) and adds an invert option, all while preserving **ANSI codes**.

## Installation

#### From PyPI:

```bash
pip install bbansi
```

#### From APT as root or with `sudo`:

Add APT Key with `curl`:

```bash
curl -fsSL https://pablinet.github.io/apt/pablinet.gpg -o /etc/apt/trusted.gpg.d/pablinet.gpg```
```

Add APT Key with `wget`:

```bash
wget -O /etc/apt/trusted.gpg.d/pablinet.gpg https://pablinet.github.io/apt/pablinet.gpg
```

Update and install:

```
apt update && apt install python3-bbansi
```

If you encounter any errors, please check the project's [GitHub repository](https://github.com/PabliNet/bbansi).

## Command-line Interface (APT Version)

The APT installation includes seven executable commands that accept BBANSI tags:

`ef` (emulates the echo command)

`capital`

`capitalize`

`invert`

`lower`

`title`

`upper`

For more information on the usage of these commands, use ef `-h` or `--help`.

## Usage

```python
from bbansi import flip, input, print

print (flip('[kb]wELCOME TO THIS EXAMPLE', 'invert'), reset=True)
name = input ('r [b]What is your name? ')
print (f'Your name is [171,15]{flip(name, 'capitalize')}[]')
```

### Expected Output

Here's a preview of the output, both in its raw ANSI form and as it would appear in a terminal.

Raw Output:

```
'\x1b[5;1mWelcome to this example\x1b[0m'
'\x1b[1mWhat is your name?\x1b[0m pavel'
'Your name is \x1b[38;5;171;48;5;15mPavel
```

## print function

The print function has been extended with two optional boolean parameters: reset and ansi.

* **delay:** The parameter `delay` must match the pattern `/[0-9]+(\.[0-9]+)?/`.  
When provided, the output is printed character by character with a delay of `delay` seconds between each character.

* **reset:** When set to True, the ANSI reset sequence `'\x1b\[0m'` is automatically appended to the end of the output, ensuring that subsequent text does not retain any applied styling.

* **ansi:** When set to True, the ANSI escape codes are rendered explicitly in the output, similar to the behavior of the `repr()` function.

## input function

The only addition to this customized input function is the ability to automatically **reset styles and colors** by prefixing the prompt message with \-r.

**Example:** `name \= input ('-r [b]What is your name?')`

## Tags

|Tag open|Tag close|ANSI open|ANSI Close|Description|
|:-----------:|:-----------:|:-----:|:-----:|:---------------:|
|`[b]`¹|`[/b]`¹|`'\x1b[1m'`|`'\x1b[22m'`|Bold|
|`[d]`¹|`[/d]`¹|`'\x1b[2m'`|`'\x1b[22m'`|Dim|
|`[i]`¹|`[/i]`¹|`'\x1b[3m'`|`'\x1b[23m'`|Italic|
|`[u]`¹|`[/u]`¹|`'\x1b[4m'`|`'\x1b[24m'`|Underline|
|`[k]`¹|`[/k]`¹|`'\x1b[5m'`|`'\x1b[25m'`|Blink|
|`[r]`¹|`[/r]`¹|`'\x1b[7m'`|`'\x1b[27m'`|Reverse video|
|`[h]`¹|`[/h]`¹|`'\x1b[8m'`|`'\x1b[8m'`|Hidden text|
|`[s]`¹|`[/s]`¹|`'\x1b[9m'`|`'\x1b[29m'`|Strike out|
|`[FG,BG]`²|`[-1,256]`²|`'\x1b[38;5;FG;48;5;BGm'`|`'\x1b[39;49m'`|Text color and bacground color|
|`[FG]`²|`[354]`²|`'\x1b[38;5;FGm'`|`'\x1b[39m'`|Only text color|
|`[,BG]`²|`[,-1]`²|`'\x1b[48;5;BGm'`|`'\x1b[49m'`|Only background color|
|···|`[]`|···|`'\x1b[0m'`|All reset|

¹Multiple ANSI styles can be combined, e.g., [biuk].  
²The values for *FG* and *BG* must be integers within the inclusive range of 0 to 255\. Any value outside this range will reset the corresponding color.

## Escapes

`\\`    Backslash

`\a`    Alert BELL

`\b`    Backspace

`\c`    Produce no further output

`\e`    Escape

`\f`    Form feed

`\n`    New line

`\r`    Carriage return

`\t`    Horizontal tab

`\v`    Vertical tab

`\0NNN` Byte with octal value NNN (1 to 3 digits)

`\xHH`  Byte with hexadecimal value HH (1 to 2 digits)

`[[`    Opening square bracket

`]]`    Closing square bracket

## flip function

The flip function addresses a key limitation of standard string methods like .capitalize(), .lower(), and .title(): it correctly handles **ANSI styling codes** and **non-alphabetic characters**, preserving the codes while accurately modifying the text.

### Examples

Standard string methods:

```python
>>> string = '¡hello world!'
>>> print (string.capitalize())
¡hello world!  # The 'h' remains lowercase

>>> string = '\x1b[1mhello world\x1b[0m'
>>> print (repr(string.title()))
'\x1b[1Mhello World\x1b[0M'  # ANSI codes are incorrectly altered

>>> print (repr(string.upper()))
'\x1b[1MHELLO WORLD\x1b[0M'  # ANSI codes are affected
```
With the flip function:
```python
>>> string = '¡hello world!'
>>> print (flip(string, 'capitalize')
¡Hello world!  # Correctly capitalizes the first alphabetic character

>>> string = '\x1b[1mhello WOrld\x1b[0m'
>>> print (flip(string, 'capital')
'\x1b[1mHello world\x1b[0m'  # Proper casing, ANSI preserved

>>> print (flip(string, 'invert')
'\x1b[1mHELLO woRLD\x1b[0m'  # Inverts current case

>>> print (flip(string, 'title'))
'\x1b[1mHello World\x1b[0m'  # Proper title case

>>> print (flip(string, 'upper'))
'\x1b[1mHELLO WORLD\x1b[0m'  # All caps, ANSI untouched
```
You can also use the first letter of each option (**c**apitalize, **i**nvert, **l**ower, **t**itle, or **u**pper) for a more concise syntax.
```python
>>> string = '¡hello world!'
>>> print (flip(string, 'c')
¡Hello world!  # Correctly capitalizes the first alphabetic character

>>> string = '\x1b[1mhello WOrld\x1b[0m'
>>> print (flip(string, 'c')
'\x1b[1mHello world\x1b[0m'  # Proper casing, ANSI preserved

>>> print (flip(string, 'i')
'\x1b[1mHELLO woRLD\x1b[0m'  # Inverts current case

>>> print (flip(string, 't'))
'\x1b[1mHello World\x1b[0m'  # Proper title case

>>> print (flip(string, 'u'))
'\x1b[1mHELLO WORLD\x1b[0m'  # All caps, ANSI untouched
```
