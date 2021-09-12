from dataclasses import field
from strategy.state import State
import strategy.states.chase_ball as chase_ball
from util.drive import steer_toward_target
from util.vec import Vec3

class Retreat(State):

    def __init__(self, field_info):

        super().__init__(field_info)

    def tick(self, car_index, packet):
        
        my_car = packet.game_cars[car_index]

        self.controller.steer = steer_toward_target(my_car, Vec3(self.field_info.goals[my_car.team].location))
        self.controller.throttle = 1
        self.controller.boost = 1

        return self.controller

    def exit_conditions(self, car_index, packet):
        
        if packet.game_ball.physics.location.y >= 0:

            return chase_ball.ChaseBall(self.field_info)

        return None