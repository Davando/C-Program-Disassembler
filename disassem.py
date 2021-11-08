import subprocess
import webbrowser
import datetime
import sys
import os
import re

dwarf_dump = ""
obj_dump = []
source_code_lines = []

dwarf_list = []
obj_dict = {}
main_loc = ""

def get_dump_file(argv): 
    # creates gcc arguments from command line file arguments
    argument_files = "gcc -g3 -o myprogram "
    for arg in argv:
        argument_files += arg + " "

    # compiles .c files with dump info
    compile_files = subprocess.check_call(argument_files, shell=True)
    
    # saves contents of dwarf-dump file as string 
    dwarf_dump_as_str = subprocess.run(["llvm-dwarfdump", "--debug-line", "myprogram"], capture_output = True).stdout.decode('utf-8')
   # print(dwarf_dump_as_str)

    # cleans data from dwarf dump file to only include address and source code
    # file line number
    global dwarf_dump
    clean_up_dwarf_dump(dwarf_dump_as_str)

    # saves contents of obj-dump file as string
    obj_dump_as_str = subprocess.run(["objdump", "-d", "myprogram"], capture_output = True).stdout.decode('utf-8')
    # print(obj_dump_as_str)

    # finds location of main method
    global main_loc
    main_loc = re.search("<main>:\s*([0-9a-f]*):", obj_dump_as_str).group(1)

    # cleans data from obj-dump to only include address and assembly code
    lines = re.split("\n", obj_dump_as_str)
    for line in lines:
        temp = re.findall("401\w{3}:.*", line)
        if len(temp) != 0:
            temp = re.sub("\\t", " ", line)
            obj_dump.append(temp)

def clean_up_dwarf_dump(raw_dwarf_dump):
    file_dump = re.split("debug_line\[.*\]", raw_dwarf_dump)
    for each_file in file_dump:
        file_name = re.search("\"\w*.c\"", each_file)
        # includes all but last address/line since it duplicates on last and
        # first rows of each consecutive file.
        address_and_line = re.findall("0x\w{16}\s*[0-9]*", each_file)[:-1]
        
        # if file dump includes c file name, we create a dictionary of address
        # and source line numbers and add it to a list (dwarf_list) containing 
        # the c file name and the aforementioned dictionary.
        if file_name is not None:
            dic = {}   
            for line in address_and_line:
                address = re.search("0x0*([a-f0-9]*)", line).group(1)
                line_num = re.split("\s+", line)
                dic[address] = line_num[1]
            dwarf_list.append([file_name.group(), dic])

def get_c_files(argv):
    # Saves input .c files to a list by line number
    global source_code_lines
    for file in argv:
        f = open(file, 'r')
        text_file = f.read()
        source_code_lines.append(re.split("\n", text_file))
        
def populate_obj_dict():
    # adds contents of obj_dump to a dictionary obj_dict using asm address as
    # key and the corresponding asm code as value
    global obj_dump
    for line in obj_dump:
        dump = re.split(":\W+", line)
        address = re.findall("\w+", line)
        obj_dict[address[0]] = dump[1]

def create_html():
    f = open('myprogram.html', 'w')
    path = str(subprocess.run(["pwd"], capture_output = True).stdout.decode('utf-8'))

    html_template = """<html>
    <head>
        <title>DISASSEMBLER</title>
        <style>
            table, th, td {border: 1px solid black;}
            table {width:100%; border-collapse: collapse;}
        </style>
    </head>
    <body>
        <h2>David Wang | CSC254 Disassembler Assignment</h2>
        <p>When and where the disassembler tool is used:</p>

        <p>"""+ str(datetime.datetime.now()) +"""</p>
        <p>""" + path + """ </p>
        <p>Let's compare the assembly code with the source c code</p>
        <p> The main method starts at: <a href=#"""+ main_loc +">" + main_loc+"""</a>
    """

    html_template += "<table>\n"
    
    html_template +=  """ <tr>
    <th> </th>
    <th>Assembly Code</th>
    <th>Source Code</th>
    </tr>
    """
    
    source_file_index = 0

    for file in dwarf_list:
        html_template += """ <tr>
        <td>""" + "<a href=./"+file[0][1:-1] +">" + file[0]+"</a>" + """</td>
        </tr>
        """
        # for each key in the dictionary
        last_line_num = 0
        used_line_dict = {}
        for key in file[1]:
            
            asm_code = obj_dict[key]
            st = re.search("j[a-z]*\s*([a-f0-9]*)", asm_code)
        
            if st is not None:
                st = st.group(1)
                replace_term = "<a href=#"+ st +">" + st+"</a>"
                asm_code = re.sub(st, replace_term, asm_code)

            html_template += """ <tr>
            <td>""" + "<a name="+ key +" href=#"+ key +">" + key+"</a>" +"""</td>
            <td>""" +  asm_code + """</td>
            """
            

            if file[1][key] != last_line_num:
                html_template += """
                <td>""" + "line: " + file[1][key] + """</td>"""
                html_template += """<td>"""
                if used_line_dict.get(file[1][key], False):
                    html_template += """<td style = "background-color: grey;">"""
                else:
                    html_template += """<td>"""
                html_template += source_code_lines[source_file_index][int(file[1][key])-1] +"""</td>
                """
                last_line_num = file[1][key]
                used_line_dict[file[1][key]] = True

            html_template += """
            </tr>
            """
        source_file_index += 1

    html_template += "</table>"

    html_template += """
    </body>
    </html>
    """
    f.write(html_template)
    f.close()
    # webbrowser.open('myprogram.html') 
    print("IT WORKS! The html file has been made.")

if __name__ == "__main__":
    get_dump_file(sys.argv[1:])
    get_c_files(sys.argv[1:])
    populate_obj_dict()
    create_html()
