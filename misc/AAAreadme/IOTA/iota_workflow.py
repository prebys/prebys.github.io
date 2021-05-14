# !/usr/bin/env synergia
# import a bunch of stuff
import synergia
import numpy as np
import sys


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

from iota_workflow_options import opts

#
# This module defines the ramp actions, which will be performed each turn.
#
class Ramp_actions(synergia.simulation.Propagate_actions):
    def __init__(self):
        synergia.simulation.Propagate_actions.__init__(self)
    def turn_end_action(self, stepper, bunch, turn_num):
        print "modifying lattice, turn number: ",turn_num
        for element in stepper.get_lattice_simulator().get_lattice().get_elements():
            if element.get_name() == "cavity1":
                if turn_num>=opts.t1:
                  rfvoltage=opts.rfV1
                else:
                  rfvoltage=opts.rfV0/(1-(1-np.sqrt(opts.rfV0/opts.rfV1))*turn_num/opts.t1)**2
                element.set_double_attribute("volt", rfvoltage)
                print "  updated", element.get_name()," RF1 voltage to ",element.get_double_attribute("volt")
            if element.get_name() == "cavity2":
                if turn_num<opts.t20:
                  rfvoltage = 0.
                elif turn_num>=opts.t21:
                  rfvoltage = opts.rf2V1
                else:
                  t = turn_num-opts.t20
                  t1 = opts.t21-opts.t20
                  rfvoltage=opts.rf2V0/(1-(1-np.sqrt(opts.rf2V0/opts.rf2V1))*t/t1)**2
                element.set_double_attribute("volt", rfvoltage)
                print "  updated", element.get_name()," RF2 voltage to ",element.get_double_attribute("volt")
                  
        stepper.get_lattice_simulator().update()


# Check that the RF makes sense
if opts.rfV0>opts.rfV1:
  print "Warning, V0>V1.  Setting V0=V1"
  opts.rfV0=opts.rfV1
if opts.rf2V0>opts.rf2V1:
  print "Warning, V20>V21. Setting V20=V21"
  opts.rf2V0=opts.rf2V1

opts.t1=0
if opts.rfV1>opts.rfV0:
#
#  The details of this calculation are in the numbers.xlsx worksheet.
#  They were originally done for v0=10V (.000010) and h=55.  tune scales
#  as the sqrt of V0*h
  omegaS = 0.025329464*np.sqrt(opts.rfV0/.000010*opts.harmonic/55)
  opts.t1 = (1-np.sqrt(opts.rfV0/opts.rfV1))*opts.adiabaticity/omegaS
  print "V0,V1,omegaS,t1:",opts.rfV0,", ",opts.rfV1,", ",omegaS,", ",opts.t1

# Set up the second RF curve
opts.t20=opts.t1+opts.rf2_wait
opts.t21=opts.t20
if opts.rf2V1>opts.rf2V0:
  omegaS = 0.025329464*np.sqrt(opts.rf2V0/.000010*opts.harmonic2/55)
  opts.t21 = opts.t20+(1-np.sqrt(opts.rfV0/opts.rfV1))*opts.adiabaticity/omegaS
  print "V20,V21,omegaS,t20,t21:",opts.rf2V0,", ",opts.rf2V1,", ",omegaS,", ",opts.t20,", ",opts.t21
  

# Define a lattice
#     Read the lattice named "machine" from the Madx file "iota6.madx"
lattice = synergia.lattice.MadX_reader().get_lattice("machine", "iota6_protons.madx")
# This is a workaround by Eric Stern to get around a memory leak problem
for elem in lattice.get_elements():
   if elem.get_type() == "quadrupole":
       elem.set_string_attribute("propagator_type", "basic")
#
# Reset the RF harmonic
for element in lattice.get_elements():
	if element.get_name() == "cavity1":
		element.set_double_attribute("harmon",opts.harmonic)
		print "  updated", element.get_name()," harmonic to ",element.get_double_attribute("harmon")
	if element.get_name() == "cavity2":
		element.set_double_attribute("harmon",opts.harmonic2)
		print "  updated", element.get_name()," harmonic to ",element.get_double_attribute("harmon")



# Define a bunch
x_emit = opts.x_emit  # m-rad, RMS
x_normcut = opts.x_normcut  # x emittance cut (admittance/emittance)
y_emit = opts.y_emit  # m-rad, RMS
y_normcut = opts.y_normcut  # y emittance cut (admittance/emittance)
z_std = 2*.0018  # z bunch size, 
dpop = 1e-3  # unitless, RMS \frac{\delta p}{p_{tot}}
real_particles = opts.real_particles  # real particles, used for space charge, impedance, etc
if opts.rfV1==0.:
  z_period = 6.73E-02 # space between bunches
else:
#  z_period = 0.726695086 # corresponds to RF frequency
  z_period = 0.726695086*55./opts.harmonic # corresponds to RF frequency
  real_particles *= z_period/6.73E-02  # scale to particles in RF bucket

# correct for emittance cut, if any
if x_normcut>0.:
	real_particles *= (1.-np.exp(-x_normcut))
