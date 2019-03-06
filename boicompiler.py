import re
import sys
import os
import random
from itertools import cycle  # will repeat after end

source = []
cppcode = ['// NOTE: This code was generated algorithmically from Boi source code.\n',
           '// It looks sloppy because it is not meant to be read by humans.\n',
           '#include <iostream>\n', '#include <stdlib.h>\n', '#include <string>\n', 
           'using namespace std;\n']

files = sys.argv[1]


if files[-4:] != ".boi":
    print('\033[1;31m' + 'Boi: Filename Error: Not a `.boi` file' + '\033[0m')
    sys.exit()


else:
    string = open(files).read()
    source_code_lines = string.split('\n')
    for x in source_code_lines:
        if "include" in x:
            lib = open(x[8:])
            code = lib.read()
            lib_code_lines = code.split('\n')
            for p in lib_code_lines:
                if p[0:1] != "~ " and p[-2:] != " ~":
                    source.append(p)
                else:
                    source.append("\n")
        elif x[0:1] != "~ " and x[-2:] != " ~":
            source.append(x)
        else:
            source.append("\n")
            
            
def notInt(s):
    try: 
        int(s)
        return False
    except ValueError:
        return True

            
def interpret(code):
    start   = re.search('start{|start {', code) # start{

    funcdec = re.search(r'func (.+)\((.*?)\) {', code) # func <function-name>(args) {
    endfunc = re.search(r'} end-func', code)
    funccall = re.search(r'do (.+)\((.*?)\)', code)

    comment = re.search('~ (.+) ~', code) # Catches inline comments. # Or is supposed to, but it doesn't work.
    vardec  = re.search('var \$(.+)\=(.+)', code) # var $<variable-name>=<value>
    newline = re.search('newl', code) # newl

    sum  = re.search(r'sum\{(.*?), (.*?)\}', code)  # sum{number, number}
    prod = re.search(r'prod\{(.*?), (.*?)\}', code) # prod{number, number}
    diff = re.search(r'diff\{(.*?), (.*?)\}', code) # diff{number, number}
    quot = re.search(r'quot\{(.*?), (.*?)\}', code) # quot{number, number}
    mathcodes = ["sum{", "prod", "diff", "quot", "toin"]
    
    output  = re.search('output\((.+)\)', code) # output(something)
    input   = re.search('input\((.+), (.+)\)', code) # input(<buffer-size>, <variable-name>)
    
    ifstat_start = re.search('\sif \((.+)\) then {', code) # if (condition) then {
    else_clause  = re.search('} else {', code) # } else {
    ifstat_end   = re.search('} end-if', code) # } end-if
    
    for_loop = re.search(r'for \((.+) to (.+)\) do {', code) # for (start to end) do {
    while_loop = re.search(r'while \((.+)\) do {', code) # while (condition) do {
    until_loop = re.search(r'until \((.+)\) do {', code) # until (condition) do {
    loop_end  = re.search('} end-loop', code) # } end-loop
    
    cpp_sub_stat = re.search(r'[^\"](.+?)\-\-[^\"]', code)
    cpp_inc_stat = re.search(r'[^\"](.+?)\+\+[^\"]', code)
    string_literal = re.search(r'\"(.+)\"', code)
    
    boi_sub_stat = re.search('inc\(\-(.+)\)', code)
    boi_inc_stat = re.search('inc\((.+)\)', code)
    
    int_cast = re.search(r'toint\((.+)\)', code)
    float_cast = re.search(r'toflo\((.+)\)', code)
    
    sys = re.search(r'system\((.+)\)', code)
    
    end     = re.search('}end|} end', code)
    
    if start:
        return 'int main(void){\n'
    if output:
        return 'cout << ' + interpret(output.group(1)) + ';\n'
    if input:
        variable = "var" + str(random.randint(0, 1000000000000))
        return "string " + variable + ";\n" + "getline(cin, " + variable + ");\n" + "if (" + variable + ".length() <= " + interpret(input.group(1)) + ") {\n" + "    " + input.group(2) + " = " + variable + ";\n" + "} else {\n" + "    cout << \"\\033[1;31m\" << \"Boi: Overflow Error: Not enough space in variable '" + input.group(2) + "'\" << \"\\033[0m\\n\";\n" + "    exit(EXIT_SUCCESS);\n" + "}\n"

    """
    The above is pretty confusing to look at in this layout, so
    here's what it looks like in the `out.cpp` file:
    
    string var+number;
    cin >> var+number;
    if (var+number.length() <= variableSize) {
        variable = var+number;
    } else {
        cout << "\033[1;31m" << "Boi: Overflow Error: Not enough space in variable 'variable'" << "\033[0m\n";
        exit(EXIT_SUCCESS);
    }
    
    What this does is it creates a variable `var` + a random number, so it's unlikely to
    be used for anything else by the Boi programmer and therefore can safely be used as a reserved
    word. The loop then puts user input of arbitrary size into that variable, and checks to see if
    it is less than or equal to the maximum allowed length given to it in the Boi program. If it isn't,
    it throws this error and quits.

    """

    if funcdec and not output and not input:
        if not funcdec.group(2):
            print('\033[1;31m' + 'Boi: Syntax Error: Attempted function declaration without arguments' + '\033[0m')
            print('\033[1;31m' + '>>>' + str(code) + '\033[0m')
            sys.exit()
        elif funcdec.group(2) == "void":
            return 'void ' + funcdec.group(1) + '() {\n'
        else:
            args = funcdec.group(2).split()
            new_args = []
            for x in args:
                new_args.append("string " + x)
            return 'void ' + funcdec.group(1) + '(' + ''.join(new_args) + ') {\n'
    if endfunc:
        return '} // end of function defintion\n'
    if funccall and not output and not input:
        if not funccall.group(2):
            print('\033[1;31m' + 'Boi: Syntax Error: Attempted function call without arguments' + '\033[0m')
            print('\033[1;31m' + '>>>' + str(code) + '\033[0m')
            sys.exit()
        elif funccall.group(2) == "void":
            return funccall.group(1) + '();\n'
        else:
            return funccall.group(1) + '(' + interpret(funccall.group(2)) + ');\n'
    if comment:
        return interpret(code.replace("~ " + comment.group(1) + " ~", ""))
    if vardec:
        if vardec.group(2) == "void":
            return 'string ' + vardec.group(1) + ';\n'
        elif vardec.group(2)[0] != '"' and vardec.group(2)[-1] != '"':
            if "." in vardec.group(2) and "flo" not in vardec.group(2):
                return 'double ' + vardec.group(1) +  '=' + interpret(vardec.group(2)) + ';\n'
            elif ".flo" in vardec.group(2):
                return 'float ' + vardec.group(1) + '=' + interpret(vardec.group(2)).replace('.flo', '') + ';\n'
            elif "toflo" in vardec.group(2):
                return 'float ' + vardec.group(1) + '=' + interpret(vardec.group(2)) + ';\n'
            else:
                return 'int ' + vardec.group(1) + '=' + interpret(vardec.group(2)) + ';\n'
        else:
            return 'string ' + vardec.group(1) + '=' + interpret(vardec.group(2)) + ';\n'
    if int_cast:
        return 'stoi(' + interpret(int_cast.group(1)) + ')'
    if float_cast:
        return 'stof(' + interpret(float_cast.group(1)) + ')'
    if newline:
        return 'cout << endl;\n'

    if end and not ifstat_end and not loop_end and not endfunc:
        return 'return 0;\n}\n'
    if ifstat_start:
        return 'if (' + interpret(ifstat_start.group(1)) + ') {\n'
    if else_clause:
        return '} else {\n'
    if ifstat_end:
        return '} // to end a conditional only\n'
    if cpp_sub_stat or cpp_inc_stat:
        if not string_literal:
            print('\033[1;31m' + 'Boi: Syntax Error: Invalid expression' + '\033[0m')
            print('\033[1;31m' + '>>>' + str(code) + '\033[0m')
            sys.exit()
        else:
            pass
    if boi_sub_stat:
        return boi_sub_stat.group(1) + ' = ' + boi_sub_stat.group(1) + ' - 1;\n'
    if boi_inc_stat:
        return boi_inc_stat.group(1) + ' = ' + boi_inc_stat.group(1) + ' + 1;\n'
    if for_loop:
        variable = "var" + str(random.randint(0, 1000000000000))
        return 'for (int ' + variable + ' = ' + interpret(for_loop.group(1)) + '; ' + variable + ' < ' + interpret(for_loop.group(2)) + '; ' + variable + '++) {\n'
    if while_loop:
        return 'while (' + interpret(while_loop.group(1)) + ') {\n'
    if until_loop:
        return 'while (not (' + interpret(until_loop.group(1)) + ')) {\n'
    if loop_end:
        return '} // end the loop\n'
    if sum:
        return interpret(sum.group(1)) + ' + ' + interpret(sum.group(2))
    if prod:
        return interpret(prod.group(1)) + ' * ' + interpret(prod.group(2))
    if diff:
        return interpret(diff.group(1)) + ' - ' + interpret(diff.group(2))
    if quot:
        return interpret(quot.group(1)) + ' / ' + interpret(quot.group(2))
    if sys:
        if string_literal:
            return 'system(' + sys.group(1) + ');\n'
        else:
            return 'system(' + sys.group(1) + '.c_str());\n'
    else:
        return code
        

for x in source:
    if interpret(x) != None:
        cppcode.append(interpret(x))

    else:
        cppcode.append("\n")
    
cpp_out = open('out.cpp', 'w+') # The C++ interpretation of the Boi code goes here.

for x in cppcode:
    if "prod{" in x or "sum{" in x or "diff{" in x or "quot{" in x:
        print('\033[1;31m' + 'Boi: Syntax Error: Can\'t use nested arithmetic operators' + '\033[0m')
        sys.exit()
    else:
        cpp_out.write(x)
    
cpp_out.close()
    
os.system('g++ -o %s.binary out.cpp && ./%s.binary && rm -f out.cpp' % (files, files))
