from apps.consumption.component.recipe import Recipe
from apps.consumption.service.unique import Unique


class Manufacturer(Unique):
    def __init__(self, recipes: list[Recipe]) -> None:
        self.recipes = recipes
