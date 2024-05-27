import inspect
import random
import sys
from typing import Self


class Neuron:
    max_mutation_spread = 0.1
    weight_borders = [-1, 1]

    def __init__(self, input_weights: list[float]) -> None:
        self.input_weights = input_weights
        self.input_weights_sum = sum(self.input_weights)
        self.output: float = 0

    def process(self, inputs: list[float]) -> None:
        self.output = sum(inputs) / len(inputs) / self.input_weights_sum

    def dump(self) -> dict:
        data = {key: value for key, value in self.__dict__.items()
                if key in inspect.signature(self.__class__).parameters}
        data["class"] = self.__class__.__name__
        return data

    @classmethod
    def load(cls, dictionary: dict) -> Self:
        return cls(**dictionary)

    @classmethod
    def mutate_input_weight(cls, weight: float) -> float:
        new_weight = weight + random.uniform(-cls.max_mutation_spread, cls.max_mutation_spread)
        new_weight = max(new_weight, cls.weight_borders[0])
        new_weight = min(new_weight, cls.weight_borders[1])
        return new_weight

    def mutate(self) -> Self:
        return self.__class__([self.mutate_input_weight(weight) for weight in self.input_weights])


class OutputNeuron(Neuron):
    def __init__(self, input_weights: list[float], value: int) -> None:
        super().__init__(input_weights)
        self.value = value

    def __gt__(self, other: "OutputNeuron") -> bool:
        return self.output > other.output


class Brain:
    def __init__(self) -> None:
        self.layers: list[list[Neuron | OutputNeuron]] = []
        self.output: float = 0

    def dump(self) -> list[list[dict]]:
        return [[neuron.dump() for neuron in layer] for layer in self.layers]

    @classmethod
    def load(cls, data: list[list[dict]]) -> Self:
        brain = cls()
        for layer_description in data:
            layer = []
            brain.layers.append(layer)
            for neuron_description in layer_description:
                neuron_class = getattr(sys.modules[__name__], neuron_description.pop("class"))
                neuron = neuron_class(**neuron_description)
                layer.append(neuron)
        return brain

    def process(self, inputs: list[float]) -> None:
        for layer in self.layers:
            for neuron in layer:
                neuron.process(inputs)
            inputs = [x.output for x in layer]

        self.output = max(self.layers[-1]).value

    def mutate(self) -> Self:
        new_brain = self.__class__()
        new_brain.layers = [[neuron.mutate() for neuron in layer] for layer in self.layers]
        return new_brain
