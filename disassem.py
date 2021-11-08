import subprocess
import webbrowser
import datetime
import sys
import os
import re

dwarf_dump = ""
obj_dump = []
source_code_lines = []

dwarf_dict = {}
####
dwarf_list = []
####
obj_dict = {}
source_dict = {}

def get_dump_file(argv): 
    
    # creates gcc arguments from command line file arguments
    argument_files = "gcc -g3 -o myprogram "
    for arg in argv:
        argument_files += arg + " "

    # compiles .c files with dump info
    compile_files = subprocess.check_call(argument_files, shell=True)
    
    # saves contents of dwarf-dump file as string 
    dwarf_dump_as_str = subprocess.run(["llvm-dwarfdump", "--debug-line", "myprogram"], capture_output = True).stdout.decode('utf-8')
    print(dwarf_dump_as_str)

    # cleans data from dwarf dump file to only include address and source code
    # file line number
    global dwarf_dump
    clean_up_dwarf_dump(dwarf_dump_as_str)

    #dwarf_dump = re.findall("0x\w{16}\s*[0-9]*", dwarf_dump_as_str)
    #print("Here's the output")
    #for i in dwarf_dump:
    #    print(i)
    # print(dwarf_dump)
    
    # saves contents of obj-dump file as string
    obj_dump_as_str = subprocess.run(["objdump", "-d", "myprogram"], capture_output = True).stdout.decode('utf-8')
    print(obj_dump_as_str)

    # cleans data from obj-dump to only include address and assembly code
    lines = re.split("\n", obj_dump_as_str)
    for line in lines:
        temp = re.findall("401\w{3}:.*", line)
        if len(temp) != 0:
            temp = re.sub("\\t", " ", line)
            obj_dump.append(temp)

    #for i in obj_dump:
    #    print(i)

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
                #address = re.findall("401\w+", line)
                address = re.search("0x0*([a-f0-9]*)", line).group(1)
                line_num = re.split("\s+", line)
                dic[address] = line_num[1]
            dwarf_list.append([file_name.group(), dic])

    #print("DUUUUMMMPP LIIISSSTTT")
    #for lst in dwarf_list:
    #    print(lst)


def get_c_files(argv):
    # Saves input .c files to a list by line number
    global source_code_lines
    for file in argv:
        f = open(file, 'r')
        text_file = f.read()
        source_code_lines.append(re.split("\n", text_file))
        
   # print("ICCCCCCCCCIIIIIIIII")
   # for i in source_code_lines:
   #     index = 1
   #     for j in i:
   #         print(index, j)
   #         index += 1
    # adds contents of each source code files to a dictionary using the file
    # name as key and the contents of the file as value
    

    # prints source code along with line numbers
    #for file in source_code_lines:
    #    index = 1
    #    for line in file:
    #        print(index, line)
    #        index += 1
         
def populate_dwarf_dict():
    print("hi1")
    # adds contents of dwarf_dump to a dictionary dwarf_dict using the asm
    # address as key and source code line number as value
    global dwarf_dict
    for line in dwarf_dump:
        # address = re.findall("401\w+", line)
        address = re.search("0*(\w)", line).group()
        print("address2", address)
        line_num = re.split("\s+", line)
        dwarf_dict[address[0]] = line_num[1]
    #print(dwarf_dict)

def populate_obj_dict():
    print("hi2")
    # adds contents of obj_dump to a dictionary obj_dict using asm address as
    # key and the corresponding asm code as value
    global obj_dump
    for line in obj_dump:
        dump = re.split(":\W+", line)
        address = re.findall("\w+", line)
        obj_dict[address[0]] = dump[1]
    #print(obj_dict)
    #for i in obj_dict:
    #    print(obj_dict[i])
        

#def populate_source_dict():
#    print("hi3")
#    for i in range(len(source_code_lines)):
#        source_dict[i+1] = source_code_lines[i]
#    print(source_dict)
#    for i in source_dict:
#        print(obj_dict[i])

def create_html():
    f = open('compare.html', 'w')
    html_template = """<html>
    <head>
        <title>DISASSEMBLER</title>
        <style>
            table, td {border: 1px solid black;}
            table {width:100%; border-collapse: collapse;}
            th {display: inline; text-align: left;}
        </style>
    </head>
    <body>
        <h2>Let's compare the source code with assembly</h2>
        <p>""" + str(datetime.datetime.now()) + """ </p>
        <p>blah blah blah blah blah blah blah blah blah blah</p>
    """

    html_template += "<table>\n"
    
    html_template +=  """ <tr>
    <th>Assembly Code</th>
    <th>Source Code</th>
    </tr>
    """
    print("HEEEEEEERRRRREEEEEE")
    #print(len(source_code_lines))
    #print(source_code_lines)
    #print(dwarf_dict.keys())
    #print(dwarf_dict.values())
    #print(obj_dict.keys())
    
    #for key in dwarf_dict:
    #    html_template +=  """ <tr>
    #    <th>""" + key + """</th>
    #    <th>""" +  obj_dict[key] + """</th>
    #    <th>""" + "line: " + dwarf_dict[key] + """</th>
    #    <th>""" + source_code_lines[int(dwarf_dict[key])-1] + """</th>
    #    </tr>
    #    """
    

    for file in dwarf_list:
        source_file_index = 0
        html_template += """ <tr>
        <th>""" + file[0] + """</th>
        </tr>
        """
       # for key in file[1]:
       #     print(len(source_code_lines[source_file_index]), file[1][key])
       # source_file_index += 1    
       # print("NEXT")
        # for each key in the dictionary
        last_line_num = 0
        for key in file[1]:
            
            asm_code = obj_dict[key]
            #print(asm_code) 
            #st = re.search("j[pqmnle].*([a-f0-9]*)", asm_code)
            st = re.search("j[a-z]*\s*([a-f0-9]*)", asm_code)
            #print("IIIICCCCCIIII")
        
            if st is not None:
                print(st.group(1))
                st = st.group(1)
                replace_term = "<a href=#"+ st +">" + st+"</a>"
                print(type(st))
                print(type(replace_term))
                asm_code = re.sub(st, replace_term, asm_code)

            html_template += """ <tr>
            <td>""" + "<a name="+ key +" href=#"+ key +">" + key+"</a>" +"""</td>
            <td>""" +  asm_code + """</td>
            <td>""" + "line: " + file[1][key] + """</td>
            """
            
            if file[1][key] != last_line_num:
                html_template += """
                <td>""" + source_code_lines[source_file_index][int(file[1][key])-1] +"""</td>
                """
                last_line_num = file[1][key]

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
    webbrowser.open('compare.html') 
    print("IT WORKS!")

if __name__ == "__main__":
    #get_dump_file(["test.c", "test1.c", "test2.c"])
    get_dump_file(sys.argv[1:])
    get_c_files(sys.argv[1:])
    #populate_dwarf_dict()
    populate_obj_dict()
    create_html()
