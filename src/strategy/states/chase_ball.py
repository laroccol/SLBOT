from strategy.state import State
import strategy.states.retreat as retreat
from util.drive import steer_toward_target
from util.vec import Vec3

class ChaseBall(State):

    def __init__(self, field_info):

        super().__init__(field_info)

    def tick(self, car_index, packet):

        self.controller.steer = steer_toward_target(packet.game_cars[car_index], Vec3(packet.game_ball.physics.location))
        self.controller.throttle = 1
        self.controller.boost = 1

        return self.controller

    def exit_conditions(self, car_index, packet):
        
        if packet.game_ball.physics.location.y < 0:
            
            return retreat.Retreat(self.field_info)

        return None
