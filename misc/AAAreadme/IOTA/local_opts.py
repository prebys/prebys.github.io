#!/usr/bin/env python

# The local_options file must be named local_opts.py and placed
# in the Synergia2 job manager search path.

from synergia_workflow import options

# Any instance of the Options class will be added as a suboption.
opts = options.Options('local')
opts.add("loadbalance",True,"whether to specify --loadbalance for mpirun", bool)


# Any instance of the Override class will be used to override
#   the defaults of the existing options.
override = options.Override()
override.account = "iota"
override.numproc = 32
override.procspernode=32
override.queue="amd32"
override.walltime="24:00:00"
# use local copy of synergia setup file
override.setupsh="/home/prebys/synergia2-devel/setup.sh"
# comment these out so that it will use the local file
#override.template="job_example_wilson"
#override.resumetemplate="resume_example_wilson"
#override.templatepath="full path to template file"
