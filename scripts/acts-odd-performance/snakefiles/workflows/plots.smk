include: "../common.smk"

rule all_plots:
    input:
        "plots/acts-odd-performance/detector_material.pdf",
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/detector_efficiency_mixed.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),

        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_duplication.pdf", sim_label=SIM_LABELS, seeding_label=["truth-estimated", "triplet"]),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_mu.pdf", sim_label=SIM_LABELS, seeding_label=["truth-estimated", "triplet"]),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_mixed.pdf", sim_label=SIM_LABELS, seeding_label=["truth-estimated", "triplet"]),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_ttbar.pdf", sim_label=SIM_LABELS, seeding_label=["truth-estimated", "triplet"]),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_fake_ttbar.pdf", sim_label=SIM_LABELS, seeding_label=["truth-estimated", "triplet"]),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_ttbar_pileup.pdf", sim_label=SIM_LABELS, seeding_label=["truth-estimated", "triplet"]),

        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_duplication.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_efficiency_mu.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_efficiency_mixed.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_efficiency_ttbar.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_fake_ttbar.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_efficiency_ttbar_pileup.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),

        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/fitting_resolution_d0_vs_eta_mu.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/fitting_resolution_z0_vs_pt_mixed.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/fitting_pullmean_vs_eta_mu.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/fitting_pullwidth_vs_eta_mu.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),

        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/ambi_efficiency_ttbar.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/ambi_duplication_ttbar.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),

        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/refit_resolution_d0_vs_eta_mu.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/refit_resolution_z0_vs_pt_mixed.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/refit_pullmean_vs_eta_mu.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/refit_pullwidth_vs_eta_mu.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),

        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/vertex_resolution.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/vertex_pull.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/vertex_efficiency.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/vertex_contamination.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),

        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/cpu_total_ttbar.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/cpu_alg_ttbar.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),

rule plot_detector_material:
    input:
        script = "scripts/acts-odd-performance/plot_detector_material.py",
        scan_acts = "data/acts-odd-performance/scan/fatras/material_tracks.root",
        scan_geant4 = "data/acts-odd-performance/scan/geant4/material_tracks.root",
    output:
        "plots/acts-odd-performance/detector_material.pdf",
    shell:
        """
        python {input.script} {input.scan_acts} {input.scan_geant4} --output {output}
        """

