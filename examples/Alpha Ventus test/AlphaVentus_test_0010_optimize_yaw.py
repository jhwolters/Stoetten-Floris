# Copyright 2019 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

# See read the https://floris.readthedocs.io for documentation


import matplotlib.pyplot as plt
import floris.tools as wfct
import floris.tools.visualization as vis
import floris.tools.cut_plane as cp
from floris.tools.optimization import optimize_yaw
import numpy as np
import json
import os


print('Running FLORIS with no yaw...')
fi = wfct.floris_utilities.FlorisInterface("AlphaVentus_test_input.json")

# set turbine locations to 3 turbines in a row
D = fi.floris.farm.turbines[0].rotor_diameter
layout_x = [
        0.0,
        800.0,
        1600.0,
        0.0,
        800.0,
        1600.0,
        0.0,
        800.0,
        1600.0,
        0.0,
        800.0,
        1600.0
      ]
layout_y = [
        0.0,
        0.0,
        0.0,
        800.0,
		800.0,
		800.0,
		1600.0,
		1600.0,
		1600.0,
		2400.0,
		2400.0,
		2400.0
      ]
fi.reinitialize_flow_field(layout_array=(layout_x, layout_y))
fi.calculate_wake()

#Importing the data from the .json file as python variables
with open('AlphaVentus_test_input.json', 'r') as file:
	data = json.load(file)

	farm = data["farm"]
	properties = farm["properties"]
	farmname = farm["name"]
	farmdescription = farm["description"]
	wind_dir = properties["wind_direction"]
	wind_speed = properties["wind_speed"]
	layoutx = properties["layout_x"]
	layouty = properties["layout_y"]


# initial power output
power_initial = np.sum(fi.get_turbine_power())

# ================================================================================
print('Plotting the FLORIS flowfield...')
# ================================================================================

# Initialize the horizontal cut
hor_plane = wfct.cut_plane.HorPlane(
    fi.get_hub_height_flow_data(),
    fi.floris.farm.turbines[0].hub_height
)

# Plot and show
fig, ax = plt.subplots()
wfct.visualization.visualize_cut_plane(hor_plane, ax=ax)
name = 'Wind farm without yaw control {} {} deg.png'
plt.savefig(name.format(farmname, wind_dir))
plt.close()
os.startfile(name.format(farmname, wind_dir))


# ================================================================================
print('Finding optimal yaw angles in FLORIS...')
# ================================================================================
# set bounds for allowable wake steering
min_yaw = 0.0
max_yaw = 25.0
yaw_angles = optimize_yaw(fi, min_yaw, max_yaw)

print('yaw angles = ')
for i in range(len(yaw_angles)):
    print('Turbine ', i, '=', yaw_angles[i], ' deg')

# assign yaw angles to turbines and calculate wake
fi.calculate_wake(yaw_angles=yaw_angles)
power_opt = np.sum(fi.get_turbine_power())

#Creating a power gain variable for power comparison
power_gain = 100.*(power_opt - power_initial)/power_initial

print('==========================================')
print('Total Power Gain = %.1f%%' %
      (100.*(power_opt - power_initial)/power_initial))
print('==========================================')
# ================================================================================
print('Plotting the FLORIS flowfield with yaw...')
# ================================================================================

#Rounding the yaw angles to two decimals
yaw_angles = np.round(yaw_angles, decimals=2)
power_gain = round(power_gain, 4)
print(power_gain)


#Creating a .txt file with the input and output data of the yaw optimization and automatically saving it
with open('AlphaVentus_test_output.txt', 'w') as f:
	f.write('Data from the wind farm yaw optimization\n')
	f.write('\n-Farm name: ')
	f.write(farmname)
	f.write('\n-Description: ')
	f.write(farmdescription)
	f.write('\n-Wind direction (deg): ')
	f.write(str(wind_dir))
	f.write('\n-Wind speed (m/s): ')
	f.write(str(wind_speed))
	f.write('\n-Wind farm coordinates (in meters):\n')
	f.write('\n ---X-coordinates:')
	f.write(str(layoutx))
	f.write('\n ---Y-coordinates:')
	f.write(str(layouty))
	f.write('\n\n-Yaw angles after optimization:\n')
	f.write(str(yaw_angles))
	f.write('\n\n-Power before the optimization (MWh per year):')
	f.write(str(power_initial))
	f.write('\n-Power after the optimization (MWh per year):')
	f.write(str(power_opt))
	f.write('\n\n-Total gain in power production from yaw angle optimization: ')
	f.write(str(power_gain))
	f.write(' %')

os.startfile('AlphaVentus_test_output.txt')


# Initialize the horizontal cut
hor_plane = wfct.cut_plane.HorPlane(
    fi.get_hub_height_flow_data(),
    fi.floris.farm.turbines[0].hub_height
)

# Plot and show
ig, ax = plt.subplots()
wfct.visualization.visualize_cut_plane(hor_plane, ax=ax)
name = 'Wind farm yaw optimized {} {} deg.png'
plt.savefig(name.format(farmname, wind_dir))
plt.close()
os.startfile(name.format(farmname, wind_dir))
