Name: David Wang
Partner: None
Date: 11/7/21

USE GUIDE:
    
    Language used: Python3    

    - Running the program:
        1) In the command line type:
            python3 <script.py> <test_file1 test_file2 etc...>
                ex. python3 disassem.py test.c test1.c test2.c    

        2) The python script takes the names of the .c files as input.
           The script is able to compile the files and generate an 
           executeable by the name of 'myprogram'. As such, the html
           generated is called 'myprogram.html'. 

    - Functionality:
        - side-by-side comparison of assembly code (left) and c code (right)
        - links are included for all assembly lines (and for asm jump lines)
        - clicking on the name of the c files will open up the whole source code
          file.
        - repeated source code lines will be highlighted in grey.
        - you can find the main function my clicking on the link at the
          beginning blurb.
