from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.messages.flat.QuickChatSelection import QuickChatSelection
from rlbot.utils.structures.game_data_struct import GameTickPacket
from strategy.states.chase_ball import ChaseBall

from util.ball_prediction_analysis import find_slice_at_time
from util.boost_pad_tracker import BoostPadTracker
from util.drive import steer_toward_target
from util.sequence import Sequence, ControlStep
from util.vec import Vec3


class MyBot(BaseAgent):


    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.active_sequence: Sequence = None
        self.boost_pad_tracker = BoostPadTracker()


    def initialize_agent(self):
        # Set up information about the boost pads now that the game is active and the info is available
        self.boost_pad_tracker.initialize_boosts(self.get_field_info())
        self.state = ChaseBall(self.get_field_info())


    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        """
        This function will be called by the framework many times per second. This is where you can
        see the motion of the ball, etc. and return controls to drive your car.
        """

        # Keep our boost pad info updated with which pads are currently active
        self.boost_pad_tracker.update_boost_status(packet)

        self.renderer.draw_string_3d(packet.game_cars[self.index].physics.location, 1, 1, self.state.name, self.renderer.white())

        ball_prediction = self.get_ball_prediction_struct()
        
        if ball_prediction is not None:
            previous_location = ball_prediction.slices[0].physics.location
            for i in range(1, 160):
                prediction_slice = ball_prediction.slices[i]
                location = prediction_slice.physics.location
                self.renderer.draw_line_3d(previous_location, location, self.renderer.white())
                previous_location = location

        next_state = self.state.exit_conditions(self.index, packet)
        if next_state != None:
            self.state = next_state

        return self.state.tick(self.index, packet)

        # # This is good to keep at the beginning of get_output. It will allow you to continue
        # # any sequences that you may have started during a previous call to get_output.
        # if self.active_sequence is not None and not self.active_sequence.done:
        #     controls = self.active_sequence.tick(packet)
        #     if controls is not None:
        #         return controls

        # if packet.game_info.is_kickoff_pause:
        #     self.kickoff(packet)

        # # Gather some information about our car and the ball
        # my_car = packet.game_cars[self.index]
        # enemy_car = packet.game_cars[1 - self.index]
        # car_location = Vec3(my_car.physics.location)
        # car_velocity = Vec3(my_car.physics.velocity)
        # ball_location = Vec3(packet.game_ball.physics.location)

        # # By default we will chase the ball, but target_location can be changed later
        # target_location = ball_location

        # if car_location.dist(ball_location) > 1500:
        #     # We're far away from the ball, let's try to lead it a little bit
        #     ball_prediction = self.get_ball_prediction_struct()  # This can predict bounces, etc
        #     ball_in_future = find_slice_at_time(ball_prediction, packet.game_info.seconds_elapsed + 2)

        #     # ball_in_future might be None if we don't have an adequate ball prediction right now, like during
        #     # replays, so check it to avoid errors.
        #     if ball_in_future is not None:
        #         target_location = Vec3(ball_in_future.physics.location)
        #         self.renderer.draw_line_3d(ball_location, target_location, self.renderer.cyan())

        # # Draw some things to help understand what the bot is thinking
        # self.renderer.draw_line_3d(car_location, target_location, self.renderer.white())
        # self.renderer.draw_string_3d(car_location, 1, 1, f'Speed: {car_velocity.length():.1f}', self.renderer.white())
        # self.renderer.draw_rect_3d(target_location, 8, 8, True, self.renderer.cyan(), centered=True)

        # if 750 < car_velocity.length() < 800:
        #     # We'll do a front flip if the car is moving at a certain speed.
        #     return self.begin_front_flip(packet)

        # controls = SimpleControllerState()
        # # controls.steer = steer_toward_target(my_car, Vec3(enemy_car.physics.location))
        # controls.throttle = 1.0
        # controls.boost = 1.0
        # # You can set more controls if you want, like controls.boost.

        # return controls


    def begin_front_flip(self, packet):
        # Send some quickchat just for fun
        self.send_quick_chat(team_only=False, quick_chat=QuickChatSelection.Information_IGotIt)

        # Do a front flip. We will be committed to this for a few seconds and the bot will ignore other
        # logic during that time because we are setting the active_sequence.
        self.active_sequence = Sequence([
            ControlStep(duration=0.05, controls=SimpleControllerState(jump=True)),
            ControlStep(duration=0.05, controls=SimpleControllerState(jump=False)),
            ControlStep(duration=0.2, controls=SimpleControllerState(jump=True, pitch=-1)),
            ControlStep(duration=0.8, controls=SimpleControllerState()),
            
        ])

        # Return the controls associated with the beginning of the sequence so we can start right away.
        return self.active_sequence.tick(packet)


    def kickoff(self, packet):

        my_car = packet.game_cars[self.index]
        car_start = my_car.physics.location

        direction = -1 if car_start.x > 0 else 1
        if my_car.team == 1: direction *= -1


        if car_start.x < -2000 or car_start.x > 2000:
            self.diagonal_kickoff(packet, direction)
        elif car_start.x != 0:
            self.offset_kickoff(packet, direction)
        else:
            self.middle_kickoff(packet)


    def diagonal_kickoff(self, packet, direction):
        pass


    def offset_kickoff(self, packet, direction):
        pass


    def middle_kickoff(self, packet):
        pass
