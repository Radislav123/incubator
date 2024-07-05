from apps.consumption.service.unique import Unique


class ProductType(Unique):
    def __init__(self, name: str, components: list["ProductType"] | None = None) -> None:
        self.name = name

        if components is None:
            self.components = []
            self.volume = 1
            self.mass = 1
        else:
            self.components = components
            self.volume = sum(x.volume for x in self.components)
            self.mass = sum(x.mass for x in self.components)


class Product:
    def __init__(self, product_type: ProductType, amount: int) -> None:
        self.product_type = product_type
        self.amount = amount
        self.volume = self.product_type.volume * self.amount
        self.mass = self.product_type.mass * self.amount
