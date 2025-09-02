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

    @cluey.main('clean')
    def count_vowels(self, string: str, **kwargs) -> int:
        """Counts the number of vowels in the string."""
        
        string = self.clean(string, **kwargs).lower()

        result = sum(1 for character in string if character in 'aeiou')
        print("Vowels:", result)
        return result


if __name__ == "__main__":
    StringTools().main()