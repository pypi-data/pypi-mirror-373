import cluey

class GreetApp(cluey.Cluey):
    """ A friendly app to greet you. """

    @cluey.main
    def greet(self, name: str = cluey.Argument(..., help="The name of the person to greet")):
        """Greet a person by name"""
        print(f"Hello, {name}!")

    @cluey.flag(shortcut="-v")
    def version(self) -> str:
        """Show the version of this CLI"""
        return "GreetApp version 0.1.0"


if __name__ == "__main__":
    GreetApp().main()