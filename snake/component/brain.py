import inspect
import sys
from typing import Self


class Neuron:
    def __init__(self, input_weights: list[float]) -> None:
        self.input_weights = input_weights
        self.output: float = 0

    # todo: write it
    def process(self, inputs: list[float]) -> None:
        pass

    def dump(self) -> dict:
        data = {key: value for key, value in self.__dict__.items()
                if key in inspect.signature(self.__class__).parameters}
        data["class"] = self.__class__.__name__
        return data

    @classmethod
    def load(cls, dictionary: dict) -> Self:
        return cls(**dictionary)


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
