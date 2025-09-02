==========
cluey
==========

.. start-badges

|pypi badge| |testing badge| |coverage badge| |docs badge| |black badge| |git3moji badge| |cluey badge|

.. |pypi badge| image:: https://img.shields.io/pypi/v/cluey?color=blue
   :alt: PyPI - Version
   :target: https://pypi.org/project/cluey/

.. |cluey badge| image:: https://img.shields.io/badge/cluey-B1230A.svg
    :target: https://rbturnbull.github.io/cluey/

.. |testing badge| image:: https://github.com/rbturnbull/cluey/actions/workflows/testing.yml/badge.svg
    :target: https://github.com/rbturnbull/cluey/actions

.. |docs badge| image:: https://github.com/rbturnbull/cluey/actions/workflows/docs.yml/badge.svg
    :target: https://rbturnbull.github.io/cluey
    
.. |black badge| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    
.. |coverage badge| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/rbturnbull/b84e24e6b58498cfcdd7f19388e111ad/raw/coverage-badge.json
    :target: https://rbturnbull.github.io/cluey/coverage/

.. |git3moji badge| image:: https://img.shields.io/badge/git3moji-%E2%9A%A1%EF%B8%8F%F0%9F%90%9B%F0%9F%93%BA%F0%9F%91%AE%F0%9F%94%A4-fffad8.svg
    :target: https://robinpokorny.github.io/git3moji/

.. end-badges

**Cluey - Command Line Utility for Engineers & You**

Build clever, class-based command line apps with minimal boilerplate

Documentation at https://rbturnbull.github.io/cluey/


.. start-quickstart

Installation
=======================

The software can be installed using ``pip``

.. code-block:: bash

    pip install cluey

To install the latest version from the repository, you can use this command:

.. code-block:: bash

    pip install git+https://github.com/rbturnbull/cluey.git

Documentation is available here: https://rbturnbull.github.io/cluey/

Your first Cluey CLI
=======================

Here is a minimal example of a Cluey CLI app:

.. code-block:: Python

    import cluey

    class GreetApp(cluey.Cluey):
        """A minimal Cluey CLI app"""

        @cluey.main
        def greet(self, name: str = cluey.Argument(..., help="")):
            """Greet a person by name"""
            print(f"Hello, {name}!")


    if __name__ == "__main__":
        GreetApp().main()


Then you can run this:

.. code-block:: bash

    python cluey/examples/greet.py --help

Which will display:

.. code-block:: bash

    ╭─ Arguments ─────────────────────────────────────────────────────────────────╮
    │ *    name      TEXT  The name of the person to greet [required]             │
    ╰─────────────────────────────────────────────────────────────────────────────╯
    ╭─ Options ───────────────────────────────────────────────────────────────────╮
    │ --version  -v        Show the version of this CLI                           │
    │ --help               Show this message and exit.                            │
    ╰─────────────────────────────────────────────────────────────────────────────╯

To run the app,

.. code-block:: bash

    python cluey/examples/cluey/examples/greet.py Alice

This will display:

.. code-block:: bash

    Hello, Alice!

Adding a flag
=================

.. code-block:: python

    import cluey

    class GreetApp(cluey.Cluey):
        """A minimal Cluey CLI app"""

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


To display the version of the app, run:

.. code-block :: bash

    python cluey/examples/greet.py --version
    # OR
    python cluey/examples/greet.py -v


Adding a second command
=======================

.. code-block:: python

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

Then you can run the following:

.. code-block :: bash
    
    python cluey/examples/arithmetic.py --help
    python cluey/examples/arithmetic.py add --help
    python cluey/examples/arithmetic.py subtract --help
    python cluey/examples/arithmetic.py add 3 2
    python cluey/examples/arithmetic.py subtract 3 2

Add options with defaults
=========================

