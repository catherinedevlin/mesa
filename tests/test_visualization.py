from collections import defaultdict
from unittest import TestCase

import mesa
from mesa.model import Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.visualization_old.ModularVisualization import ModularServer
from mesa.visualization_old.modules import CanvasGrid, TextElement
from mesa.visualization_old.UserParam import (
    NumberInput,
    Slider,
)


class MockAgent(mesa.Agent):
    """
    Minimalistic agent implementation for testing purposes
    """

    def __init__(self, unique_id, model, val):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.val = val
        self.local = 0

    def step(self):
        self.val += 1
        self.local += 0.25


class MockModel(Model):
    """Test model for testing"""

    def __init__(self, width, height, key1=103, key2=104):
        super().__init__()
        self.width = width
        self.height = height
        self.key1 = (key1,)
        self.key2 = key2
        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(width, height, torus=True)

        for _c, pos in self.grid.coord_iter():
            x, y = pos
            a = MockAgent(x + y * 100, self, x * y * 3)
            self.grid.place_agent(a, (x, y))
            self.schedule.add(a)

    def step(self):
        self.schedule.step()


class TestModularServer(TestCase):
    """Test server for testing"""

    def portrayal(self, cell):
        return {
            "Shape": "rect",
            "w": 1,
            "h": 1,
            "Filled": "true",
            "Layer": 0,
            "x": 0,
            "y": 0,
            "Color": "black",
        }

    def setUp(self):
        self.user_params = {
            "width": 1,
            "height": 1,
            "key1": NumberInput("Test Parameter", 101),
            "key2": Slider("Test Parameter", 200, 0, 300, 10),
        }

        self.viz_elements = [
            CanvasGrid(self.portrayal, 10, 10, 20, 20),
            TextElement(),
            # ChartModule([{"Label": "Wolves", "Color": "#AA0000"},  # Todo - test chart module
            #              {"Label": "Sheep", "Color": "#666666"}])
        ]

        self.server = ModularServer(
            MockModel, self.viz_elements, "Test Model", model_params=self.user_params
        )

    def test_canvas_render_model_state(self):
        test_portrayal = self.portrayal(None)
        test_grid_state = defaultdict(list)
        test_grid_state[test_portrayal["Layer"]].append(test_portrayal)

        state = self.server.render_model()
        assert state[0] == test_grid_state

    def test_text_render_model_state(self):
        state = self.server.render_model()
        assert state[1] == "<b>VisualizationElement goes here</b>."

    def test_user_params(self):
        print(self.server.user_params)
        assert self.server.user_params == {
            "key1": NumberInput("Test Parameter", 101).json,
            "key2": Slider("Test Parameter", 200, 0, 300, 10).json,
        }
