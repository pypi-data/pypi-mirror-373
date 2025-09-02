from torch import nn

from . import Model, blocks, manipulators


class GaussianModel(Model):
    def __init__(self):
        super().__init__(
            manipulators.SUM(
                Model(
                    blocks.MultiplyLayer(1, 1, False),
                    manipulators.Exp(),
                ),
            ),
            nn.Linear(1, 1, False)
        )
