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

