include: "../common.smk"


rule all_scan:
    input:
        "data/odd-performance/scan/fatras/propagation_summary.root",
        "data/odd-performance/scan/fatras/material_tracks.root",
        "data/odd-performance/scan/geant4/material_tracks.root",

rule fatras_scan:
    input:
        script = "scripts/odd-performance/detector_scan.py",
    output:
        "data/odd-performance/scan/fatras/propagation_summary.root",
        "data/odd-performance/scan/fatras/material_tracks.root",
    params:
        outdir = "data/odd-performance/scan/fatras",
        skip = 0,
        events = config["scan"]["number_of_events"],
    log:
        stdout = "data/odd-performance/scan/fatras/stdout.txt",
        stderr = "data/odd-performance/scan/fatras/stderr.txt",
    threads: get_scan_threads
    shell:
        """
        scripts/activate_and_run.sh python {input.script} \
          fatras \
          {params.outdir} \
          --skip {params.skip} \
          --events {params.events} \
          --threads {threads} \
          > {log.stdout} \
          2> {log.stderr}
        """

rule geant4_scan:
    input:
        script = "scripts/odd-performance/detector_scan.py",
    output:
        "data/odd-performance/scan/geant4/material_tracks.root",
    params:
        outdir = "data/odd-performance/scan/geant4",
        skip = 0,
        events = config["scan"]["number_of_events"],
    log:
        stdout = "data/odd-performance/scan/geant4/stdout.txt",
        stderr = "data/odd-performance/scan/geant4/stderr.txt",
    threads: get_scan_threads
    shell:
        """
        scripts/activate_and_run.sh python {input.script} \
          geant4 \
          {params.outdir} \
          --skip {params.skip} \
          --events {params.events} \
          --threads {threads} \
          > {log.stdout} \
          2> {log.stderr}
        """
