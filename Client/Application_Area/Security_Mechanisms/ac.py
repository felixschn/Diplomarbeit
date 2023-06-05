def ac0():
    print("disabled ac0")


def ac1():
    print("enabled ac1")

def ac2():
    print("enabled ac2")


def ac(mode):
    match mode:
        case 0:
            ac0()
        case 1:
            ac1()
        case 2:
            ac2()
        case _:
            print("cannot find ac mode")