rule plot_detector_efficiency_mixed:
    input:
        script = "scripts/acts-odd-performance/plot_detector_efficiency_mixed.py",
        reco_particles = expand("data/acts-odd-performance/reco/1{ptype}-pt10GeV_{{sim_label}}_{{seeding_label}}/particles_selected.root", ptype=["mu", "pi", "e"]),
        sim_particles = expand("data/acts-odd-performance/sim/1{ptype}-pt10GeV_{{sim_label}}/particles.root", ptype=["mu", "pi", "e"]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/detector_efficiency_mixed.pdf",
    shell:
        """
        python {input.script} {input.reco_particles} {input.sim_particles} --output {output}
        """

rule plot_seeding_duplication:
    input:
        script = "scripts/acts-odd-performance/plot_seeding_duplication.py",
        reco = "data/acts-odd-performance/reco/1mu-pt1GeV_{sim_label}_{seeding_label}/performance_seeding.root",
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_duplication.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_seeding_efficiency_mu:
    input:
        script = "scripts/acts-odd-performance/plot_seeding_efficiency_mu.py",
        reco = expand("data/acts-odd-performance/reco/1mu-pt{pt}GeV_{{sim_label}}_{{seeding_label}}/performance_seeding.root", pt=[1,10,100]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_mu.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_seeding_efficiency_mixed:
    input:
        script = "scripts/acts-odd-performance/plot_seeding_efficiency_mixed.py",
        reco = expand("data/acts-odd-performance/reco/1{ptype}-pt10GeV_{{sim_label}}_{{seeding_label}}/performance_seeding.root", ptype=["mu", "pi", "e"]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_mixed.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_seeding_efficiency_ttbar:
    input:
        script = "scripts/acts-odd-performance/plot_seeding_efficiency_ttbar.py",
        reco = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_seeding.root", pu=[0, 60, 120, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_ttbar.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_seeding_fake_ttbar:
    input:
        script = "scripts/acts-odd-performance/plot_seeding_fake_ttbar.py",
        reco = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_seeding.root", pu=[0, 60, 120, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_fake_ttbar.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_seeding_efficiency_ttbar_pileup:
    input:
        script = "scripts/acts-odd-performance/plot_seeding_efficiency_ttbar_pileup.py",
        reco = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_seeding.root", pu=[0, 30, 60, 90, 120, 150, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_ttbar_pileup.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_finding_duplication:
    input:
        script = "scripts/acts-odd-performance/plot_finding_duplication.py",
        reco = "data/acts-odd-performance/reco/1mu-pt1GeV_{sim_label}_{seeding_label}/performance_finding_ckf.root",
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_duplication.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_finding_efficiency_mu:
    input:
        script = "scripts/acts-odd-performance/plot_finding_efficiency_mu.py",
        reco = expand("data/acts-odd-performance/reco/1mu-pt{pt}GeV_{{sim_label}}_{{seeding_label}}/performance_finding_ckf.root", pt=[1,10,100]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_efficiency_mu.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_finding_efficiency_mixed:
    input:
        script = "scripts/acts-odd-performance/plot_finding_efficiency_mixed.py",
        reco = expand("data/acts-odd-performance/reco/1{ptype}-pt10GeV_{{sim_label}}_{{seeding_label}}/performance_finding_ckf.root", ptype=["mu", "pi", "e"]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_efficiency_mixed.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_finding_efficiency_ttbar:
    input:
        script = "scripts/acts-odd-performance/plot_finding_efficiency_ttbar.py",
        reco = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_finding_ckf.root", pu=[0, 60, 120, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_efficiency_ttbar.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_finding_fake_ttbar:
    input:
        script = "scripts/acts-odd-performance/plot_finding_fake_ttbar.py",
        reco = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_finding_ckf.root", pu=[0, 60, 120, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_fake_ttbar.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_finding_efficiency_ttbar_pileup:
    input:
        script = "scripts/acts-odd-performance/plot_finding_efficiency_ttbar_pileup.py",
        reco = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_finding_ckf.root", pu=[0, 30, 60, 90, 120, 150, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_efficiency_ttbar_pileup.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_fitting_resolution_d0_vs_eta_mu:
    input:
        script = "scripts/acts-odd-performance/plot_fitting_resolution_d0_vs_eta_mu.py",
        reco = expand("data/acts-odd-performance/reco/1mu-pt{pt}GeV_{{sim_label}}_{{seeding_label}}/performance_fitting_ckf.root", pt=[1,10,100]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/fitting_resolution_d0_vs_eta_mu.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_fitting_resolution_z0_vs_pt_mixed:
    input:
        script = "scripts/acts-odd-performance/plot_fitting_resolution_z0_vs_pt_mixed.py",
        reco = expand("data/acts-odd-performance/reco/1{ptype}-pt1-100GeV_{{sim_label}}_{{seeding_label}}/performance_fitting_ckf.root", ptype=["mu", "pi", "e"]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/fitting_resolution_z0_vs_pt_mixed.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_fitting_pullmean_vs_eta_mu:
    input:
        script = "scripts/acts-odd-performance/plot_fitting_pullmean_vs_eta_mu.py",
        reco = expand("data/acts-odd-performance/reco/1mu-pt{pt}GeV_{{sim_label}}_{{seeding_label}}/performance_fitting_ckf.root", pt=[1,10,100]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/fitting_pullmean_vs_eta_mu.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_fitting_pullwidth_vs_eta_mu:
    input:
        script = "scripts/acts-odd-performance/plot_fitting_pullwidth_vs_eta_mu.py",
        reco = expand("data/acts-odd-performance/reco/1mu-pt{pt}GeV_{{sim_label}}_{{seeding_label}}/performance_fitting_ckf.root", pt=[1,10,100]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/fitting_pullwidth_vs_eta_mu.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_ambi_efficiency_ttbar:
    input:
        script = "scripts/acts-odd-performance/plot_ambi_efficiency_ttbar.py",
        ckf = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_finding_ckf.root", pu=[0, 60, 120, 200]),
        ambi = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_finding_ambi.root", pu=[0, 60, 120, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/ambi_efficiency_ttbar.pdf",
    shell:
        """
        python {input.script} {input.ambi} {input.ckf} --output {output}
        """

rule plot_ambi_duplication_ttbar:
    input:
        script = "scripts/acts-odd-performance/plot_ambi_duplication_ttbar.py",
        ckf = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_finding_ckf.root", pu=[0, 60, 120, 200]),
        ambi = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_finding_ambi.root", pu=[0, 60, 120, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/ambi_duplication_ttbar.pdf",
    shell:
        """
        python {input.script} {input.ambi} {input.ckf} --output {output}
        """

rule plot_refit_resolution_d0_vs_eta_mu:
    input:
        script = "scripts/acts-odd-performance/plot_fitting_resolution_d0_vs_eta_mu.py",
        reco = expand("data/acts-odd-performance/reco/1mu-pt{pt}GeV_{{sim_label}}_{{seeding_label}}/performance_fitting_kfrefit.root", pt=[1,10,100]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/refit_resolution_d0_vs_eta_mu.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_refit_resolution_z0_vs_pt_mixed:
    input:
        script = "scripts/acts-odd-performance/plot_fitting_resolution_z0_vs_pt_mixed.py",
        reco = expand("data/acts-odd-performance/reco/1{ptype}-pt1-100GeV_{{sim_label}}_{{seeding_label}}/performance_fitting_kfrefit.root", ptype=["mu", "pi", "e"]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/refit_resolution_z0_vs_pt_mixed.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_refit_pullmean_vs_eta_mu:
    input:
        script = "scripts/acts-odd-performance/plot_fitting_pullmean_vs_eta_mu.py",
        reco = expand("data/acts-odd-performance/reco/1mu-pt{pt}GeV_{{sim_label}}_{{seeding_label}}/performance_fitting_kfrefit.root", pt=[1,10,100]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/refit_pullmean_vs_eta_mu.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_refit_pullwidth_vs_eta_mu:
    input:
        script = "scripts/acts-odd-performance/plot_fitting_pullwidth_vs_eta_mu.py",
        reco = expand("data/acts-odd-performance/reco/1mu-pt{pt}GeV_{{sim_label}}_{{seeding_label}}/performance_fitting_kfrefit.root", pt=[1,10,100]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/refit_pullwidth_vs_eta_mu.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_vertex_resolution:
    input:
        script = "scripts/acts-odd-performance/plot_vertex_resolution.py",
        reco = "data/acts-odd-performance/reco/ttbar-pu200_{sim_label}_pu0-{seeding_label}/performance_amvf_truth_time.root",
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/vertex_resolution.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_vertex_pull:
    input:
        script = "scripts/acts-odd-performance/plot_vertex_pull.py",
        reco = "data/acts-odd-performance/reco/ttbar-pu200_{sim_label}_pu0-{seeding_label}/performance_amvf_truth_time.root",
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/vertex_pull.pdf",
    shell:
        """
        python {input.script} {input.reco} --output {output}
        """

rule plot_vertex_efficiency:
    input:
        script = "scripts/acts-odd-performance/plot_vertex_efficiency.py",
        reco_amvf_wot = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_amvf_truth_notime.root", pu=[0, 30, 60, 90, 120, 150, 200]),
        reco_amvf_wt = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_amvf_truth_time.root", pu=[0, 30, 60, 90, 120, 150, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/vertex_efficiency.pdf",
    shell:
        """
        python {input.script} --inputs-wot {input.reco_amvf_wot} --inputs-wt {input.reco_amvf_wt} --output {output}
        """

rule plot_vertex_contamination:
    input:
        script = "scripts/acts-odd-performance/plot_vertex_contamination.py",
        reco_amvf_wot = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_amvf_truth_notime.root", pu=[0, 30, 60, 90, 120, 150, 200]),
        reco_amvf_wt = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_amvf_truth_time.root", pu=[0, 30, 60, 90, 120, 150, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/vertex_contamination.pdf",
    shell:
        """
        python {input.script} --inputs-wot {input.reco_amvf_wot} --inputs-wt {input.reco_amvf_wt} --output {output}
        """

rule plot_cpu_total_ttbar:
    input:
        script = "scripts/acts-odd-performance/plot_cpu_total_ttbar.py",
        times = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/timing.csv", pu=[0, 30, 60, 90, 120, 150, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/cpu_total_ttbar.pdf",
    shell:
        """
        python {input.script} {input.times} --output {output}
        """

rule plot_cpu_alg_ttbar:
    input:
        script = "scripts/acts-odd-performance/plot_cpu_alg_ttbar.py",
        times = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/timing.csv", pu=[0, 30, 60, 90, 120, 150, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/cpu_alg_ttbar.pdf",
    shell:
        """
        python {input.script} {input.times} --output {output}
        """
