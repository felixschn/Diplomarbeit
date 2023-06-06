def _ac0():
    print("disabled ac0")


def _ac1():
    print("enabled ac1")

def _ac2():
    print("enabled ac2")


def ac(mode):
    match mode:
        case 0:
            _ac0()
        case 1:
            _ac1()
        case 2:
            _ac2()
        case _:
            print("cannot find ac mode")
