def fw0():
    print("disabled fw0")


def fw1():
    print("enabled fw1")


def fw2():
    print("enabled fw2")


def fw3():
    print("enabled fw3")


def fw(mode):
    match mode:
        case 0:
            fw0()
        case 1:
            fw1()
        case 2:
            fw2()
        case 3:
            fw3()
        case _:
            print("cannot find fw mode")
