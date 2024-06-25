import copy
import math
from typing import Self

import PIL.Image
import arcade.hitbox
import pymunk
from arcade import PymunkPhysicsEngine, Sprite, SpriteList

from core.service.color import Color
from core.texture import Texture
from core.view.simulation import SimulationView as CoreSimulationView
from gravity.settings import Settings


class BodySystem:
    def __init__(self, bodies: SpriteList["Body"]) -> None:
        self.bodies = bodies
        self.x: float | None = None
        self.y: float | None = None
        self.mass: float | None = None
        self.impulse: tuple[float, float] | None = None

    def calculate(self) -> None:
        if len(self.bodies) != 0:
            self.mass = sum(x.physics_body.mass for x in self.bodies)
            self.x = sum(x.center_x * x.physics_body.mass for x in self.bodies) / self.mass
            self.y = sum(x.center_y * x.physics_body.mass for x in self.bodies) / self.mass
            impulse_x = sum(x.physics_body.velocity[0] * x.physics_body.mass for x in self.bodies)
            impulse_y = sum(x.physics_body.velocity[1] * x.physics_body.mass for x in self.bodies)
            self.impulse = (impulse_x, impulse_y)
        else:
            self.mass = None
            self.x = None
            self.y = None
            self.impulse = None


class PhysicsEngine(PymunkPhysicsEngine):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class Body(Sprite):
    physics_body: pymunk.Body

    def __init__(self, view: "SimulationView", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.view = view
        self.bordered: dict["Body", float] = {}

    def __repr__(self) -> str:
        return f"Body_{hash(self)}"

    # оригинал описан в PymunkPhysicsEngine.add_sprite
    def velocity_callback(
            self,
            body: pymunk.Body,
            gravity: tuple[float, float],
            damping: float,
            delta_time: float
    ) -> None:
        # Custom damping
        if self.pymunk.damping is not None:
            adj_damping = ((self.pymunk.damping * 100.0) / 100.0)**delta_time
            damping = adj_damping

        # Custom gravity
        coeff = 10
        for other in self.view.bodies:
            distance_x = other.center_x - self.center_x
            distance_y = other.center_y - self.center_y
            distance_square = distance_x**2 + distance_y**2
            distance = distance_square**(1 / 2)

            if not (distance < self.width / 2 or distance < self.height / 2 or
                    distance < other.width / 2 or distance < other.height / 2):
                adding_gravity = other.physics_body.mass / distance_square
                adding_gravity_x = coeff * adding_gravity * distance_x / distance
                adding_gravity_y = coeff * adding_gravity * distance_y / distance

                gravity_x = gravity[0] + math.copysign(adding_gravity_x, other.center_x - self.center_x)
                gravity_y = gravity[1] + math.copysign(adding_gravity_y, other.center_y - self.center_y)
                gravity = (gravity_x, gravity_y)

        # Go ahead and update velocity
        pymunk.Body.update_velocity(body, gravity, damping, delta_time)

    def prepare_physics(self, mass: float = 1000, impulse: tuple[float, float] = None) -> None:
        self.view.physics_engine.add_sprite(self, mass)
        self.physics_body = self.view.physics_engine.get_physics_object(self).body
        if impulse is not None:
            self.physics_body.apply_impulse_at_local_point(impulse)
        self.physics_body.velocity_func = self.velocity_callback

    # noinspection PyMethodOverriding
    def on_update(self, delta_time: float) -> None:
        max_distance = 0
        if (self.center_x < -max_distance or self.center_x > self.view.window.width + max_distance or
                self.center_y < -max_distance or self.center_y > self.view.window.height + max_distance):
            self.remove_from_simulation()

    def merge(self, sprite_list: list["Body"]) -> tuple[SpriteList[Self], Self, float, tuple[float, float]]:
        new_sprite_list = SpriteList()
        new_sprite_list.append(self)
        for body in sprite_list:
            new_sprite_list.append(body)

        body_system = BodySystem(new_sprite_list)
        body_system.calculate()
        radius = sum((x.width / 2)**2 for x in new_sprite_list)**(1 / 2)

        new_body = self.view.create_body(body_system.x, body_system.y, radius)
        return new_sprite_list, new_body, body_system.mass, body_system.impulse

    def remove_from_simulation(self) -> None:
        self.remove_from_sprite_lists()
        for other in self.bordered:
            try:
                del other.bordered[self]
            except KeyError:
                pass


class SimulationView(CoreSimulationView):
    settings = Settings()

    bodies: SpriteList[Body]
    physics_engine: PhysicsEngine
    body_system: BodySystem
    creating_body: Body | None

    def __init__(self) -> None:
        super().__init__()

    def on_show_view(self) -> None:
        super().on_show_view()

        self.bodies = SpriteList()
        self.physics_engine = PhysicsEngine()
        self.body_system = BodySystem(self.bodies)
        self.creating_body = None

    def on_draw(self) -> None:
        super().on_draw()
        self.bodies.draw()

        draw_hit_boxes = False
        if draw_hit_boxes:
            self.bodies.draw_hit_boxes(Color.RED)

        draw_mass_center = False
        if draw_mass_center and self.body_system.x is not None:
            arcade.draw_point(self.body_system.x, self.body_system.y, Color.RED, 30)

    def on_update(self, delta_time: float) -> None:
        self.body_system.calculate()

        self.physics_engine.step(delta_time)
        self.bodies.on_update(delta_time)

        merge = True
        if merge:
            new_bodies = {}
            for body in self.bodies:
                collided = set(arcade.check_for_collision_with_list(body, self.bodies))
                body_list = copy.copy(collided)
                body_list.update(body.bordered)
                merge_list = []
                for other in body_list:
                    if other in collided:
                        if other not in body.bordered:
                            body.bordered[other] = delta_time
                        else:
                            body.bordered[other] += delta_time
                            if body.bordered[other] > 1:
                                merge_list.append(other)
                    else:
                        del body.bordered[other]

                if len(merge_list) > 0:
                    merged_list, new_body, new_body_mass, new_body_impulse = body.merge(merge_list)
                    merged_list = list(merged_list)
                    new_bodies[new_body] = (new_body_mass, new_body_impulse)
                    for merged in merged_list:
                        merged.remove_from_simulation()

            for new_body, (new_body_mass, new_body_impulse) in new_bodies.items():
                self.bodies.append(new_body)
                new_body.prepare_physics(new_body_mass, new_body_impulse)

    def create_body(self, x: float, y: float, radius: float = 10) -> Body:
        image = PIL.Image.open(f"{self.settings.IMAGES_FOLDER}/circle_0.png")
        texture = Texture(image, hit_box_algorithm = arcade.hitbox.algo_detailed)
        scale = radius / sum(texture.size) * 4
        angle = 0
        body = Body(self, texture, scale, x, y, angle)
        return body

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        super().on_mouse_press(x, y, button, modifiers)
        if button == 1:
            self.creating_body = self.create_body(x, y)
        elif button == 4:
            bodies = arcade.get_sprites_at_point((x, y), self.bodies)
            for body in bodies:
                body.remove_from_simulation()

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        super().on_mouse_release(x, y, button, modifiers)
        if button == 1:
            if self.creating_body is not None:
                self.bodies.append(self.creating_body)

                coeff = 1000
                threshold = 2

                impulse_x = x - self.creating_body.center_x
                impulse_y = y - self.creating_body.center_y

                if abs(impulse_x) >= threshold:
                    impulse_x *= coeff
                else:
                    impulse_x = 0
                if abs(impulse_y) >= threshold:
                    impulse_y *= coeff
                else:
                    impulse_y = 0

                self.creating_body.prepare_physics(impulse = (impulse_x, impulse_y))
