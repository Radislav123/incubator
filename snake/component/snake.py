from snake.component.brain import Brain
from snake.component.map import Map
from snake.service.color import Color


class Segment:
    color = Color.SNAKE_ALIVE

    def __init__(self, world_map: Map, x: int, y: int) -> None:
        self.map = world_map
        self.x = x
        self.y = y

    def move_to(self, x: int, y: int) -> tuple[int, int]:
        self.map.snake[self.x][self.y] = None
        previous_x = self.x
        previous_y = self.y
        self.x = x
        self.y = y
        self.map.snake[self.x][self.y] = self
        return previous_x, previous_y


class Snake:
    colors = {
        True: Color.SNAKE_ALIVE,
        False: Color.SNAKE_DEAD
    }

    def __init__(self, brain: Brain, world_map: Map) -> None:
        self.brain = brain
        self.world_map = world_map
        self.segments: list[Segment] = []
        self.add_segment(self.world_map.side_length - 1, self.world_map.side_length - 1)
        self.head = self.segments[0]

        self.age = 0
        self.starvation = 0
        self.max_starvation = 100
        self.alive = True
        self.direction = 0

    def add_segment(self, x: int, y: int) -> None:
        segment = Segment(self.world_map, x, y)
        self.segments.append(segment)
        self.world_map.snake[x][y] = segment

    def move(self, offset_x: int, offset_y: int) -> None:
        x = self.segments[0].x + offset_x
        y = self.segments[0].y + offset_y
        for segment in self.segments:
            x, y = segment.move_to(x, y)

    def choose_direction(self) -> None:
        self.brain.process([0])

        directions_amount = len(self.world_map.offsets)
        direction_change = self.brain.output + directions_amount
        self.direction = (self.direction + direction_change) % direction_change

    def eat(self) -> None:
        if self.world_map.food[self.head.x][self.head.y]:
            self.starvation = 0
        else:
            self.starvation += 1

    def perform(self) -> None:
        self.choose_direction()
        move_x, move_y = self.world_map.offsets[self.direction]

        border_collision = self.world_map.borders[self.head.x + move_x][self.head.y + move_y]
        segment_collision = self.world_map.snake[self.head.x + move_x][self.head.y + move_y]
        starvation_death = self.starvation > self.max_starvation

        self.alive = not (border_collision or segment_collision or starvation_death)
        if self.alive:
            self.move(move_x, move_y)
            self.eat()
        else:
            Segment.color = Color.SNAKE_DEAD

        self.age += 1
