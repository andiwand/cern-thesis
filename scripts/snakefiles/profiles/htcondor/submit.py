#!/usr/bin/env python3

import sys
import htcondor
from os import makedirs
from os.path import join
from uuid import uuid4

from snakemake.utils import read_job_properties


jobscript = sys.argv[1]
job_properties = read_job_properties(jobscript)

UUID = uuid4()  # random UUID
jobDir = "/afs/cern.ch/user/a/astefl/condor_jobs/{}_{}".format(
    job_properties["jobid"], UUID
)
makedirs(jobDir, exist_ok=True)

col = htcondor.Collector()
credd = htcondor.Credd()
credd.add_user_cred(htcondor.CredTypes.Kerberos, None)

sub = htcondor.Submit(
    {
        "executable": jobscript,
        "arguments": "",
        "max_retries": "0",
        "log": join(jobDir, "condor.log"),
        "output": join(jobDir, "condor.out"),
        "error": join(jobDir, "condor.err"),
        "MY.WantOS": "el9",
        "MY.SendCredential": True,
        "+JobFlavour": '"workday"',
        "request_cpus": "1",
        "request_memory": "8GB",
    }
)

request_memory = job_properties["resources"].get("mem_mb", None)
if request_memory is not None:
    sub["request_memory"] = str(request_memory)

request_disk = job_properties["resources"].get("disk_mb", None)
if request_disk is not None:
    sub["request_disk"] = str(request_disk)

schedd = htcondor.Schedd()
clusterID = schedd.submit(sub)

# print jobid for use in Snakemake
print("{}_{}_{}".format(job_properties["jobid"], UUID, clusterID))