.. code-block:: python

    import unicodedata
    import cluey


    class StringTools(cluey.Cluey):
        """ Does simple string functions """
        @cluey.main
        def lowercase(
            self,
            string: str = cluey.Argument(..., help="The string to process."),
        ) -> str:
            """Converts the string to lowercase."""
            string = string.lower()
            print(string)
            return string

        @cluey.main
        def clean(
            self, 
            string: str = cluey.Argument(..., help="The string to process."),
            strip_accents:bool = cluey.Option(False, help="Whether or not to strip accents."),
            ascii:bool = cluey.Option(False, help="Whether or not to include only ascii characters."),
        ) -> str:
            """Cleans the given string."""
            if strip_accents:
                string = ''.join(
                    character for character in unicodedata.normalize('NFKD', string)
                    if not unicodedata.combining(character)
                )
            
            if ascii:
                string = ''.join(character for character in string if character.isascii())
            
            print(string)
            return string


    if __name__ == "__main__":
        StringTools().main()    


Now the optional arguments can be set via the command line:

.. code-block:: bash

    python cluey/examples/stringtools.py clean "Café ☕️" --strip-accents --ascii

    Cafe


Call one method from another
============================

So far, all of the above could have been done more easily with Typer, but with Cluey, 
you are able to call one method from another and the function arguments get passed to the command line.

.. code-block:: python

    import unicodedata
    import cluey


    class StringTools(cluey.Cluey):
        """ Does simple string functions """

        @cluey.main
        def clean(
            self, 
            string: str = cluey.Argument(..., help="The string to process."),
            strip_accents:bool = cluey.Option(True, help="Whether or not to strip accents."),
            ascii:bool = cluey.Option(False, help="Whether or not to include only ascii characters."),
        ) -> str:
            """Cleans the given string."""
            if strip_accents:
                string = ''.join(
                    character for character in unicodedata.normalize('NFKD', string)
                    if not unicodedata.combining(character)
                )
            
            if ascii:
                string = ''.join(character for character in string if character.isascii())
            
            print(string)
            return string

        @cluey.main('clean')
        def count_vowels(self, string: str, **kwargs) -> int:
            """Counts the number of vowels in the string."""
            
            string = self.clean(string, **kwargs).lower()

            result = sum(1 for character in string if character in 'aeiou')
            print("Vowels:", result)
            return result


    if __name__ == "__main__":
        StringTools().main()


Now I can see that all the options for the ``clean`` command are available with ``count_vowels``:

.. code-block:: bash

    python cluey/examples/stringtools.py count-vowels --help

.. code-block:: bash
                                                                   
    Usage: stringtools.py count-vowels [OPTIONS] STRING               
                                                                    
    Counts the number of vowels in the string.                        
                                                                    
    ╭─ Arguments ─────────────────────────────────────────────────────╮
    │ *    string      TEXT  The string to process. [required]        │
    ╰─────────────────────────────────────────────────────────────────╯
    ╭─ Options ───────────────────────────────────────────────────────╮
    │ --strip-accents    --no-strip-accents      Whether or not to    │
    │                                            strip accents.       │
    │                                            [default:            │
    │                                            no-strip-accents]    │
    │ --ascii            --no-ascii              Whether or not to    │
    │                                            include only ascii   │
    │                                            characters.          │
    │                                            [default: no-ascii]  │
    │ --help                                     Show this message    │
    │                                            and exit.            │
    ╰─────────────────────────────────────────────────────────────────╯

.. code-block:: bash

    python cluey/examples/stringtools.py count-vowels "Café ☕️" --strip-accents

.. code-block:: bash

    Cafe
    Vowels: 2


Methods that are not commands
=============================

Not all methods need to be exposed as commands to the command-line interface.

