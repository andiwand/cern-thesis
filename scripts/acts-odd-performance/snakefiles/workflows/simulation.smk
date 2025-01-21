include: "../common.smk"


rule all_simulation:
    input:
        expand("data/acts-odd-performance/sim/{event_sim_label}/{sim_output}", event_sim_label=EVENT_SIM_LABELS, sim_output=SIM_OUTPUTS)


rule simulation:
    input:
        script = "scripts/acts-odd-performance/simulation.py",
    output:
        expand("data/acts-odd-performance/sim/{{event_sim_label}}/{sim_output}", sim_output=SIM_OUTPUTS),
    params:
        outdir = "data/acts-odd-performance/sim/{event_sim_label}",
        skip = 0,
        events = get_number_of_events,
    log:
        stdout = "data/acts-odd-performance/sim/{event_sim_label}/stdout.txt",
        stderr = "data/acts-odd-performance/sim/{event_sim_label}/stderr.txt",
    threads: get_sim_threads
    shell:
        """
        scripts/activate_and_run.sh python {input.script} \
          {wildcards.event_sim_label} \
          {params.outdir} \
          --skip {params.skip} \
          --events {params.events} \
          --threads {threads} \
          > {log.stdout} \
          2> {log.stderr}
        """
