import math

import PIL.Image
import arcade.hitbox
import pymunk
from arcade import PymunkPhysicsEngine, Sprite, SpriteList

from core.texture import Texture
from core.view.simulation import SimulationView as CoreSimulationView
from gravity_simulator.settings import Settings


class MassCenter:
    def __init__(self, view: "SimulationView", x: float = 0, y: float = 0, mass: float = 0) -> None:
        self.view = view
        self.x = x
        self.y = y
        self.mass = mass

    def calculate(self) -> None:
        if len(self.view.bodies) != 0:
            self.mass = sum(x.physics_body.mass for x in self.view.bodies)
            self.x = sum(x.center_x * x.physics_body.mass for x in self.view.bodies) / self.mass
            self.y = sum(x.center_y * x.physics_body.mass for x in self.view.bodies) / self.mass
        else:
            self.mass = None
            self.x = None
            self.y = None


class PhysicsEngine(PymunkPhysicsEngine):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class Body(Sprite):
    physics_body: pymunk.Body

    def __init__(self, view: "SimulationView", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.view = view

    # оригинал описан в PymunkPhysicsEngine.add_sprite
    def velocity_callback(self, body: pymunk.Body, gravity: tuple[float, float], damping: float, delta_time: float):
        # Custom damping
        if self.pymunk.damping is not None:
            adj_damping = ((self.pymunk.damping * 100.0) / 100.0)**delta_time
            damping = adj_damping

        # Custom gravity
        calculation_type = 1
        if calculation_type == 0:
            if len(self.view.bodies) > 1:
                mass_center = self.view.mass_center
                full_mass = mass_center.mass
                system_mass = mass_center.mass - body.mass

                # self.physics_body == body
                system_x = (mass_center.x * full_mass - self.center_x * body.mass) / system_mass
                system_y = (mass_center.y * full_mass - self.center_y * body.mass) / system_mass

                distance_x = system_x - self.center_x
                distance_y = system_y - self.center_y
                distance_square = distance_x**2 + distance_y**2
                distance = distance_square**(1 / 2)

                if distance_square != 0:
                    adding_gravity = system_mass / distance_square
                    adding_gravity_x = adding_gravity * distance_x / distance
                    adding_gravity_y = adding_gravity * distance_y / distance

                    gravity_x = gravity[0] + math.copysign(adding_gravity_x, system_x - self.center_x)
                    gravity_y = gravity[1] + math.copysign(adding_gravity_y, system_y - self.center_y)
                    gravity = (gravity_x, gravity_y)
        elif calculation_type == 1:
            for other in self.view.bodies:
                if self in self.view.adding_gravities:
                    adding_gravity = self.view.adding_gravities.pop(self)
                    adding_gravity_x = -adding_gravity[0]
                    adding_gravity_y = -adding_gravity[1]

                    gravity_x = gravity[0] + math.copysign(adding_gravity_x, other.center_x - self.center_x)
                    gravity_y = gravity[1] + math.copysign(adding_gravity_y, other.center_y - self.center_y)
                    gravity = (gravity_x, gravity_y)
                else:
                    distance_x = other.center_x - self.center_x
                    distance_y = other.center_y - self.center_y
                    distance_square = distance_x**2 + distance_y**2
                    distance = distance_square**(1 / 2)

                    if (distance < self.width / 2 or distance < self.height / 2 or
                            distance < other.width / 2 or distance < other.height / 2):
                        self.view.adding_gravities[other] = (0, 0)
                    else:
                        adding_gravity = other.physics_body.mass / distance_square
                        adding_gravity_x = adding_gravity * distance_x / distance
                        adding_gravity_y = adding_gravity * distance_y / distance

                        gravity_x = gravity[0] + math.copysign(adding_gravity_x, other.center_x - self.center_x)
                        gravity_y = gravity[1] + math.copysign(adding_gravity_y, other.center_y - self.center_y)
                        gravity = (gravity_x, gravity_y)

                        self.view.adding_gravities[other] = (adding_gravity_x, adding_gravity_y)

        # Go ahead and update velocity
        pymunk.Body.update_velocity(body, gravity, damping, delta_time)

    def prepare_physics(self) -> None:
        # килограммы
        mass = 10000

        self.view.physics_engine.add_sprite(self, mass)
        self.physics_body = self.view.physics_engine.get_physics_object(self).body
        self.physics_body.velocity_func = self.velocity_callback

    # noinspection PyMethodOverriding
    def on_update(self, delta_time: float) -> None:
        max_distance = 5000
        if (self.center_x < -max_distance or self.center_x > self.view.window.width + max_distance or
                self.center_y < -max_distance or self.center_y > self.view.window.height + max_distance):
            self.remove_from_sprite_lists()


class SimulationView(CoreSimulationView):
    settings = Settings()

    bodies: SpriteList[Body]
    physics_engine: PhysicsEngine
    mass_center: MassCenter

    def __init__(self) -> None:
        super().__init__()

        self.adding_gravities: dict[Body, tuple[float, float]] = {}

    def on_show_view(self) -> None:
        super().on_show_view()

        self.bodies = SpriteList()
        self.physics_engine = PhysicsEngine()
        self.mass_center = MassCenter(self)

    def on_draw(self) -> None:
        super().on_draw()
        self.bodies.draw()
        # self.bodies.draw_hit_boxes(Color.RED)

    def on_update(self, delta_time: float) -> None:
        self.mass_center.calculate()

        self.physics_engine.step(delta_time)
        self.bodies.on_update(delta_time)

    def add_body(self, x: float, y: float) -> None:
        radius = 10
        image = PIL.Image.open(f"{self.settings.IMAGES_FOLDER}/circle_0.png")
        texture = Texture(image, hit_box_algorithm = arcade.hitbox.algo_detailed)
        scale = radius / sum(texture.size) * 4
        angle = 0
        body = Body(self, texture, scale, x, y, angle)

        self.bodies.append(body)
        body.prepare_physics()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        super().on_mouse_press(x, y, button, modifiers)
        self.add_body(x, y)