.. code-block:: python

    import cluey

    class MLApp(cluey.Cluey):
        """A simple machine learning style CLI"""

        @cluey.method
        def get_batches(
            self,
            items: list[str] = cluey.Argument(..., help="List of items to process"),
            batch_size: int = cluey.Option(
                2,
                help="Batch size for training and evaluation"
            ),
        ):
            """Split items into batches (not a command)."""
            batches = [
                items[i:i + batch_size]
                for i in range(0, len(items), batch_size)
            ]
            return batches

        @cluey.main("get_batches")
        def train(self, **kwargs):
            """Train a model in batches."""
            batches = self.get_batches(**kwargs)
            print(f"Training on {len(batches)} batches")
            for batch in batches:
                print(f"Training on batch: {batch}")

        @cluey.main("get_batches")
        def evaluate(self, **kwargs):
            """Evaluate a model in batches."""
            batches = self.get_batches(**kwargs)
            print(f"Evaluating {len(batches)} batches:")
            for batch in batches:
                print(f"Evaluating on batch: {batch}")


    if __name__ == "__main__":
        MLApp().main()

Now all the arguments and options for ``get_batches`` are available with ``train`` and ``evaluate`` but ``get_batches`` isn't a command.

.. code-block:: bash

    $ python cluey/examples/ml.py --help

    Usage: ml.py [OPTIONS] COMMAND [ARGS]...                                              
                                                                                        
    ╭─ Options ───────────────────────────────────────────────────────────────────────────╮
    │ --help          Show this message and exit.                                         │
    ╰─────────────────────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ──────────────────────────────────────────────────────────────────────────╮
    │ evaluate   Evaluate a model in batches.                                             │
    │ train      Train a model in batches.                                                │
    ╰─────────────────────────────────────────────────────────────────────────────────────╯    

    $ python cluey/examples/ml.py train A B C D E
    Training on 3 batches
    Training on batch: ['A', 'B']
    Training on batch: ['C', 'D']
    Training on batch: ['E']

    $ python cluey/examples/ml.py evaluate F G H I J K L M --batch-size 3
    Evaluating 3 batches:
    Evaluating on batch: ['F', 'G', 'H']
    Evaluating on batch: ['I', 'J', 'K']
    Evaluating on batch: ['L', 'M']

Inheritance
===========

Cluey allows you to have base classes and inherit from them to build more complex CLIs.

.. code-block:: python

    import cluey
    from cluey.examples.ml import MLApp


    class ExtendedMLApp(MLApp):
        """Extends MLApp with an extra command"""

        @cluey.main("get_batches")
        def stats(self, **kwargs):
            """Show batch statistics."""
            batches = self.get_batches(**kwargs)
            sizes = [len(b) for b in batches]
            total = sum(sizes)
            print(f"{len(batches)} batches; sizes={sizes}; total_items={total}")


    if __name__ == "__main__":
        ExtendedMLApp().main()

This app contains all the commands of the base MLApp but it adds the extra ``stats`` command.

.. code-block:: bash

    $ python cluey/examples/extendedml.py --help

    Usage: extendedml.py [OPTIONS] COMMAND [ARGS]...                           
                                                                                
    ╭─ Options ────────────────────────────────────────────────────────────────╮
    │ --help          Show this message and exit.                              │
    ╰──────────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ───────────────────────────────────────────────────────────────╮
    │ evaluate   Evaluate a model in batches.                                  │
    │ stats      Show batch statistics.                                        │
    │ train      Train a model in batches.                                     │
    ╰──────────────────────────────────────────────────────────────────────────╯    

    $ python cluey/examples/extendedml.py stats A B C D E F G H I J K L M

    7 batches; sizes=[2, 2, 2, 2, 2, 2, 1]; total_items=13

Calling Super
=============

You can also override methods from the parent class and extend the arguments and options, without redefining the arguments from the ``super`` method.

.. code-block:: python

    import cluey
    from cluey.examples.ml import MLApp


    class ExtendedMLApp(MLApp):
        """Extends MLApp with an extra command"""

        @cluey.method('super')
        def get_batches(
            self,
            lowercase:bool=cluey.Option(False, help="Whether or not to lowercase items."),
            **kwargs,
        ):
            """Split items into batches and optionally lowercase them."""
            batches = super().get_batches(**kwargs)
            if lowercase:
                batches = [[item.lower() for item in batch] for batch in batches]
            return batches

        @cluey.main("get_batches")
        def stats(self, **kwargs):
            """Show batch statistics."""
            batches = self.get_batches(**kwargs)
            sizes = [len(b) for b in batches]
            total = sum(sizes)
            print(f"{len(batches)} batches; sizes={sizes}; total_items={total}")


    if __name__ == "__main__":
        ExtendedMLApp().main()


