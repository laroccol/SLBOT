from dataclasses import field
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState

class State():
    
    def __init__(self, field_info):

        self.field_info = field_info
        self.controller = SimpleControllerState()

    def tick(self, car_index, packet):

        return self.controller

    def exit_conditions(self, car_index, packet):
        
        return None