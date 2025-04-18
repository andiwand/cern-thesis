include: "../common.smk"


rule all_reconstruction:
    input:
        expand("data/odd-performance/reco/{event_sim_reco_label}/{reco_output}", event_sim_reco_label=EVENT_SIM_RECO_LABELS, reco_output=RECO_OUTPUTS)


rule reconstruction:
    input:
        script = "scripts/odd-performance/reconstruction.py",
        sim = expand("data/odd-performance/sim/{event_sim_label}/{sim_output}", event_sim_label=get_event_sim_label, sim_output=SIM_OUTPUTS),
    output:
        expand("data/odd-performance/reco/{{event_sim_reco_label}}/{reco_output}", reco_output=RECO_OUTPUTS),
    params:
        simdir = expand("data/odd-performance/sim/{event_sim_label}", event_sim_label=get_event_sim_label),
        outdir = "data/odd-performance/reco/{event_sim_reco_label}",
        events = get_number_of_events,
    log:
        stdout = "data/odd-performance/reco/{event_sim_reco_label}/stdout.txt",
        stderr = "data/odd-performance/reco/{event_sim_reco_label}/stderr.txt",
    threads: get_reco_threads
    resources:
        mem_mb = get_reco_mem_mb,
    shell:
        """
        scripts/activate_and_run.sh python {input.script} \
          {wildcards.event_sim_reco_label} \
          {params.outdir} \
          --simdir {params.simdir} \
          --skip 0 \
          --events {params.events} \
          --threads {threads} \
          > {log.stdout} \
          2> {log.stderr}
        """
