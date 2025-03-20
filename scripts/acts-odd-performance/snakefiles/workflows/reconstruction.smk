include: "../common.smk"


rule all_reconstruction:
    input:
        expand("data/acts-odd-performance/reco/{reco_label}/{event_sim_label}/{reco_output}", reco_label=RECO_LABELS, event_sim_label=EVENT_SIM_LABELS, reco_output=RECO_OUTPUTS)


rule reconstruction:
    input:
        script = "scripts/acts-odd-performance/reconstruction.py",
        sim = expand("data/acts-odd-performance/sim/{{event_sim_label}}/{sim_output}", sim_output=SIM_OUTPUTS),
    output:
        expand("data/acts-odd-performance/reco/{{reco_label}}/{{event_sim_label}}/{reco_output}", reco_output=RECO_OUTPUTS),
    params:
        outdir = "data/acts-odd-performance/reco/{reco_label}/{event_sim_label}",
        events = get_number_of_events,
    log:
        stdout = "data/acts-odd-performance/reco/{reco_label}/{event_sim_label}/stdout.txt",
        stderr = "data/acts-odd-performance/reco/{reco_label}/{event_sim_label}/stderr.txt",
    threads: get_reco_threads
    resources:
        mem_mb = get_reco_mem_mb,
    shell:
        """
        scripts/activate_and_run.sh python {input.script} \
          {wildcards.event_sim_label} \
          {wildcards.reco_label} \
          {params.outdir} \
          --simdir data/acts-odd-performance/sim/{wildcards.event_sim_label} \
          --skip 0 \
          --events {params.events} \
          --threads {threads} \
          > {log.stdout} \
          2> {log.stderr}
        """
