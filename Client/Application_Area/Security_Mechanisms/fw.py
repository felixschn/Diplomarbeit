def _fw0():
    print("disabled fw0")


def _fw1():
    print("enabled fw1")


def _fw2():
    print("enabled fw2")


def _fw3():
    print("enabled fw3")


def fw(mode):
    match mode:
        case 0:
            _fw0()
        case 1:
            _fw1()
        case 2:
            _fw2()
        case 3:
            _fw3()
        case _:
            print("cannot find fw mode")