Adding executable script using Poetry
=====================================

If you use Poetry as your package manager, you can add an executable script to your project by modifying the `pyproject.toml` file:

.. code-block:: toml

    [tool.poetry.scripts]
    cluey-example-extendedml = "cluey.examples.extendedml:ExtendedMLApp.main"

This will create a command-line script named `cluey-example-extendedml` that runs the `ExtendedMLApp` application.


A separate tools CLI
====================

Sometimes you want your main app to be a single command CLI, but you also want to provide a separate CLI executable with several helper subcommands.


.. code-block:: python

    import cluey
    from cluey.examples.ml import MLApp


    class ProductionMLApp(MLApp):
        """Extends MLApp with an extra command"""

        @cluey.main("get_batches")
        def predict(self, **kwargs):
            """Predict using model in batches."""
            batches = self.get_batches(**kwargs)
            print(f"Evaluating {len(batches)} batches:")
            for batch in batches:
                print(f"Evaluating on batch: {batch}")

        @cluey.tool("super")
        def train(self, **kwargs):
            """Train the model."""
            return super().train(**kwargs)

        @cluey.tool("super")
        def evaluate(self, **kwargs):
            """Evaluate the model."""
            return super().evaluate(**kwargs)

        @cluey.tool()
        def cite(self, **kwargs):
            """Cite this model."""
            print("Please cite the paper: Turnbull, Robert, 'Cluey: A Command Line Utility for Engineers and You', Fantastic Journal (2025), 1–25.")


    if __name__ == "__main__":
        ProductionMLApp().main()

This overrides the ``train`` and ``evaluate`` commands to turn them into tools instead of being on the main CLI. Then it adds a new tool.
You can create executables for both the main app and the tools app using Poetry:

.. code-block:: toml

    [tool.poetry.scripts]
    cluey-example-productionml = "cluey.examples.productionml:ProductionMLApp.main"
    cluey-example-productionml-tools = "cluey.examples.productionml:ProductionMLApp.tools"

This allows the following:

.. code-block:: bash

    $ cluey-example-productionml predict --help
    Usage: cluey-example-productionml [OPTIONS] ITEMS...                                   
                                                                                            
    Predict using model in batches.                                                        
                                                                                            
    ╭─ Arguments ──────────────────────────────────────────────────────────────────────────╮
    │ *    items      ITEMS...  List of items to process [required]                        │
    ╰──────────────────────────────────────────────────────────────────────────────────────╯
    ╭─ Options ────────────────────────────────────────────────────────────────────────────╮
    │ --batch-size        INTEGER  Batch size for training and evaluation [default: 2]     │
    │ --help                       Show this message and exit.                             │
    ╰──────────────────────────────────────────────────────────────────────────────────────╯

    $ cluey-example-productionml-tools --help
    Usage: cluey-example-productionml-tools [OPTIONS] COMMAND [ARGS]...                    
                                                                                            
    ╭─ Options ────────────────────────────────────────────────────────────────────────────╮
    │ --help          Show this message and exit.                                          │
    ╰──────────────────────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ───────────────────────────────────────────────────────────────────────────╮
    │ cite       Cite this model.                                                          │
    │ evaluate   Evaluate the model.                                                       │
    │ predict    Predict using model in batches.                                           │
    │ train      Train the model.                                                          │
    ╰──────────────────────────────────────────────────────────────────────────────────────╯

.. end-quickstart

Credits
=======================

.. start-credits

Cluey was created created by `Robert Turnbull <https://robturnbull.com>`_ with contributions from Wytamma Wirth and Ashkan Pakzad.

.. end-credits