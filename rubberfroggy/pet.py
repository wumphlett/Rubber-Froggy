from rubberfroggy.animate import Animator, Canvas, State


class Pet:
    def __init__(self, x: int, y: int, canvas: "Canvas", animator: "Animator"):
        self.x = x
        self.y = y
        self.v_x = 0.
        self.v_y = 0.
        self.a_x = 0.
        self.a_y = 0.
        self.canvas = canvas
        self.animator = animator

    @property
    def current_animation(self):
        return self.animator.animations[self.animator.state]

    def reset(self):
        self.v_x, self.v_y = self.current_animation.velocity()
        self.a_x, self.a_y = self.current_animation.acceleration()

    def update(self):
        self.move()
        self.progress()

    def move(self):
        self.v_x += self.a_x
        self.v_y += self.a_y
        self.x = int(self.x + self.v_x)
        self.y = int(self.y + self.v_y)

        resolution = self.current_animation.resolution

        if self.x < 0:
            self.x = resolution[0]
        if self.x > self.canvas.width - resolution[0]:
            self.x = self.canvas.width - resolution[0]

        if self.y > self.canvas.height - resolution[1]:
            self.y = self.canvas.height - resolution[1]
            if self.animator.state == State.FALLING:
                self.set_animation(State.LANDED)

    def progress(self):
        animation = self.current_animation
        if self.animator.number < len(animation.frames) - 1:
            self.animator.number += 1
        else:
            self.animator.number = 0
            self.set_animation(animation.next(self.animator))

    def tick(self):
        self.update()
        self.update_geometry()
        self.canvas.label.configure(image=self.draw())
        self.canvas.window.after(1, self.handle_event)

    def draw(self):
        return self.current_animation.frames[self.animator.number]

    def set_animation(self, state: "State"):
        if changed := self.animator.set_state(state):
            self.reset()
        return changed

    def update_geometry(self):
        resolution = self.current_animation.resolution
        self.canvas.window.geometry(f"{resolution[0]}x{resolution[1]}+{self.x}+{self.y}")

    def handle_event(self):
        self.canvas.window.after(self.current_animation.timer, self.tick)

    # Events
    def start_hold(self, _):
        self.set_animation(State.GRABBED)

    def while_hold(self, event):
        resolution = self.current_animation.resolution
        self.x = event.x_root - int(resolution[0] / 2)
        self.y = event.y_root - int(resolution[1] / 2)
        self.update_geometry()

    def stop_hold(self, _):
        self.set_animation(State.FALLING)
