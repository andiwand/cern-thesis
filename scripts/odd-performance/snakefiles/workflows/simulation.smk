include: "../common.smk"


rule all_simulation:
    input:
        expand("data/odd-performance/sim/{event_sim_label}/{sim_output}", event_sim_label=EVENT_SIM_LABELS, sim_output=SIM_OUTPUTS)


rule simulation:
    input:
        expand(
            "data/odd-performance/sim/{{event_sim_label}}/slices/{skip}_{events}/{{sim_output}}",
            skip=get_skip_events,
            events=get_events_per_slice,
        ),
    output:
        "data/odd-performance/sim/{event_sim_label}/{sim_output}",
    shell:
        """
        scripts/activate_and_run.sh hadd -f {output} {input}
        rm -f {input}
        """


rule simulation_slice:
    input:
        script = "scripts/odd-performance/simulation.py",
    output:
        expand("data/odd-performance/sim/{{event_sim_label}}/slices/{{skip}}_{{events}}/{sim_output}", sim_output=SIM_OUTPUTS),
    params:
        outdir = "data/odd-performance/sim/{event_sim_label}/slices/{skip}_{events}",
    log:
        stdout = "data/odd-performance/sim/{event_sim_label}/slices/{skip}_{events}/stdout.txt",
        stderr = "data/odd-performance/sim/{event_sim_label}/slices/{skip}_{events}/stderr.txt",
    threads: get_sim_threads
    resources:
        mem_mb = get_sim_mem_mb
    shell:
        """
        scripts/activate_and_run.sh python {input.script} \
          {wildcards.event_sim_label} \
          {params.outdir} \
          --skip {wildcards.skip} \
          --events {wildcards.events} \
          --threads {threads} \
          > {log.stdout} \
          2> {log.stderr}
        """
