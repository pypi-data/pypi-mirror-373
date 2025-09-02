import cluey

class ArithmeticApp(cluey.Cluey):
    """ Does basic arithmetic """

    @cluey.main
    def add(
        self, 
        a: float = cluey.Argument(..., help="A value to start with."),
        b: float = cluey.Argument(..., help="A value to add."),
    ):
        """ Sums two values """
        print(a+b)

    @cluey.main
    def subtract(
        self, 
        a: float = cluey.Argument(..., help="A value to start with."),
        b: float = cluey.Argument(..., help="A value to sub."),
    ):
        """ Subtracts one value from another """
        print(a-b)


if __name__ == "__main__":
    ArithmeticApp().main()