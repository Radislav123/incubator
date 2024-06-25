from typing import TYPE_CHECKING

import arcade.shape_list
from arcade.shape_list import ShapeElementList

from apps.snake.component.brain import Neuron
from apps.snake.service.color import Color
from apps.snake.settings import Settings
from apps.snake.ui.mixin import SnakeStyleButtonMixin
from core.service.functions import float_range
from core.texture import Texture
from core.ui.button.texture_button import TextureButton
from core.ui.layout.box_layout import BoxLayout
from core.ui.text.label import Label


if TYPE_CHECKING:
    from apps.snake.view.simulation import SimulationView


class NeuronMap(SnakeStyleButtonMixin, TextureButton):
    radius = 20
    default_textures: dict[float, Texture] = None

    output_step = 0.05
    outputs = list(float_range(*Neuron.output_borders, output_step))

    def __init__(self, neuron: Neuron, **kwargs) -> None:
        self.neuron = neuron
        texture = self.get_texture()
        super().__init__(width = texture.width, height = texture.height, texture = texture, **kwargs)

    def get_texture(self) -> Texture:
        if self.default_textures is None:
            self.__class__.default_textures = {}
            color_length = len(Color.NEURON_ACTIVE)
            color_difference = [Color.NEURON_ACTIVE[i] - Color.NEURON_SLEEP[i] for i in range(color_length)]

            for output in self.outputs:
                color = tuple(int(Color.NEURON_SLEEP[i] + color_difference[i] * output) for i in range(color_length))
                texture = Texture.create_circle(self.radius, color = color)
                self.__class__.default_textures[output] = texture

        nearest_key = min(self.default_textures, key = lambda key: abs(key - self.neuron.output))
        return self.default_textures[nearest_key]

    def update_texture(self) -> None:
        texture = self.get_texture()
        if self.texture != texture:
            self.texture = texture


class LayerLabel(SnakeStyleButtonMixin, Label):
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(
            text = text,
            width = NeuronMap.radius,
            height = NeuronMap.radius,
            color = Color.NORMAL,
            **kwargs
        )


class BrainMap(BoxLayout):
    settings = Settings()
    gap = (20, 40, 20, 40)
    space_between_layers = 50
    space_between_neurons = 20

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        self.brain = self.view.released_arena.snake.brain
        self.all_neuron_maps = []
        layer_maps = []
        for layer in self.brain.layers:
            neuron_maps: list[NeuronMap | Label] = [NeuronMap(neuron) for neuron in layer]
            self.all_neuron_maps.extend(neuron_maps)

            label = LayerLabel(str(len(neuron_maps)))
            neuron_maps.insert(0, label)

            layer_map = BoxLayout(children = neuron_maps, space_between = self.space_between_neurons)
            layer_maps.append(layer_map)

        super().__init__(vertical = False, children = layer_maps, space_between = self.space_between_layers, **kwargs)
        self.with_padding(top = self.gap[0], right = self.gap[1], bottom = self.gap[2], left = self.gap[3])
        self.fit_content()
        self.with_background(
            texture = Texture.create_rounded_rectangle(
                self.size,
                color = Color.NORMAL,
                border_color = Color.BORDER
            )
        )

        self.synapses = ShapeElementList()
        self.prepare_synapses()

    def prepare_synapses(self) -> None:
        layers = self.children
        layers_space = self.space_between_layers
        neurons_space = self.space_between_neurons
        radius = NeuronMap.radius
        diameter = radius * 2
        synapse_width = 0.7
        max_layer = max(len(x.children) for x in layers)

        for index, neuron in enumerate(layers[0].children[1:]):
            x_0 = self.gap[3] // 2
            x_1 = self.gap[3]
            y = (self.view.window.height - radius - self.gap[1] - neurons_space
                 - (diameter + neurons_space) * (index + (max_layer - len(layers[0].children)) / 2))
            neuron: NeuronMap
            color = self.get_synapse_color(neuron.neuron.input_weights[0])
            synapse = arcade.shape_list.create_line(x_0, y, x_1, y, color, synapse_width * 1.2)
            self.synapses.append(synapse)

        for layer_index in range(len(layers) - 1):
            layer_0 = layers[layer_index]
            layer_1 = layers[layer_index + 1]
            for index_0, _ in enumerate(layer_0.children[1:]):
                x_0 = self.gap[3] + diameter + (diameter + layers_space) * layer_index
                x_1 = self.gap[3] + (diameter + layers_space) * (layer_index + 1)
                y_0 = (self.view.window.height - radius - self.gap[1] - neurons_space
                       - (neurons_space + diameter) * (((max_layer - len(layer_0.children)) / 2) + index_0))
                for index_1, neuron_1 in enumerate(layer_1.children[1:]):
                    y_1 = (self.view.window.height - radius - self.gap[1] - neurons_space
                           - (neurons_space + diameter) * (((max_layer - len(layer_1.children)) / 2) + index_1))
                    neuron_1: NeuronMap
                    color = self.get_synapse_color(neuron_1.neuron.input_weights[index_0])
                    synapse = arcade.shape_list.create_line(x_0, y_0, x_1, y_1, color, synapse_width)
                    self.synapses.append(synapse)

    @staticmethod
    def get_synapse_color(weight: float) -> list[int]:
        color_length = len(Color.SYNAPSE_NEUTRAL)
        color_difference_positive = [Color.SYNAPSE_POSITIVE[i] - Color.SYNAPSE_NEUTRAL[i] for i in range(color_length)]
        color_difference_negative = [Color.SYNAPSE_NEGATIVE[i] - Color.SYNAPSE_NEUTRAL[i] for i in range(color_length)]
        if weight >= 0:
            color = [int(Color.SYNAPSE_NEUTRAL[i] + color_difference_positive[i] * weight / Neuron.weight_borders[1])
                     for i in range(color_length)]
        else:
            color = [int(Color.SYNAPSE_NEUTRAL[i] + color_difference_negative[i] * weight / Neuron.weight_borders[0])
                     for i in range(color_length)]
        return color
