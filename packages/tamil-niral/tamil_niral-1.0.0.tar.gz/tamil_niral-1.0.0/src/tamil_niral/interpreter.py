# -*- coding: utf-8 -*-

import re
import sys
import os
import time
import math
import random

################################################################################
# தமிழ் நிரலுக்கான பிரத்யேக பிழைகள்
################################################################################

class TamilNiralError(Exception):
    """தமிழ் நிரலில் உள்ள அனைத்து பிழைகளுக்குமான அடிப்படை வகுப்பு."""
    def __init__(self, message, line_num=None, line_text=None, offset=None):
        super().__init__(message)
        self.line_num = line_num
        self.line_text = line_text
        self.offset = offset

class TamilNiralSyntaxError(TamilNiralError):
    """தொடரியல் பிழைகளுக்கு."""
    def __init__(self, message, line_num=None, line_text=None, offset=None):
        super().__init__(f"தொடரியல்பிழை: {message}", line_num, line_text, offset)

class TamilNiralNameError(TamilNiralError):
    """இல்லாத மாறி அல்லது செயலை குறிப்பிடும்போது ஏற்படும் பிழை."""
    def __init__(self, message, line_num=None, line_text=None, offset=None):
        super().__init__(f"பெயர்ப்பிழை: {message}", line_num, line_text, offset)

class TamilNiralValueError(TamilNiralError):
    """சரியான வகை ஆனால் பொருத்தமற்ற மதிப்புடன் ஒரு செயல்பாடு செய்யப்படும்போது ஏற்படும் பிழை."""
    def __init__(self, message, line_num=None, line_text=None, offset=None):
        super().__init__(f"மதிப்புப்பிழை: {message}", line_num, line_text, offset)

class TamilNiralTypeError(TamilNiralError):
    """பொருத்தமற்ற வகை பொருளின் மீது ஒரு செயல்பாடு செய்யப்படும்போது ஏற்படும் பிழை."""
    def __init__(self, message, line_num=None, line_text=None, offset=None):
        super().__init__(f"வகைப்பிழை: {message}", line_num, line_text, offset)
        
class TamilNiralIndexError(TamilNiralError):
    """பட்டியல் அல்லது சரத்தின் வரம்பிற்கு வெளியே ஒரு குறியீட்டை அணுக முயற்சிக்கும்போது ஏற்படும் பிழை."""
    def __init__(self, message, line_num=None, line_text=None, offset=None):
        super().__init__(f"குறியீட்டுப்பிழை: {message}", line_num, line_text, offset)

class TamilNiralKeyError(TamilNiralError):
    """அகராதியில் இல்லாத ஒரு திறவை அணுக முயற்சிக்கும்போது ஏற்படும் பிழை."""
    def __init__(self, message, line_num=None, line_text=None, offset=None):
        super().__init__(f"திறவுப்பிழை: {message}", line_num, line_text, offset)
        
class TamilNiralFileNotFoundError(TamilNiralError):
    """குறிப்பிட்ட கோப்பு காணப்படாதபோது ஏற்படும் பிழை."""
    def __init__(self, message, line_num=None, line_text=None, offset=None):
        super().__init__(f"கோப்புக்காணவில்லைப்பிழை: {message}", line_num, line_text, offset)

################################################################################
# கோப்பு கையாளுதலுக்கான பிரத்யேக தமிழ் வகுப்பு
################################################################################

class TamilFileWrapper:
    def __init__(self, file_object):
        self._file = file_object

    def எழுது(self, content):
        return self._file.write(content)

    def படி(self, size=-1):
        return self._file.read(size)
    
    def மூடு(self):
        return self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.மூடு()

################################################################################
# மொழிமாற்றி வகுப்பு (Transpiler)
################################################################################

