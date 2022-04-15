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
    IDLE_TO_GRABBED = auto()
    GRABBED = auto()
    GRAB_TO_FALL = auto()
    FALLING = auto()
    LANDING = auto()
    IDLE_TO_QUESTION = auto()
    QUESTION_TO_IDLE = auto()
    QUESTION = auto()
    HEART = auto()


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
        reverse: bool = False,
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

        if reverse:
            frames.reverse()

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
        open(path, "rb")
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
        animations = {
            State.IDLE_TO_QUESTION: Animation(
                [State.QUESTION],
                gif="idle_to_question.gif",
                timer=200,
                resolution=resolution,
            ),
            State.QUESTION: Animation(
                [State.QUESTION],
                gif="question.gif",
                timer=200,
                resolution=resolution,
            ),
            State.QUESTION_TO_IDLE: Animation(
                [State.IDLE],
                gif="idle_to_question.gif",
                timer=200,
                reverse=True,
                resolution=resolution,
            ),
            State.IDLE: Animation(
                list(repeat(State.IDLE, 8)) + list(repeat(State.IDLE_TO_SLEEP, 2)) + [State.HEART],
                gif="idle.gif",
                timer=500,
                resolution=resolution,
            ),
            State.IDLE_TO_SLEEP: Animation(
                [State.SLEEP],
                gif="idle_to_sleep.gif",
                timer=200,
                resolution=resolution,
            ),
            State.SLEEP: Animation(
                list(repeat(State.SLEEP, 4)) + [State.SLEEP_TO_IDLE],
                gif="sleep.gif",
                timer=800,
                resolution=resolution,
            ),
            State.SLEEP_TO_IDLE: Animation(
                [State.IDLE],
                gif="idle_to_sleep.gif",
                timer=200,
                reverse=True,
                resolution=resolution,
            ),
            State.IDLE_TO_GRABBED: Animation(
                [State.IDLE_TO_GRABBED],
                gif="idle_to_grabbed.gif",
                resolution=resolution,
            ),
            State.GRABBED: Animation(
                [State.GRABBED],
                gif="grabbed.gif",
                timer=400,
                resolution=resolution,
            ),
            State.GRAB_TO_FALL: Animation(
                [State.FALLING],
                gif="grabbed_to_falling.gif",
                timer=50,
                multiplier=2,
                v_y=4,
                a_y=1,
                resolution=resolution,
            ),
            State.FALLING: Animation(
                [State.FALLING],
                gif="falling.gif",
                timer=15,
                multiplier=2,
                v_y=8,
                a_y=1,
                resolution=resolution,
            ),
            State.LANDING: Animation(
                [State.IDLE],
                gif="landing.gif",
                timer=150,
                resolution=resolution,
            ),
            State.HEART: Animation(
                [State.IDLE],
                gif="heart.gif",
                timer=150,
                resolution=resolution,
            ),
        }
        return animations
