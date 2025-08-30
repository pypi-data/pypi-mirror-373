# PYPI readme_en.md

Matrix HDL is a tool that aggregates Verilog RTL code in a matrix style. It helps users build and develop the hierarchy of Verilog RTL code using a spreadsheet. Therefore, this tool can convert Verilog RTL code to and from spreadsheets. Due to this feature, Matrix HDL can serve as an entry point for AI to interpret Verilog RTL code, enabling users to input the hierarchical relationships of Verilog RTL to AI tools for interpretation.

It uses three Python scripts to convert Verilog RTL code:
    
1. mh_hyperlink:  This script adds hyperlinks to the code aggregation in spreadsheet format. Modules and sub - modules on each sheet page can be automatically navigated to the upper or lower level via hyperlinks. Simply follow it with the .xlsx file.
    
    Example: (code.xlsx is the generated file without hyperlink relationships. Running the following script will add hyperlinks to module names and sub - module names) 
    ```
    mh_hyperlink code.xlsx
    ```
    
2. mh_export: This script exports the code aggregation in spreadsheet format to .v files.
    - -single:  If this parameter is provided, the code will be exported to a single .v file, and the file name is given by -o. If not provided, the code will be exported to a directory, and the directory name is given by -o, with one sheet page corresponding to one .v file.
    - -o：Specifies the directory name or file name.
    
    Examples:
    ```
    mh_export code.xlsx -single -o top  #top.v
    mh_export code.xlsx -o top   #top/ xxx.v etc
    ```
    
3. mh_ports: This script imports the ports of .v files into the special page @module of the .xlsx file (this page lists a module name and its ports in each column, and the description of this module will not appear in the .xlsx file). If it's a single .v file, you can directly follow it with this .v file. For batch import, use the -f or -v option.
    
    -o :  Specifies the .xlsx file that accepts the import. It only modifies the @module page. If the module name exists, it will be updated; if not, a new column will be added at the end.
    
    -f : Followed by a list file. When you need to import multiple files, you can list them in this file.
    
    -v: Followed by a directory name. It will automatically search for .v files in this directory.
    
   Examples:    
    ```
    mh_ports uart.v -o code.xlsx
    mh_export -v code/ -o code.xlsx
    ```

Please install the matrixhdl package and execute these three scripts to convert spreadsheet format to Verilog RTL code.


# PYPI readme_zh.md

Matrix HDL是一个采用矩阵的方式来聚合Verilog RTL代码的工具。它会帮助用户采用Spreadsheet来进行Verilog RTL代码的hierarchy的搭建和开发。因此，本工具会实现Verilog RTL代码到Spreadsheet之间的转换。正因为有此特点，Matrix HDL可以成为AI解读Verilog RTL代码的入口，能够帮助用户把Verilog RTL的层级关系，输入给AI工具进行解读。

它采用3个python脚本来实现对Verilog RTL代码的转换。
  
1. mh_hyperlink: 它用来对spreadsheet格式的代码聚合加上超链接。每一个sheet页面的模块和子模块可以通过超链接自动导览到上一级或者下一级。后面直接跟上.xlsx文件。
    
    举例：(code是生成的.xlsx文件，但它没有超链接关系，执行下面的脚本，可以为模块名和子模块名增加超链接）
    ```python
    mh_hyperlink code.xlsx
    ```
    
2. mh_export: 它用来对spreadsheet格式的代码聚合导出.v的文件格式。
    - -single:  如果带有这个参数，那么会导出到一个.v文件，文件名由-o给出；如果没有这个参数，那么会导出到一个目录下，目录名由-o给出，一个sheet页面对应一个.v文件。
    - -o：指定目录名或者文件名。
    
    举例：
    ```python
    mh_export code.xlsx -single -o top  #top.v
    mh_export code.xlsx -o top   #top/ xxx.v etc
    ```
    
3. mh_ports: 它导入.v文件的端口到.xlsx文件的特殊页面@module（这一页面每一列列出一个模块名和它的端口，.xlsx文件不会出现这一模块的描述）。如果是单个.v文件，可以直接跟上这一个.v文件，如果批量导入，使用-f或者-v选项。
    
    -o :  指定接受导入的.xlsx文件，它只会修改@module页面。如果模块名存在，那么进行更新；如果不存在，会在最后增加一列）
    
    -f : 跟上列表文件。当需要导入多个文件时，可以在文件列表里面给出。
    
    -v: 跟上目录名。它会自动搜寻这一目录下的.v文件。
    
    举例：
    ```python
    mh_ports uart.v -o code.xlsx
    mh_export -v code/ -o code.xlsx
    ```

请安装matrixhdl文件，执行这三个脚本，来实现对spreadsheet格式转换为verilog RTL代码。