#------------------------------------------------------------------------------
# INITIAL SETUP
from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
import time, math

#connecting to vehicle
import argparse
parser = argparse.ArgumentParser(description='commands')
parser.add_argument('--connect')
args = parser.parse_args()

connection_string = args.connect

print('Connection to the Vehicle on %s'%connection_string)
vehicle = connect(connection_string,wait_ready = True,heartbeat_timeout=180)

Xsign = -1
Ysign = -1
#------------------------------------------------------------------------------
# FUNCTIONS
def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print "Basic pre-arm checks"
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print " Waiting for vehicle to initialise..."
        time.sleep(1)

    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode    = VehicleMode("GUIDED")
    vehicle.armed   = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print " Altitude: ", vehicle.location.global_relative_frame.alt
        #Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            print "Reached target altitude"
            break
        time.sleep(1)
#-----------------------------------
def condition_yaw(heading, relative=False):
    if relative:
        is_relative=1 #yaw relative to direction of travel
    else:
        is_relative=0 #yaw is an absolute angle
    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
        0, #confirmation
        heading,    # param 1, yaw in degrees
        90,          # param 2, yaw speed deg/s
        -1,          # param 3, direction -1 ccw, 1 cw
        is_relative, # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used
    # send command to vehicle
    vehicle.send_mavlink(msg)
#-----------------------------------
def get_location_offset_meters(original_location, dNorth, dEast, alt):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
    specified `original_location`. The returned Location adds the entered `alt` value to the altitude of the `original_location`.
    The function is useful when you want to move the vehicle around specifying locations relative to
    the current vehicle position.
    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius=6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    return LocationGlobal(newlat, newlon,original_location.alt+alt)
#-----------------------------------
def circle(C_alt,radius,interval):
    center = vehicle.location.global_relative_frame
    print(center)
    condition_yaw(0, relative = False)
    print("Yaw 0 absolute (North)")
    print("going to WP1")
    time.sleep(2)

    for i in range(1,interval + 1):
        print(i)
        angle = i*(90-(180 - (720 / interval)) / 2)
        """
        if angle <= 360 and angle > 270:
            Xsign = 1
            Ysign = -1

        elif angle <= 270 and angle > 180:
            Xsign = 1
            Ysign = 1

        elif angle <= 180 and angle > 90:
            Xsign = -1
            Ysign = 1

        else:
            Xsign = -1
            Ysign = -1
        """
        Y = radius*math.cos(90 - angle)
        X = radius*math.sin(90 - angle)
        print "x: ", X, "y: ", Y, "X sign: ", Xsign, "Y sign: ", Ysign

        WP = get_location_offset_meters(center,Y,X,0)
        vehicle.simple_goto(WP)
        time.sleep(10)
        print "Yaw: ", angle

    condition_yaw(angle, relative = False)
    print(angle)
    time.sleep(5)
#------------------------------------------------------------------------------
# MISSIONS
arm_and_takeoff(5)
#SPEED
vehicle.airspeed = 17.5

#CIRCLE
condition_yaw(0, relative = False)
circle(5,15,6)

#RETURN
print('RTL')
vehicle.mode = VehicleMode('RTL')

#CLOSE CONNECTION
vehicle.close()
