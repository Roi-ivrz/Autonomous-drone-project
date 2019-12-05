from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

#connecting to vehicle
import argparse
parser = argparse.ArgumentParser(description='commands')
parser.add_argument('--connect')
args = parser.parse_args()

connection_string = args.connect

print('Connection to the Vehicle on %s'%connection_string)
vehicle = connect(connection_string,wait_ready = True,heartbeat_timeout=180)

#functions
def arm_and_takeoff(tgt_altitude):
	print('Arming')

	while not vehicle.is_armable:
		print('Arm failed')
		time.sleep(1)

	vehicle.mode = VehicleMode('GUIDED')
	vehicle.armed = True

	vehicle.simple_takeoff(tgt_altitude)
	print('TAKEOFF')

	#wait for reaching the target altitude
	while True:
		altitude = vehicle.location.global_relative_frame.alt

		if altitude >= tgt_altitude -1:
			print('Target Altitude Reached')
			break
	time.sleep(1)


#MAIN MISSION
arm_and_takeoff(15)

#SPEED
vehicle.airspeed = 10

#WAYPOINT #1
print('going to waypoint #1')
wp1 = LocationGlobalRelative(38.733478, -121.211845, 15)
vehicle.simple_goto(wp1)

#TRAVEL
time.sleep(30)

#RETURN
print('RTL')
vehicle.mode = VehicleMode('RTL')

#TRAVEL
time.sleep(25)

#CLOSE CONNECTION
vehicle.close()
