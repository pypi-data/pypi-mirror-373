import easy_subprocess

def test():    
    with easy_subprocess.EasyPopen("cmd", encoding = "oem", print_output = True, initial_output = True) as console:
        console.send_input("C:")
        console.send_input("cd C:\\")
        console.send_input("dir")


def test2():    
    with easy_subprocess.EasyPopen("program.py", print_output = True) as program:
        program.send_input("hello1")
        program.send_input("hello2")
        program.send_input("hello3")

    
print("Executing test1() ...")
test()
print()
print("Executing test2() ...")
test2()
