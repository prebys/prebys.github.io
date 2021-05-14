#!/usr/bin/env python

from synergia_workflow import Options, Job_manager

opts = Options("iota_workflow")
opts.add("real_particles",1.5e8,"Number of real particles")
opts.add("macro_particles",50000,"Number of macro particles")
opts.add("space_charge",0,"0,1=no space charge, 2=2D, 3=3D")
opts.add("turns", 1, "Number of times to track through fodo lattice")
opts.add("turns_step",1,"Number of turns between beam diags")
opts.add("ncell",32,"Number of cells for space charge simulation grid")
opts.add("x_emit",3.9e-6,"x emittance [m-rad]")
opts.add("y_emit",3.9e-6,"y emittance [m-rad]")
opts.add("x_normcut",0.,"x normalize emittance cut (admittance/emittance)")
opts.add("y_normcut",0.,"y normalize emittance cut (admittance/emittance)")
opts.add("harmonic",4,"RF harmonic")
opts.add("rfV0",.000010,"Initial voltage of RF (MV)")
opts.add("rfV1",.001000,"Final voltage or RF (MV)")
opts.add("adiabaticity",10,"RF adiabaticity")
opts.add("harmonic2",56,"2nd RF Harmonic")
opts.add("rf2_wait",100,"Turns to wait before second RF harmonic")
opts.add("rf2V0",0.,"Initial voltage of second RF harmonic (MV)")
opts.add("rf2V1",0.,"Final voltage of second RF harmonic (MV)")
# Create the job manager for the simulation fodo_workflow.py, including the 
# above options. When creating job directories, include the file fodo.lat.
job_mgr = Job_manager("iota_workflow.py", opts, ["iota6_protons.madx"])

