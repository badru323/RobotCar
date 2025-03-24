"""
PID controller for smooth steering
"""

class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd 
        self.prev_error = 0
        self.integral = 0

    def update(self, error, dt):
        # Proportional term
        P_out = self.Kp*error

        # Integral term
        self.integral += error*dt
        I_out = self.Ki * self.integral

        # Derivative term 
        derivative = (error - self.prev_error)/dt 
        D_out = self.Kd * derivative 

        # PID output 
        output = P_out + I_out + D_out

        # Remember current error for next derivative calculation
        self.prev_error = error

        return output 
    
    