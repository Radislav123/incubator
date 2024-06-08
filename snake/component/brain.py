import inspect
import json
import math
import random
import sys
from typing import Callable, Self


NeuronDescription = dict[str, list[float] | str | float]
LayerDescription = list[NeuronDescription]
BrainDescription = dict[str, list[LayerDescription] | str | int]


# https://www.mathway.com/ru/Graph
class FunctionsMixin:
    max_mutation_spread: float
    weight_borders: list[int]
    output_borders: list[int]

    input_weights: list[float]
    inputs_amount: int

    def adder(self, inputs: list[float]) -> float:
        return sum(inputs[x] * self.input_weights[x] for x in range(self.inputs_amount))

    # https://ru.wikipedia.org/wiki/%D0%A1%D0%B8%D0%B3%D0%BC%D0%BE%D0%B8%D0%B4%D0%B0
    def sigmoid(self, inputs: list[float]) -> float:
        input_value = self.adder(inputs)
        # чем больше t, тем круче подъем
        t = 8
        return 1 / (1 + math.e**(-t * input_value))

    # https://pytorch.org/docs/stable/generated/torch.nn.ELU.html
    def elu(self, inputs: list[float]) -> float:
        input_value = self.adder(inputs)
        if input_value > 0:
            value = input_value
        else:
            alpha = 1
            value = alpha * (math.exp(input_value) - 1) + 1
        return value


class Neuron(FunctionsMixin):
    max_mutation_spread = 0.1
    weight_borders = [-1, 1]
    output_borders = [0, 1]
    function: Callable[[list[float]], float]
    output_history_length = 100

    def __init__(self, input_weights: list[float], *args, **kwargs) -> None:
        self.input_weights = input_weights
        self.inputs_amount = len(self.input_weights)
        self.output_history: list[float] = [0 for _ in range(self.output_history_length)]

    def __hash__(self) -> int:
        return hash(sum(hash(x) for x in self.input_weights))

    def process(self, inputs: list[float]) -> None:
        output = self.function(inputs)
        self.output_history = [output, *self.output_history[:self.output_history_length - 1]]

    def dump(self) -> dict:
        data = {key: value for key, value in self.__dict__.items()
                if key in inspect.signature(self.__class__).parameters}
        data["max_mutation_spread"] = self.max_mutation_spread
        data["weight_borders"] = self.weight_borders
        data["output_borders"] = self.output_borders
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

    @classmethod
    def get_default_description(cls, inputs_amount: int, *args, **kwargs) -> NeuronDescription:
        description = {
            "input_weights": [0 for _ in range(inputs_amount)],
            "class": cls.__name__
        }
        return description

    @property
    def output(self) -> float:
        return self.output_history[0]


class FeedbackNeuron(Neuron):
    history_depth = 1

    @classmethod
    def get_default_description(cls, inputs_amount: int, *args, **kwargs) -> NeuronDescription:
        return super().get_default_description(inputs_amount + cls.history_depth, *args, **kwargs)

    def process(self, inputs: list[float]) -> None:
        super().process([*inputs, *self.output_history[:self.history_depth]])


class InputNeuron(Neuron):
    function = FunctionsMixin.sigmoid


class InnerNeuron(Neuron):
    function = FunctionsMixin.sigmoid


class OutputNeuron(Neuron):
    function = FunctionsMixin.sigmoid

    def __init__(self, input_weights: list[float], value: int, *args, **kwargs) -> None:
        super().__init__(input_weights, *args, **kwargs)
        self.value = value

    def __hash__(self) -> int:
        return hash(sum(hash(x) for x in self.input_weights) + hash(self.value))

    def __gt__(self, other: "OutputNeuron") -> bool:
        return self.output > other.output

    def mutate(self) -> Self:
        return self.__class__([self.mutate_input_weight(weight) for weight in self.input_weights], self.value)

    # noinspection PyMethodOverriding
    @classmethod
    def get_default_description(cls, inputs_amount: int, value: int, *args, **kwargs) -> NeuronDescription:
        description = super().get_default_description(inputs_amount, *args, **kwargs)
        description["value"] = value
        return description


class Brain:
    file_extension = "brain"
    default_score = 0.0

    def __init__(self, generation: int, score: float = default_score, name: str | None = None) -> None:
        self.layers: list[list[Neuron | OutputNeuron]] = []
        self.output: float = 0
        self.generation = generation
        self.score = score
        self.age = 0
        self._name = name
        self.loading_dict: BrainDescription | None = None

    def __hash__(self) -> int:
        return hash(sum(hash(y) for x in self.layers for y in x))

    @classmethod
    def get_default(cls) -> Self:
        input_len = 9
        output_len = 3
        inner_layer_lens = [(input_len + output_len) // 2]
        input_layer = [InputNeuron.get_default_description(1) for _ in range(input_len)]

        previous_layer_len = input_len
        inner_layers = []
        for layer_len in inner_layer_lens:
            layer = [InnerNeuron.get_default_description(previous_layer_len) for _ in range(layer_len)]
            inner_layers.append(layer)
            previous_layer_len = layer_len

        output_layer = [OutputNeuron.get_default_description(previous_layer_len, value - output_len // 2)
                        for value in range(output_len)]
        # перемещает нейрон, отвечающий за движение прямо, на первое место,
        # чтобы змеи изначально двигались прямо, а не по кругу
        output_layer.insert(0, output_layer.pop(output_len // 2))

        description = {
            "layers": [input_layer, *inner_layers, output_layer],
            "generation": 0,
            "score": cls.default_score
        }
        brain = cls.load(description)
        return brain

    def dump(self, **kwargs) -> BrainDescription:
        data = {
            "layers": [[neuron.dump() for neuron in layer] for layer in self.layers],
            "generation": self.generation,
            "score": self.score
        }
        if self.name is not None:
            data["name"] = self.name
        data.update(kwargs)
        return data

    def dump_to_file(self, path: str, **kwargs) -> None:
        with open(path, 'w') as file:
            json.dump(self.dump(**kwargs), file, indent = 4)

    @classmethod
    def load(cls, data: dict) -> Self:
        generation = data["generation"]
        if "name" in data:
            name = data["name"]
        else:
            name = None
        score = data["score"]

        brain = cls(generation, score, name)
        brain.loading_dict = data

        for layer_description in data["layers"]:
            layer = []
            brain.layers.append(layer)
            for neuron_description in layer_description:
                neuron_class = getattr(sys.modules[__name__], neuron_description.pop("class"))
                neuron = neuron_class(**neuron_description)
                layer.append(neuron)
        return brain

    @classmethod
    def load_from_file(cls, path: str) -> Self:
        with open(path, 'r') as file:
            brain = cls.load(json.load(file))
        return brain

    def process(self, inputs: list[float]) -> None:
        for index, neuron in enumerate(self.layers[0]):
            neuron.process(inputs[index: index + 1])
        inputs = [x.output for x in self.layers[0]]

        for layer in self.layers[1:]:
            for neuron in layer:
                neuron.process(inputs)
            inputs = [x.output for x in layer]

        self.output = max(self.layers[-1]).value

    def mutate(self) -> Self:
        new_brain = self.__class__(self.generation, self.default_score, self.name)
        new_brain.layers = [[neuron.mutate() for neuron in layer] for layer in self.layers]
        return new_brain

    @property
    def name(self) -> str:
        if self._name is None:
            name = str([len(x) for x in self.layers])
        else:
            name = self._name
        return name

    @property
    def save_name(self) -> str:
        return f"{hash(self)}.{self.file_extension}"

    @property
    def pretty_score(self) -> float:
        return round(self.score, 3)
