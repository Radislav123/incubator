from apps.consumption.component.product import ProductType
from apps.consumption.service.unique import Unique


class Recipe(Unique):
    def __init__(self, inputs: list[ProductType], outputs: list[ProductType]) -> None:
        self.inputs = inputs
        self.outputs = outputs
