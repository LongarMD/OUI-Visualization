from common.module import Module
from modules.ao_star.ao_star import AOStarSolver
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from common.app import App


class AO_Star(Module):
    __label__ = "AO*"

    solver: AOStarSolver

    def __init__(self, app: "App") -> None:
        super().__init__(app)
        # self.solver = AOStarSolver()  # TODO
