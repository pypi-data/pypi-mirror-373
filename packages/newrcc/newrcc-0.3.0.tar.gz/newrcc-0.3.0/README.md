# NewRcc

---
## Logo

---
![图片](newrcc/resource/Logo.jpg)
## Welcome

---
Welcome to view this instruction document. This is a 
toolkit that can make the output of your console more
beautiful. It not only supports controlling the 
**text style** of the output in your console, but also
supports conveniently helping you quickly build console
**progress bars** with multiple styles. Come and install
it and try to beautify the console of your project.

**Installation Guide**

First, make sure that the pip package management tool 
of Python has been installed on your 
computer.

Then enter the following command in the console.
```
pip install newrcc
```
## Quick Start

---

```python
# Import several important members in the NewRcc package.
from newrcc.c_color import TextColor
import newrcc.c_console

"""
Use the colorfulText function in CConsole to convert 
ordinary text into colorful text.
"""
print(CConsole.ctext("Hello NewRcc!", TextColor.GREEN))

"""
Directly use the printColorfulText function in CConsole
 to print colorful text in the console.
"""
CConsole.printColorfulText("Hello NewRcc!", TextColor.BLUE)

"""
Use the ProcessBar class in CConsole to construct a progress 
bar object.
"""
process_bar = CConsole.ProcessBar("Start", "End", ...)

"""
Use the draw function of the ProcessBar class to draw the image
of a certain progress point, and use the erase function to clear 
the last drawing. 
Reasonably use these two functions in an operation process to 
achieve real-time progress display effect.
"""
process_bar.draw()
process_bar.erase()
```
## Detailed Documentation

---
For more detailed explanation documents, please visit the link: [Detail Doc ](https://#) .
## Function Features

---
- It can run normally on systems that support 
[ANSI escape sequences](https://baike.baidu.com/item/ANSI转义序列/22735729?fr=ge_ala).
- When it encounters an exception during operation, 
it will uniformly throw the `_CError` exception class 
in CError, which is inherited from `Exception`.
- It supports most common colors, including red, yellow, 
blue, green, cyan, purple, and gray. At the same time, 
it also supports [RGB color](https://baike.baidu.com/item/RGB/342517?fr=ge_ala) codes to create objects 
of the `Color` class in CColor. For specific operations, 
please refer to the [Detailed Documentation](#detailed-documentation).
- It supports other text styles besides text color, such 
as **bold**, *italic*, <u>underline</u>, ~~middleline~~, etc.
- For other features, please refer to the 
[Detail Documentation](#detailed-documentation).
## Developer Contact Information

---
**RestRegular**

  **email**： [3228097751@qq.com](https://www.qq.com)
  
  **GitHub**： [RestRegular](https://github.com/RestRegular)
##  Known Issues and Limitations

---
At present, the function of quickly building a table in 
the console has been initially completed, but it is still 
immature. **The known problem is that cells cannot span rows.**
<p style="color: red; font-style: italic;">
Warning: Do not use the row-spanning function in the table.
</p>

## Version _NewRcc-0.1.4_

---
**Contents of This Version Update**
1. A _README.md_ file has been added. 
2. A project logo has been added. 
3. Some potential problems have been found and marked in the README.md file.
4. A display error of README.md file has been fixed.

## Author

---
**RestRegular**

## Special Thanks

---
Waiting for occupancy. ^_^ 