class TamilNiralTranspiler:
    def __init__(self):
        self.program_lines = []
        self.had_error = False
        
        self.operators = {
            'கூட்டு': ' + ', 'கழி': ' - ', 'பெருக்கு': ' * ', 'வகு': ' / ',
            'ஈவு': ' // ', 'மீதி': ' % ', 'அடுக்கு': ' ** ', 'மற்றும்': ' and ',
            'அல்லது': ' or ', 'சமம்': ' == ',
            'சமமல்ல': ' != ', 'பெரிது': ' > ', 'சிறிது': ' < ',
            'பெரிதுசமம்': ' >= ', 'சிறிதுசமம்': ' <= '
        }
        
        self.assignment_operators = {
            'கூட்டிசேர்': '+=', 'கழித்துசேர்': '-=', 'பெருக்கிசேர்': '*=', 'வகுத்துசேர்': '/=',
            'மீதிசேர்': '%=', 'ஈவுசேர்': '//=', 'அடுக்கிசேர்': '**='
        }

        self.error_messages = {
            "invalid_char": "ஆங்கில எழுத்துக்கள் '{text}' அனுமதிக்கப்படுவதில்லை.",
            "undefined_name": "பெயர் '{name}' வரையறுக்கப்படவில்லை.",
            "missing_in_for": "'முன்கூறிதிரும்பு' கட்டளையில் 'இல்' என்ற முக்கிய வார்த்தை காணவில்லை.",
            "colon_missing": "'{keyword}' கட்டளைக்குப் பிறகு ':' குறியீடு காணவில்லை.",
            "incomplete_assignment": "'=' குறியீட்டிற்குப் பிறகு ஒரு மதிப்பு தேவை.",
            "file_not_found": "'{filename}' என்ற கோப்பு காணப்படவில்லை.",
            "unsupported_operation": "'{op}' என்ற செயலி '{type1}' மற்றும் '{type2}' வகைகளுக்கு இடையில் ஆதரிக்கப்படவில்லை.",
            "index_out_of_range": "பட்டியல் குறியீடு வரம்பிற்கு வெளியே உள்ளது.",
            "key_not_found": "அகராதியில் '{key}' என்ற திறவு இல்லை.",
            "invalid_value_for_cast": "'{value}' என்பதை '{type}' வகையாக மாற்ற முடியவில்லை.",
            "function_argument_mismatch": "'{func}' என்ற செயல் {expected} அளவுருக்களை எதிர்பார்க்கிறது, ஆனால் {given} கொடுக்கப்பட்டுள்ளன.",
            "invalid_input_syntax": "தவறான 'உள்ளீடு' கட்டளை அமைப்பு.",
            "unknown_type": "அறியப்படாத வகை '{type_name}'."
        }
        
        self.allowed_modules = { 'கணிதம்': 'math', 'சீரற்ற': 'random', 'கோப்பு': 'os' }
        self.file_modes = { 'படி': 'r', 'எழுது': 'w', 'சேர்': 'a' }
        self.type_casters = {
            'எண்': 'int', 'பதின்மம்': 'float', 'உரை': 'str', 'சரிதவறு': 'bool',
            'பட்டியல்': 'list', 'இணை': 'tuple', 'தொகுப்பு': 'set', 'அகராதி': 'dict'
        }

    def validate_no_english(self, text, line_num, line_text):
        match = re.search(r'[a-zA-Z]', text)
        if match:
            # f-string format வ"..." is allowed
            if text.strip().startswith('வ"') or text.strip().startswith("வ'"):
                return
            raise TamilNiralSyntaxError(self.error_messages["invalid_char"].format(text=match.group(0)), line_num, line_text, match.start() + 1)

    def report_error(self, error, filename="<stdin>", line_num=0, line_text=""):
        self.had_error = True
        print(f'கோப்பு "{filename}", வரி {line_num + 1}', file=sys.stderr)
        stripped_line = line_text.strip()
        print(f'  {stripped_line}', file=sys.stderr)
        
        offset = getattr(error, 'offset', None)
        if offset:
            indentation = len(line_text) - len(line_text.lstrip())
            pointer_pos = max(0, offset - indentation - 1)
            print('  ' + ' ' * pointer_pos + '^', file=sys.stderr)
        else:
            print('  ^', file=sys.stderr)
        print(f'{error}', file=sys.stderr)

    def transpile_expression(self, expr):
        expr = expr.strip()
        
        # Handle formatted strings (வ"...") robustly to avoid replacing operators inside string literals
        if expr.startswith('வ"') or expr.startswith("வ'"):
            # Extract inner expressions e.g., {name}
            inner_expressions = re.findall(r'{([^{}]*)}', expr)
            
            # Create unique placeholders
            placeholders = [f'__TN_PLACEHOLDER_{i}__' for i in range(len(inner_expressions))]
            
            # Replace inner expressions with placeholders
            temp_f_string = expr
            for i, inner_expr in enumerate(inner_expressions):
                temp_f_string = temp_f_string.replace('{' + inner_expr + '}', placeholders[i], 1)

            # Transpile only the extracted inner expressions recursively
            transpiled_inners = [self.transpile_expression(ie) for ie in inner_expressions]

            # Convert the temp string to a python f-string
            python_f_string = 'f' + temp_f_string[1:]

            # Replace placeholders with the transpiled code, now wrapped in braces
            for i, placeholder in enumerate(placeholders):
                python_f_string = python_f_string.replace(placeholder, f'{{{transpiled_inners[i]}}}')
            
            return python_f_string

        # Standard replacements for non-f-string expressions
        replacements = {
            'கடிகாரம்()': 'time.perf_counter()', 'வரம்பு(': 'range(',
            'கணிதம்.வர்க்கமூலம்(': 'math.sqrt(', 'சீரற்ற.சீரற்றஎண்(': 'random.randint(',
            'மெய்': 'True', 'பொய்': 'False', 'வெறுமை': 'None'
        }
        for tamil, py in self.type_casters.items():
            replacements[f'{tamil}('] = f'{py}('

        for tamil, py in replacements.items():
            expr = expr.replace(tamil, py)
        
        expr = re.sub(r'\bகிடையாது\b', 'not', expr)

        for tamil_op, py_op in self.operators.items():
            expr = expr.replace(f'{tamil_op}', f'{py_op}')
        return expr

    def transpile(self, code):
        self.program_lines = code.split('\n')
        python_code, imports = [], []
        indent_level, in_try_block = 0, False
        self.line_map = {}
        
        for i, line in enumerate(self.program_lines):
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith('ஃ'): continue
            
            line_without_f_strings = re.sub(r'வ".*?"|வ\'.*?\'', '""', stripped_line)
            self.validate_no_english(line_without_f_strings, i, line)

            if stripped_line.startswith('இறக்குமதி '):
                module_name_tamil = stripped_line.split(' ')[1].strip()
                if module_name_tamil in self.allowed_modules:
                    imp_stmt = f"import {self.allowed_modules[module_name_tamil]} as {module_name_tamil}"
                    if imp_stmt not in imports: imports.append(imp_stmt)
                else: raise TamilNiralNameError(f"தொகுதி '{module_name_tamil}' காணப்படவில்லை.", i, line)
                continue

            if stripped_line.startswith(('அல்லதுஎனில் ', 'பிழை:')) or re.match(r'^(?:இல்லையேல்|இல்லை):?$', stripped_line):
                indent_level = max(0, indent_level - 1)

            if stripped_line == 'முடி':
                indent_level, in_try_block = max(0, indent_level - 1), False
                continue

            indent = '    ' * indent_level
            current_py_line = len(imports) + len(python_code) + (3 if imports else 1)
            self.line_map[current_py_line] = i
            
            if stripped_line.startswith('முயற்சி:'):
                python_code.append(f"{indent}try:")
                indent_level, in_try_block = indent_level + 1, True
            elif stripped_line.startswith('பிழை:'):
                if not in_try_block: raise TamilNiralSyntaxError("'பிழை:' தொகுதி ஒரு 'முயற்சி:' தொகுதிக்கு வெளியே உள்ளது.", i, line)
                python_code.append(f"{indent}except Exception as பிழை:")
                indent_level, in_try_block = indent_level + 1, False
            elif stripped_line.startswith('கோப்புடன் '):
                if not stripped_line.endswith(':'): raise TamilNiralSyntaxError("'கோப்புடன்' கட்டளைக்குப் பிறகு ':' குறியீடு காணவில்லை.", i, line)
                match = re.match(r'கோப்புடன்\s+(.+)\s+என\s+(.+):', stripped_line)
                if match:
                    open_call, var_name = match.groups()
                    python_code.append(f"{indent}with {self.transpile_expression(open_call)} as {var_name}:")
                    indent_level += 1
                else: raise TamilNiralSyntaxError("தவறான 'கோப்புடன்' கட்டளை அமைப்பு.", i, line)
            elif stripped_line.startswith('அச்சிடு '):
                args = self.transpile_expression(stripped_line[len('அச்சிடு '):])
                python_code.append(f"{indent}print({args})")
            elif stripped_line.startswith('உள்ளீடு '):
                match = re.match(r'உள்ளீடு\s+(".*?"|\'.*?\')\s+([^\s=]+)(?:\s*=\s*([^\s]+))?', stripped_line)
                if match:
                    prompt, var_name, var_type_tamil = match.groups()
                    if var_type_tamil:
                        if var_type_tamil not in self.type_casters:
                            raise TamilNiralSyntaxError(self.error_messages["unknown_type"].format(type_name=var_type_tamil), i, line)
                        py_type = self.type_casters[var_type_tamil]
                        python_code.append(f"{indent}{var_name} = {py_type}(input({prompt}))")
                    else:
                        python_code.append(f"{indent}{var_name} = input({prompt})")
                else:
                    raise TamilNiralSyntaxError(self.error_messages["invalid_input_syntax"], i, line)
            elif stripped_line.startswith(('எனில் ', 'அல்லதுஎனில் ')):
                if not stripped_line.endswith(':'): raise TamilNiralSyntaxError(self.error_messages["colon_missing"].format(keyword=stripped_line.split(' ')[0]), i, line)
                keyword = 'if' if stripped_line.startswith('எனில் ') else 'elif'
                condition = self.transpile_expression(stripped_line.split(' ', 1)[1].rstrip(':'))
                python_code.append(f"{indent}{keyword} {condition}:")
                indent_level += 1
            elif re.match(r'^(?:இல்லையேல்|இல்லை):?$', stripped_line):
                python_code.append(f"{indent}else:")
                indent_level += 1
            elif stripped_line.startswith('முன்கூறிதிரும்பு '):
                if not stripped_line.endswith(':'): raise TamilNiralSyntaxError(self.error_messages["colon_missing"].format(keyword='முன்கூறிதிரும்பு'), i, line)
                if ' இல் ' not in stripped_line: raise TamilNiralSyntaxError(self.error_messages["missing_in_for"], i, line)
                parts = stripped_line.split(' இல் ')
                var_name = parts[0][len('முன்கூறிதிரும்பு '):].strip()
                iterable = self.transpile_expression(parts[1].rstrip(':'))
                python_code.append(f"{indent}for {var_name} in {iterable}:")
                indent_level += 1
            elif stripped_line.startswith('நிபந்தனைதிரும்பு '):
                if not stripped_line.endswith(':'): raise TamilNiralSyntaxError(self.error_messages["colon_missing"].format(keyword='நிபந்தனைதிரும்பு'), i, line)
                condition = self.transpile_expression(stripped_line[len('நிபந்தனைதிரும்பு '):].rstrip(':'))
                python_code.append(f"{indent}while {condition}:")
                indent_level += 1
            elif stripped_line.startswith('செயல் '):
                if not stripped_line.endswith(':'): raise TamilNiralSyntaxError(self.error_messages["colon_missing"].format(keyword='செயல்'), i, line)
                match = re.match(r'செயல்\s+([^\(]+)\((.*)\):', stripped_line)
                if match:
                    name, params_str = match.groups()
                    python_code.append(f"{indent}def {name.strip()}({params_str.strip()}):")
                    indent_level += 1
            elif stripped_line.startswith('திருப்பு '):
                python_code.append(f"{indent}return {self.transpile_expression(stripped_line[len('திருப்பு '):])}")
            else:
                found_assignment_op = False
                for tamil_op, py_op in self.assignment_operators.items():
                    op_with_spaces = f' {tamil_op} '
                    if op_with_spaces in stripped_line:
                        parts = stripped_line.split(op_with_spaces, 1)
                        var_name, expr = parts[0].strip(), parts[1].strip()
                        if not expr: raise TamilNiralSyntaxError(f"'{tamil_op}' செயலிக்குப் பிறகு ஒரு மதிப்பு தேவை.", i, line)
                        python_code.append(f"{indent}{var_name} {py_op} {self.transpile_expression(expr)}")
                        found_assignment_op = True
                        break
                
                if found_assignment_op: continue

                if '=' in stripped_line and not any(op in stripped_line for op in ['==', '!=', '<=', '>=']):
                    parts = stripped_line.split('=', 1)
                    var_name, expr = parts[0].strip(), parts[1].strip()
                    if not expr: raise TamilNiralSyntaxError(self.error_messages["incomplete_assignment"], i, line)
                    python_code.append(f"{indent}{var_name} = {self.transpile_expression(expr)}")
                else:
                    python_code.append(f"{indent}{self.transpile_expression(stripped_line)}")
        return "\n".join(imports) + "\n\n" + "\n".join(python_code)

    def _create_global_scope(self):
        def tamil_open(filename, mode_tamil='படி', encoding='utf-8'):
            try:
                py_mode = self.file_modes.get(mode_tamil, 'r')
                file_obj = open(filename, py_mode, encoding=encoding)
                return TamilFileWrapper(file_obj)
            except FileNotFoundError:
                raise TamilNiralFileNotFoundError(self.error_messages["file_not_found"].format(filename=filename))
        
        scope = {
            'time': time, 'math': math, 'random': random, 'os': os,
            'print': print, 'range': range, 'input': input,
            'True': True, 'False': False, 'None': None,
            'கோப்புதிற': tamil_open
        }
        py_types = {'int': int, 'float': float, 'str': str, 'bool': bool, 'list': list, 'tuple': tuple, 'set': set, 'dict': dict}
        for py_name in py_types.values():
            scope[py_name.__name__] = py_name
        return scope
    
    def _map_python_error(self, e, py_line_num):
        error_message = str(e)
        tamil_line_num = self.line_map.get(py_line_num, 0)
        line_text = self.program_lines[tamil_line_num] if tamil_line_num < len(self.program_lines) else ""
        
        if isinstance(e, SyntaxError):
            return TamilNiralSyntaxError(f"தவறான கட்டளை அமைப்பு: {e.msg}", tamil_line_num, e.text, e.offset)
        if isinstance(e, NameError):
            return TamilNiralNameError(self.error_messages["undefined_name"].format(name=error_message.split("'")[1]), tamil_line_num, line_text)
        if isinstance(e, ZeroDivisionError):
            return TamilNiralValueError("பூஜ்ஜியத்தால் வகுக்க முடியாது", tamil_line_num, line_text)
        if isinstance(e, TypeError):
             if "unsupported operand type" in error_message:
                 match = re.search(r"'(.*?)'.*'(.*?)' and '(.*?)'", error_message)
                 op, type1, type2 = match.groups()
                 msg = self.error_messages["unsupported_operation"].format(op=op, type1=type1, type2=type2)
                 return TamilNiralTypeError(msg, tamil_line_num, line_text)
             if "takes" in error_message and "argument" in error_message:
                 match = re.search(r"(.+)\(\) takes (\d+).*but (\d+) were given", error_message)
                 func, expected, given = match.groups()
                 msg = self.error_messages["function_argument_mismatch"].format(func=func, expected=expected, given=given)
                 return TamilNiralTypeError(msg, tamil_line_num, line_text)
        if isinstance(e, ValueError):
            type_map = {'int': 'எண்', 'float': 'பதின்மம்', 'bool': 'சரிதவறு'}
            for py_type, tamil_type in type_map.items():
                if f"invalid literal for {py_type}()" in error_message or f"could not convert string to {py_type}" in error_message:
                    match = re.search(r": '(.*)'", error_message)
                    value = match.group(1) if match else "''"
                    msg = self.error_messages["invalid_value_for_cast"].format(value=value, type=tamil_type)
                    return TamilNiralValueError(msg, tamil_line_num, line_text)
        if isinstance(e, IndexError):
            return TamilNiralIndexError(self.error_messages["index_out_of_range"], tamil_line_num, line_text)
        if isinstance(e, KeyError):
            return TamilNiralKeyError(self.error_messages["key_not_found"].format(key=error_message), tamil_line_num, line_text)
        if isinstance(e, TamilNiralFileNotFoundError): return e

        return TamilNiralError(f"இயக்க நேரப் பிழை: {error_message}", tamil_line_num, line_text)

    def run(self, code, filename="<stdin>"):
        self.had_error = False
        try:
            python_code = self.transpile(code)
            compiled_code = compile(python_code, filename, 'exec')
            exec(compiled_code, self._create_global_scope())
        except (TamilNiralError, SyntaxError) as e:
            if isinstance(e, SyntaxError):
                final_error = self._map_python_error(e, e.lineno or 0)
                self.report_error(final_error, filename, final_error.line_num, final_error.line_text)
            else:
                self.report_error(e, filename, e.line_num, e.line_text)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            py_line_num = exc_tb.tb_lineno if exc_tb else 0
            final_error = self._map_python_error(e, py_line_num)
            self.report_error(final_error, filename, final_error.line_num, final_error.line_text)
        
        return not self.had_error

def run_tamil_niral_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file: code = file.read()
    except FileNotFoundError:
        print(f"பிழை: '{filename}' கோப்பு காணப்படவில்லை", file=sys.stderr)
        return
    transpiler = TamilNiralTranspiler()
    success = transpiler.run(code, filename=filename)
    if success: print("\n>> நிரல் வெற்றிகரமாக முடிந்தது <<")
    else: print("\n>> நிரல் பிழைகளுடன் முடிந்தது <<")

def start_interactive_shell():
    print("தமிழ் நிரல் மொழி ஊடாடும் ஷெல் (v10.0 - வடிவமைப்புச் சரங்கள்)")
    print("வெளியேற 'வெளியேறு' என தட்டச்சு செய்யவும்.")
    transpiler = TamilNiralTranspiler()
    while True:
        try:
            line = input('>>> ')
            if line.strip().lower() == 'வெளியேறு': print("நன்றி!"); break
            transpiler.run(line)
        except (KeyboardInterrupt, EOFError): print("\nநன்றி!"); break

if __name__ == "__main__":
    if len(sys.argv) > 1: run_tamil_niral_file(sys.argv[1])
    else: start_interactive_shell()
