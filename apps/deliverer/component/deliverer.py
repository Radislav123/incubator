import math
import random
from typing import TYPE_CHECKING

import PIL.Image
import arcade.hitbox
import pymunk
from arcade import Sprite

from apps.deliverer.component.interest_point import InterestPoint
from apps.deliverer.service.color import Color
from apps.deliverer.settings import Settings
from core.texture import Texture


if TYPE_CHECKING:
    from apps.deliverer.view.simulation import SimulationView

Distances = tuple[float, float, float, float]
Position = tuple[float, float]


class Deliverer(Sprite):
    settings = Settings()
    physics_body: pymunk.Body

    default_radius = 5
    radius = default_radius
    default_mass = 10
    default_power = 2000
    power = default_power

    # todo: вынести в параметры
    default_max_cargo = 5
    max_cargo = default_max_cargo
    min_points_amount = 2

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        self.departure: int | None = None
        self.destination: int | None = None
        self.next_point: int | None = None
        self.cargo = 0

        image = PIL.Image.open(f"{self.settings.IMAGES_FOLDER}/circle_0.png")
        texture = Texture(image, hit_box_algorithm = arcade.hitbox.algo_detailed)
        position = [self.view.figure_new.center_x, self.view.figure_new.center_y]
        angle = random.random() * math.pi * 2
        distance = random.random() * self.radius * 10
        position[0] = position[0] + distance * math.cos(angle)
        position[1] = position[1] + distance * math.sin(angle)
        super().__init__(texture, 1, position[0], position[1], angle, **kwargs)

        self.distances_cache: dict[position, Distances] = {}
        self.resize()
        self.update_physics()
        self.update_color()

    def resize(self) -> None:
        scale = self.radius / sum(self.texture.size) * 4
        if scale != self.scale:
            self.scale = scale

    def update_physics(self) -> None:
        if self.physics_engines:
            self.view.physics_engine.remove_sprite(self)
            velocity = self.physics_body.velocity
        else:
            velocity = None

        self.view.physics_engine.add_sprite(self, self.default_mass)
        self.physics_body = self.view.physics_engine.get_physics_object(self).body
        self.physics_body.velocity_func = self.velocity_callback
        if velocity is not None:
            self.physics_body.velocity = velocity

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

    def choose_departure(self) -> None:
        if len(self.view.interest_points) >= self.min_points_amount:
            sizes = [x.size for x in self.view.interest_points]
            min_size = min(sizes)

            departures = list(range(len(self.view.interest_points)))
            # + 1 - чтобы сумма весов не была нулевой, так как это приводит к исключению
            weights = [-(min_size - x) + 1 for x in sizes]

            self.departure = random.choices(departures, weights)[0]
        else:
            self.departure = None

    def choose_destination(self) -> None:
        if len(self.view.interest_points) >= self.min_points_amount:
            sizes = [x.size for x in self.view.interest_points]
            max_size = max(sizes)

            destinations = list(range(len(self.view.interest_points)))
            # + 1 - чтобы сумма весов не была нулевой, так как это приводит к исключению
            weights = [max_size - x + 1 for x in sizes]

            # нет смысла перемещать груз в ту же точку
            if self.departure is not None:
                destinations.remove(self.departure)
                weights = weights[:self.departure] + weights[self.departure + 1:]

                self.destination = random.choices(destinations, weights)[0]
        else:
            self.destination = None

    def update_color(self) -> None:
        if self.cargo == 0:
            self.color = Color.DELIVERER_UNLOADED
        elif self.cargo == self.max_cargo:
            self.color = Color.DELIVERER_LOADED
        else:
            self.color = Color.DELIVERER_SEMI_LOADED

    def load_cargo(self) -> None:
        cargo = min(self.max_cargo - self.cargo, self.view.interest_points[self.departure].size)

        self.view.interest_points[self.departure].size -= cargo
        self.cargo += cargo
        self.physics_body.mass += cargo

        if self.cargo == self.max_cargo:
            self.next_point = self.destination

        self.update_color()

    def unload_cargo(self) -> None:
        cargo = self.cargo

        self.view.interest_points[self.destination].size += cargo
        self.physics_body.mass -= cargo
        self.cargo -= cargo

        self.departure = None
        self.destination = None
        self.next_point = None

        self.view.score += cargo
        self.update_color()

    def return_cargo(self) -> None:
        # возвращение недоставленного груза
        if self.departure is not None and len(self.view.interest_points) > self.departure:
            self.view.interest_points[self.departure].size += self.cargo
        # точка отправления отсутствует, и груз возвращается в случайную точку
        else:
            point = random.randint(0, len(self.view.interest_points) - 1)
            self.view.interest_points[point].size += self.cargo
        self.cargo = 0

    def apply_power(self, delta_time: float) -> None:
        point = self.view.interest_points[self.next_point]

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

            # https://www.desmos.com/calculator/mi9w8ny5we?lang=ru
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

            self.physics_body.velocity = (velocity[0] + adding_velocity_x, velocity[1] + adding_velocity_y)

    def update_angle(self) -> None:
        if self.next_point is not None and len(self.view.interest_points) > self.next_point:
            point = self.view.interest_points[self.next_point]
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

    def dump_velocity(self, delta_time: float) -> None:
        velocity = self.physics_body.velocity
        velocity_len = math.dist(velocity, (0, 0))
        dumping_coeff = 0.1

        dumping_velocity = (2 * self.power * delta_time / self.physics_body.mass)**(1 / 2) * dumping_coeff
        dumping_velocity_x = dumping_velocity / velocity_len * -velocity[0]
        dumping_velocity_y = dumping_velocity / velocity_len * -velocity[1]

        self.physics_body.velocity = (velocity[0] + dumping_velocity_x, velocity[1] + dumping_velocity_y)

    # noinspection PyMethodOverriding
    def on_update(self, delta_time: float) -> None:
        if self.next_point is None:
            self.choose_departure()
            self.choose_destination()
            self.next_point = self.departure

        # точка отправления была удалена
        departure_removed = self.departure is not None and len(self.view.interest_points) <= self.departure
        # точка назначения была удалена
        destination_removed = self.destination is not None and len(self.view.interest_points) <= self.destination
        if departure_removed or destination_removed:
            self.return_cargo()
            self.update_color()

            self.departure = None
            self.destination = None
            self.next_point = None

        if self.next_point is not None:
            point: InterestPoint = self.view.interest_points[self.next_point]
            if self.collides_with_sprite(point.zone):
                if self.next_point == self.departure:
                    self.load_cargo()
                elif self.next_point == self.destination:
                    self.unload_cargo()
                else:
                    raise ValueError(f"Unknown next point: {self.next_point}")
            else:
                self.apply_power(delta_time)
        else:
            self.dump_velocity(delta_time)

        self.distances_cache = {}
