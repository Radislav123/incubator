import math
import random
from typing import TYPE_CHECKING

import PIL.Image
import arcade.hitbox
import pymunk
from arcade import Sprite

from apps.deliverer.component.interest_point import InterestPoint
from apps.deliverer.settings import Settings
from core.texture import Texture


if TYPE_CHECKING:
    from apps.deliverer.view.simulation import SimulationView

Distances = tuple[float, float, float, float]
Position = tuple[float, float]


class Deliverer(Sprite):
    settings = Settings()
    physics_body: pymunk.Body

    default_radius = 10
    radius = default_radius
    default_mass = 10
    # todo: вынести в параметры
    power = 2000

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        self.departure: int = random.choices(range(len(self.view.interest_points)), k = 1)[0]
        self.destination: int | None = None

        self.max_cargo = 1
        self.cargo = 0

        image = PIL.Image.open(f"{self.settings.IMAGES_FOLDER}/circle_0.png")
        texture = Texture(image, hit_box_algorithm = arcade.hitbox.algo_detailed)
        position = list(self.view.interest_points[self.departure].position)
        angle = random.random() * math.pi * 2
        coeff = 1.5
        distance = (InterestPoint.radius + self.radius) * coeff
        position[0] = position[0] + distance * math.cos(angle)
        position[1] = position[1] + distance * math.sin(angle)
        super().__init__(texture, 1, position[0], position[1], angle, **kwargs)

        self.resize()
        self.update_physics()
        self.distances_cache: dict[position, Distances] = {}

    def update_physics(self) -> None:
        if self.physics_engines:
            self.view.physics_engine.remove_sprite(self)

        self.view.physics_engine.add_sprite(self, self.default_mass)
        self.physics_body = self.view.physics_engine.get_physics_object(self).body
        self.physics_body.velocity_func = self.velocity_callback

    def resize(self) -> None:
        scale = self.radius / sum(self.texture.size) * 4
        self.scale = scale

    # оригинал описан в PymunkPhysicsEngine.add_sprite
    def velocity_callback(
            self,
            body: pymunk.Body,
            gravity: tuple[float, float],
            damping: float,
            delta_time: float
    ) -> None:
        coeff = 100000 / InterestPoint.default_size
        for point in self.view.interest_points:
            distance_x, distance_y, distance_square, distance = self.count_distances(point.position)

            # чтобы не было рывков при коллизии
            if not (distance <= self.radius / 2 or distance <= point.radius):
                adding_gravity = point.size / distance_square
                adding_gravity_x = coeff * adding_gravity * distance_x / distance
                adding_gravity_y = coeff * adding_gravity * distance_y / distance

                gravity_x = gravity[0] + math.copysign(adding_gravity_x, point.center_x - self.center_x)
                gravity_y = gravity[1] + math.copysign(adding_gravity_y, point.center_y - self.center_y)

                gravity = (gravity_x, gravity_y)

        pymunk.Body.update_velocity(body, gravity, damping, delta_time)

    def count_distances(self, position: Position) -> Distances:
        rounded_position = (int(position[0]), int(position[1]))
        if rounded_position not in self.distances_cache:
            distance_x = position[0] - self.center_x
            distance_y = position[1] - self.center_y
            distance_square = math.pow(distance_x, 2) + math.pow(distance_y, 2)
            distance = math.sqrt(distance_square)
            self.distances_cache[rounded_position] = (distance_x, distance_y, distance_square, distance)
        return self.distances_cache[rounded_position]

    def choose_destination(self) -> None:
        max_size = max(x.size for x in self.view.interest_points)

        destinations = list(range(len(self.view.interest_points)))
        weights = [max_size - x.size for x in self.view.interest_points]
        destinations.remove(self.departure)
        weights = weights[:self.departure] + weights[self.departure + 1:]

        if len(destinations) > 0:
            self.destination = random.choices(destinations, weights)[0]
        else:
            self.destination = None

    def load_cargo(self) -> None:
        cargo = min(self.max_cargo - self.cargo, self.view.interest_points[self.departure].size)

        self.view.interest_points[self.departure].size -= cargo
        self.cargo += cargo
        self.physics_body.mass += cargo

    def unload_cargo(self) -> None:
        cargo = self.cargo

        self.view.interest_points[self.destination].size += cargo
        self.physics_body.mass -= cargo
        self.cargo -= cargo

    # https://www.desmos.com/calculator/mi9w8ny5we?lang=ru
    def apply_power(self, delta_time: float) -> None:
        point = self.view.interest_points[self.destination]
        distance_x, distance_y, distance_square, distance = self.count_distances(point.position)
        velocity = self.physics_body.velocity
        velocity_projection = (abs(velocity[0]) * abs(distance_x) + abs(velocity[1]) * abs(distance_y)) / distance
        velocity_len = math.dist(velocity, (0, 0))

        if distance != 0 and velocity_len != 0:
            velocity_cos = (velocity[0] * distance_x + velocity[1] * distance_y) / velocity_len / distance
            # ошибки округления дают cos > 1 и cos < -1
            velocity_cos = max(min(velocity_cos, 1), -1)
            angle = math.acos(velocity_cos)

            angle_threshold = math.pi / 3
            # доставщик приближается к точке
            if angle < angle_threshold:
                estimated_time = distance / velocity_projection
            # доставщик отдаляется от точки
            else:
                estimated_time = float("inf")

            acceleration_threshold = 3
            damping_threshold = 2
            threshold_offset = 1
            dumping_coeff = 0.1

            # постоянное ускорение
            if estimated_time >= acceleration_threshold + threshold_offset:
                acceleration_coeff = 1
            # ускорение
            elif estimated_time >= acceleration_threshold:
                acceleration_coeff = estimated_time - acceleration_threshold
            # постоянная скорость
            elif estimated_time >= damping_threshold:
                acceleration_coeff = 0
            # торможение
            elif estimated_time >= damping_threshold - threshold_offset:
                acceleration_coeff = (estimated_time - damping_threshold) * dumping_coeff
            # постоянное торможение
            else:
                acceleration_coeff = -1 * dumping_coeff
            acceleration_power = self.power * abs(acceleration_coeff)

            # проверка на то, что доставщик движется по орбите
            move_in_orbit = math.pi * 1 / 3 < angle < math.pi * 2 / 3
            # todo: вынести в параметры
            min_anti_orbit_power = 0.1
            # запасается мощность для орбитального торможения, если для разгона используется вся
            if move_in_orbit and abs(acceleration_coeff) > 1 - min_anti_orbit_power:
                acceleration_power *= 1 - min_anti_orbit_power

            adding_velocity = ((2 * acceleration_power * delta_time / self.physics_body.mass)**(1 / 2) *
                               math.copysign(1, acceleration_power))
            adding_velocity_x = adding_velocity / distance * distance_x
            adding_velocity_y = adding_velocity / distance * distance_y

            # орбитальное торможение
            if move_in_orbit:
                remaining_power = self.power - acceleration_power
                dumping_velocity = (2 * remaining_power * delta_time / self.physics_body.mass)**(1 / 2)
                dumping_velocity_x = dumping_velocity / velocity_len * -velocity[0]
                dumping_velocity_y = dumping_velocity / velocity_len * -velocity[1]

                adding_velocity_x += dumping_velocity_x
                adding_velocity_y += dumping_velocity_y

            self.physics_body.velocity = (
                self.physics_body.velocity[0] + adding_velocity_x,
                self.physics_body.velocity[1] + adding_velocity_y
            )

    def update_angle(self) -> None:
        point = self.view.interest_points[self.destination]
        vector = (point.center_x - self.center_x, point.center_y - self.center_y)
        axis = (1, 0)
        axis_length = 1

        distance_x, distance_y, distance_square, distance = self.count_distances(point.position)
        if distance != 0:
            cos = (vector[0] * axis[0] + vector[1] * axis[1]) / distance / axis_length
            # ошибки округления дают cos > 1 и cos < -1
            cos = max(min(cos, 1), -1)
            angle = math.acos(cos)
            if distance_y < 0:
                angle = math.pi * 2 - angle
            self.physics_body.angle = angle

    # noinspection PyMethodOverriding
    def on_update(self, delta_time: float) -> None:
        if self.destination is not None:
            self.update_angle()
            if self.collides_with_sprite(self.view.interest_point_zones[self.destination]):
                self.unload_cargo()
                self.departure = self.destination
                self.destination = None
            else:
                self.apply_power(delta_time)
        else:
            self.choose_destination()
            self.load_cargo()

        self.distances_cache = {}
