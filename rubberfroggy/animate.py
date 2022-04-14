from enum import Enum, auto
from itertools import repeat
import random
from typing import Dict, List, Tuple

from PIL import Image
import tkinter as tk

from rubberfroggy.util import BASE_PATH


SPRITE_PATH = BASE_PATH / "sprites"


class Canvas:
    def __init__(self, window: tk.Tk, label: tk.Label, width: int, height: int):
        self.window = window
        self.label = label
        self.width = width
        self.height = height


class State(Enum):
    IDLE = auto()
    IDLE_TO_SLEEP = auto()
    SLEEP_TO_IDLE = auto()
    SLEEP = auto()
    WALK_LEFT = auto()
    WALK_RIGHT = auto()
    GRABBED = auto()
    GRAB_TO_FALL = auto()
    FALLING = auto()
    LANDED = auto()


class Animation:
    def __init__(
        self,
        animations: List[State],
        resolution: Tuple[int, int],
        timer: int = 100,
        v_x: float = 0.0,
        v_y: float = 0.0,
        a_x: float = 0.0,
        a_y: float = 0.0,
        rep: int = 0,
        frames: List = None,
        gif: str = None,
        multiplier: int = 1,
    ):
        self.animations = animations
        self.resolution = resolution
        self.timer = timer
        self.v_x = v_x
        self.v_y = v_y
        self.a_x = a_x
        self.a_y = a_y
        self.rep = rep

        frames = [self.scale_to_fit(frame, *resolution) for frame in (self.load_gif(gif) if not frames else frames)]
        self.frames = [frame for group in frames for frame in repeat(group, multiplier)]

    def next(self, animator: "Animator") -> "State":
        if animator.rep < self.rep:
            animator.rep += 1
            return animator.state
        animator.rep = 0
        return random.choice(self.animations)

    def velocity(self) -> Tuple[float, float]:
        return self.v_x, self.v_y

    def acceleration(self) -> Tuple[float, float]:
        return self.a_x, self.a_y

    @staticmethod
    def load_gif(path) -> List[tk.PhotoImage]:
        path = SPRITE_PATH / path
        open(path, 'rb')
        file = Image.open(path)
        frames = [tk.PhotoImage(file=path, format=f"gif -index {i}") for i in range(file.n_frames)]
        file.close()
        return frames

    @staticmethod
    def scale_to_fit(frame: tk.PhotoImage, width: int, height: int) -> tk.PhotoImage:
        scale_width = width / frame.width()
        scale_height = height / frame.height()

        if scale_width < 1:
            frame = frame.subsample(int(1 / scale_width), 1)
        elif scale_width > 1:
            frame = frame.zoom(int(scale_width), 1)

        if scale_height < 1:
            frame = frame.subsample(1, int(1 / scale_height))
        elif scale_height > 1:
            frame = frame.zoom(1, int(scale_height))

        return frame


class Animator:
    def __init__(self, number: int, state: "State", animations: Dict["State", "Animation"], rep: int = 0):
        self.number = number
        self.state = state
        self.animations = animations
        self.rep = rep

    def set_state(self, state: "State") -> bool:
        if state == self.state:
            return False
        self.number = self.rep = 0
        self.state = state
        return True

    @staticmethod
    def get_animations(resolution: Tuple[int, int]):
        # TODO take special care when updating these that each state is represented and that you have the proper transition states
        standing = (
            [State.IDLE_TO_SLEEP]
            + list(repeat(State.IDLE, 3))
            + list(repeat(State.WALK_LEFT, 4))
            + list(repeat(State.WALK_RIGHT, 4))
        )
        animations = {
            State.IDLE: Animation(
                standing,
                gif="idle.gif",
                timer=400,
                resolution=resolution,
            ),
            State.IDLE_TO_SLEEP: Animation(
                [State.SLEEP],
                gif="idle_to_sleep.gif",
                resolution=resolution,
            ),
            State.SLEEP: Animation(
                list(repeat(State.SLEEP, 4)) + [State.SLEEP_TO_IDLE],
                gif="sleep.gif",
                timer=1000,
                resolution=resolution
            ),
            State.SLEEP_TO_IDLE: Animation(
                [State.IDLE],
                gif="sleep_to_idle.gif",
                resolution=resolution,
            ),
            State.WALK_LEFT: Animation(
                standing,
                gif="walking_left.gif",
                v_x=-3,
                resolution=resolution
            ),
            State.WALK_RIGHT: Animation(
                standing,
                gif="walking_right.gif",
                v_x=3,
                resolution=resolution
            ),
            # TODO No gifs exist for the default cat rn, update when custom gifs are made
            State.GRABBED: Animation(
                [State.GRABBED],
                gif="walking_right.gif",
                timer=50,
                resolution=resolution
            ),
            State.FALLING: Animation(
                [State.FALLING],
                gif="walking_left.gif",
                timer=10,
                multiplier=2,
                a_y=2,
                resolution=resolution,
            ),
        }

        # TODO No landing gif exists for the default cat rn, update when custom gifs are made
        animations[State.LANDED] = animations[State.IDLE]
        return animations
