# !/usr/bin/env synergia
# import a bunch of stuff
import synergia
from synergia.foundation import Four_momentum, Random_distribution,Reference_particle, pconstants
from synergia.utils import Commxx
from synergia.lattice import MadX_reader, Lattice
from synergia.bunch import Bunch, populate_6d, Diagnostics_basic, Diagnostics_full2, Diagnostics_particles, \
    Diagnostics_track
from synergia.simulation import Independent_stepper_elements, Bunch_simulator, \
    Propagator, Split_operator_stepper, \
    Split_operator_stepper_elements, Dummy_collective_operator
from synergia.collective import Space_charge_2d_bassetti_erskine, \
    Space_charge_2d_open_hockney, \
    Space_charge_3d_open_hockney

# space charge or no space charge
use_space_charge=1
# fill ring with uniform beam
turns=30 # number of turns

# Define a lattice
#     Read the lattice named "machine" from the Madx file "iota6.madx"
lattice = synergia.lattice.MadX_reader().get_lattice("machine", "iota6_protons.madx")

# Define a bunch
x_emit = 3.9e-6  # m-rad, RMS
y_emit = 3.9e-6  # m-rad, RMS
z_std = 2*.0018  # z bunch size, 
z_period = 6.73E-02 # space between bunches
dpop = 1e-3  # unitless, RMS \frac{\delta p}{p_{tot}}
real_particles = 1.5e8  # real particles, used for space charge, impedance, etc
macro_particles = 50000 # Used for PIC calculations

# Set up the space charge model
commxx = Commxx(True)
grid = [32, 32, 32]  

if use_space_charge==1: 
   space_charge = Space_charge_2d_open_hockney(commxx, grid)
else:
   space_charge = Dummy_collective_operator("null space charge")

# Define a set of simulation steps
map_order = 1
steps_per_element = 1  # simulation steps per element

# this tells it to do both a tracking simulation and
# and a space charge update at each stepp
stepper = Split_operator_stepper_elements(lattice, map_order,
                                              space_charge,
                                              steps_per_element)
lattice_simulator = stepper.get_lattice_simulator()

# Create a periodic bunch that matches the optics
seed = 1415926  # random number seed; 0 for automatic calculation (GSL)
bunch = synergia.optics.generate_matched_bunch_transverse(
             lattice_simulator,
              x_emit, y_emit, z_std, dpop,
              real_particles, macro_particles,
              seed=seed,z_period_length=z_period)
z_period = bunch.get_z_period_length()
print z_period

# Define a bunch simulator
bunch_simulator = Bunch_simulator(bunch)

# Define a set of bunch diagnostics
#     Apply *average* bunch diagnostics every step
diagnostics = Diagnostics_full2("diagnostics.h5")
bunch_simulator.add_per_step(diagnostics)

# apply macroparticle diagnostics every n turns
tracker = Diagnostics_particles("tracks.h5")
bunch_simulator.add_per_turn(tracker,10)

# Perform the simulation
propagator = Propagator(stepper)
max_turns = 0 # Number of turns to run before writing checkpoint and stopping
              # When max_turns is 0, the simulation continues until the end.
verbosity = 2  # Display information about each simulation step
propagator.propagate(bunch_simulator, turns, max_turns, verbosity)
