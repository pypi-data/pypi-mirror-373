import cluey
from cluey.examples.ml import MLApp


class ProductionMLApp(MLApp):
    """Extends MLApp with an extra command"""

    @cluey.main("get_batches")
    def predict(self, **kwargs):
        """Predict using model in batches."""
        batches = self.get_batches(**kwargs)
        print(f"Predicting over {len(batches)} batches:")
        for batch in batches:
            print(f"Predicting on batch: {batch}")

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

