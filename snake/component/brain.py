from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from snake.component.snake import Snake


class Neuron:
    def __init__(self, input_weights: list[float]) -> None:
        self.input_weights = input_weights
        self.output: float = 0

    # todo: write it
    def process(self, inputs: list[float]) -> None:
        pass


class OutputNeuron(Neuron):
    def __init__(self, input_weights: list[float], value: int) -> None:
        super().__init__(input_weights)
        self.value = value

    def __gt__(self, other: "OutputNeuron") -> bool:
        return self.output > other.output


class Brain:
    def __init__(self) -> None:
        self.layers: list[list[Neuron | OutputNeuron]] = []
        self.output = 0

    # todo: write it
    def load(self) -> None:
        inputs = [
            Neuron([0])
        ]
        outputs = [OutputNeuron([0], x) for x in range(-1, 2, 1)]
        self.layers = [
            inputs,
            outputs
        ]

    # todo: write it
    def save(self) -> None:
        pass

    def process(self, inputs: list[float]) -> None:
        for layer in self.layers:
            for neuron in layer:
                neuron.process(inputs)
            inputs = [x.output for x in layer]

        self.output = max(self.layers[-1]).value
