import copy
import inspect
import random
import sys
from typing import Self


NeuronDescription = dict[str, list[float] | str]
LayerDescription = list[NeuronDescription]
BrainDescription = dict[str, list[LayerDescription] | str | int]


class Neuron:
    max_mutation_spread = 0.1
    weight_borders = [-1, 1]
    output_borders = [0, 1]

    def __init__(self, input_weights: list[float], *args, **kwargs) -> None:
        self.input_weights = input_weights
        self.inputs_amount = len(self.input_weights)
        self.output: float = 0

    def __hash__(self) -> int:
        return hash(sum(hash(x) for x in self.input_weights))

    @classmethod
    def get_default(cls, input_weights: list[float], *args, **kwargs) -> Self:
        return cls(input_weights, *args, **kwargs)

    def process(self, inputs: list[float]) -> None:
        value = sum(inputs[x] * self.input_weights[x] for x in range(self.inputs_amount))
        if value > 1:
            self.output = 1
        else:
            self.output = 0

    def dump(self) -> dict:
        data = {key: value for key, value in self.__dict__.items()
                if key in inspect.signature(self.__class__).parameters}
        data["class"] = self.__class__.__name__
        return data

    @classmethod
    def load(cls, dictionary: NeuronDescription) -> Self:
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
    def __init__(self, input_weights: list[float], value: int, *args, **kwargs) -> None:
        super().__init__(input_weights, *args, **kwargs)
        self.value = value

    def __hash__(self) -> int:
        return hash(sum(hash(x) for x in self.input_weights) + hash(self.value))

    def __gt__(self, other: "OutputNeuron") -> bool:
        return self.output > other.output

    def mutate(self) -> Self:
        return self.__class__([self.mutate_input_weight(weight) for weight in self.input_weights], self.value)


class Brain:
    def __init__(self, generation: int, name: str | None = None) -> None:
        self.layers: list[list[Neuron | OutputNeuron]] = []
        self.output: float = 0
        self.generation = generation
        self.name = name

    def __hash__(self) -> int:
        return hash(sum(hash(y) for x in self.layers for y in x))

    @classmethod
    def get_default(cls) -> Self:
        input_neuron = {
            "input_weights": [0],
            "class": Neuron.__name__
        }
        input_layer = [copy.deepcopy(input_neuron) for _ in range(9)]

        output_neuron = {
            "input_weights": [0] * len(input_layer),
            "class": OutputNeuron.__name__
        }
        output_layer = [copy.deepcopy(output_neuron) for _ in range(3)]
        for index, neuron in enumerate(output_layer):
            neuron["value"] = index - len(output_layer) // 2

        description = {
            "layers": [input_layer, output_layer],
            "generation": 0
        }
        brain = cls.load(description)
        return brain

    def dump(self) -> BrainDescription:
        data = {
            "layers": [[neuron.dump() for neuron in layer] for layer in self.layers],
            "generation": self.generation
        }
        if self.name is not None:
            data["name"] = self.name
        return data

    @classmethod
    def load(cls, data: dict) -> Self:
        generation = data["generation"]
        if "name" in data:
            name = data["name"]
        else:
            name = None
        brain = cls(generation, name)

        for layer_description in data["layers"]:
            layer = []
            brain.layers.append(layer)
            for neuron_description in layer_description:
                neuron_class = getattr(sys.modules[__name__], neuron_description.pop("class"))
                neuron = neuron_class(**neuron_description)
                layer.append(neuron)
        return brain

    def process(self, inputs: list[float]) -> None:
        for index, neuron in enumerate(self.layers[0]):
            neuron.process(inputs[index: index + 1])
        inputs = [x.output for x in self.layers[0]]

        for layer in self.layers:
            for neuron in layer:
                neuron.process(inputs)
            inputs = [x.output for x in layer]

        self.output = max(self.layers[-1]).value

    def mutate(self) -> Self:
        new_brain = self.__class__(self.generation, self.name)
        new_brain.layers = [[neuron.mutate() for neuron in layer] for layer in self.layers]
        return new_brain

    @property
    def save_name(self) -> str:
        if self.name is not None:
            name = self.name
        else:
            name = hash(self)
        return f"{name}_{self.generation}.json"
