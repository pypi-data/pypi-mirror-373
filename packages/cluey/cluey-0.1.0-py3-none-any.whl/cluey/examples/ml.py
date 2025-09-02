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