if y_normcut>0.:
    real_particles *= (1.-np.exp(-y_normcut))

macro_particles = opts.macro_particles # Used for PIC calculations

# Set up the space charge model
commxx = Commxx()
grid = [opts.ncell, opts.ncell, opts.ncell]  

if opts.space_charge==3:
   space_charge = Space_charge_3d_open_hockney(commxx, grid)
elif opts.space_charge==2: 
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

# get lattice elements
last_lattice_element = lattice.get_elements()[-1]

lf = stepper.get_lattice_simulator().get_lattice_functions(last_lattice_element)
beta_x = lf.beta_x
alpha_x = lf.alpha_x
gamma_x = (1+alpha_x**2)/beta_x


beta_y = lf.beta_y
alpha_y = lf.alpha_y
gamma_y = (1+alpha_y**2)/beta_y

print "beta x: ", beta_x
print "alpha x: ", alpha_x
print "gamma x: ", gamma_x
print "beta y: ", beta_y
print "alpha y: ", alpha_y
print "gamma y: ", gamma_y



# Create a periodic bunch that matches the optics
seed = 1415926  # random number seed; 0 for automatic calculation (GSL)

#bunch = synergia.optics.generate_matched_bunch_transverse(
#             lattice_simulator,
#              x_emit, y_emit, z_std, dpop,
#              real_particles, macro_particles,
#              seed=seed,z_period_length=z_period)
#z_period = bunch.get_z_period_length()
#print z_period

# Build a bunch by hand

ref = lattice.get_reference_particle()

beta = ref.get_beta()
print "beta = ", beta

bunch = synergia.bunch.Bunch(
    ref,
    macro_particles, real_particles, commxx, z_period)


local_particles = bunch.get_local_particles()
local_num = bunch.get_local_num()

#generate a 2D Gaussian distribution
dist = synergia.foundation.Random_distribution(seed,commxx)

# generate x distribution
rx = np.zeros(local_num,'d')
# deal with emittance cut
xmax = 1.
if x_normcut>0.:
  xmax = 1-np.exp(-x_normcut)

dist.fill_uniform(rx,0.,xmax)
rx = -np.log(1-rx)
rx = np.sqrt(2.*rx) 

thetax = np.zeros(local_num,'d')
dist.fill_uniform(thetax, 0., 2.0*np.pi)

x_std = np.sqrt(x_emit*beta_x)
xp_std = np.sqrt(x_emit*gamma_x)
local_particles[:,0] = rx*np.cos(thetax)
local_particles[:,1] = rx*np.sin(thetax) - alpha_x*local_particles[:,0]

local_particles[:,0] *= x_std
local_particles[:,1] *= xp_std

# generate y distribution
ry = np.zeros(local_num,'d')
# deal with emittance cut
ymax = 1.
if y_normcut>0.:
  ymax = 1-np.exp(-y_normcut)


dist.fill_uniform(ry,0.,ymax)

ry = -np.log(1-ry)
ry = np.sqrt(2.*ry) 

thetay = np.zeros(local_num,'d')
dist.fill_uniform(thetay, 0., 2.0*np.pi)

y_std = np.sqrt(y_emit*beta_y)
yp_std = np.sqrt(y_emit*gamma_y)
local_particles[:,2] = ry*np.cos(thetay)
local_particles[:,3] = ry*np.sin(thetay) - alpha_y*local_particles[:,2]

local_particles[:,2] *= y_std
local_particles[:,3] *= yp_std

#generate z distribution (actually cdt)
cdtdist = np.zeros(local_num, 'd')
if opts.rfV1==0.:
  dist.fill_unit_gaussian(cdtdist)
  local_particles[:,4] = cdtdist*z_std/beta

else:
  dist.fill_uniform(cdtdist,-.5,.5)
  local_particles[:,4] = cdtdist*z_period/beta

dpopdist = np.zeros(local_num,'d')
dist.fill_unit_gaussian(dpopdist)
local_particles[:,5] = dpopdist*dpop


# Define a bunch simulator
bunch_simulator = Bunch_simulator(bunch)

# Define a set of bunch diagnostics
#     Apply *average* bunch diagnostics every step
diagnostics = Diagnostics_full2("diagnostics.h5")

#this file gets really big if we do a lot of turns
if opts.turns<10: 
  bunch_simulator.add_per_step(diagnostics)
else:
  bunch_simulator.add_per_turn(diagnostics)

# apply macroparticle diagnostics every n turns
tracker = Diagnostics_particles("tracks.h5")
bunch_simulator.add_per_turn(tracker,opts.turns_step)

ramp_actions = Ramp_actions()
# test the RF curve
#for i in range(0,opts.turns):
#  ramp_actions.turn_end_action(stepper,bunch,i)
  
#sys.exit(2)  


# Perform the simulation
propagator = Propagator(stepper)
max_turns = 0 # Number of turns to run before writing checkpoint and stopping
              # When max_turns is 0, the simulation continues until the end.
verbosity = 1  # Display information about each simulation turn
propagator.propagate(bunch_simulator, ramp_actions,opts.turns, max_turns, verbosity)
