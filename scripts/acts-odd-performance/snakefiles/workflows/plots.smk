include: "../common.smk"

rule all_plots:
    input:
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_duplication.pdf", sim_label=SIM_LABELS, seeding_label=["truth-estimated", "triplet"]),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_mu.pdf", sim_label=SIM_LABELS, seeding_label=["truth-estimated", "triplet"]),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_mixed.pdf", sim_label=SIM_LABELS, seeding_label=["truth-estimated", "triplet"]),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_ttbar.pdf", sim_label=SIM_LABELS, seeding_label=["truth-estimated", "triplet"]),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_fake_ttbar.pdf", sim_label=SIM_LABELS, seeding_label=["truth-estimated", "triplet"]),

        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_duplication.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_efficiency_mu.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_efficiency_mixed.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),

        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/plot_fitting_resolution_d0_vs_eta_mu.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),
        expand("plots/acts-odd-performance/{sim_label}_{seeding_label}/plot_fitting_resolution_z0_vs_pt_mixed.pdf", sim_label=SIM_LABELS, seeding_label=SEEDING_LABELS),

rule plot_seeding_duplication:
    input:
        script = "scripts/acts-odd-performance/plot_seeding_duplication.py",
        reco = "data/acts-odd-performance/reco/1mu-pt1GeV_{sim_label}_{seeding_label}/performance_seeding.root",
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_duplication.pdf",
    shell:
        """
        scripts/activate_and_run.sh python {input.script} {input.reco} --output {output}
        """

rule plot_seeding_efficiency_mu:
    input:
        script = "scripts/acts-odd-performance/plot_seeding_efficiency_mu.py",
        reco = expand("data/acts-odd-performance/reco/1mu-pt{pt}GeV_{{sim_label}}_{{seeding_label}}/performance_seeding.root", pt=[1,10,100]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_mu.pdf",
    shell:
        """
        scripts/activate_and_run.sh python {input.script} {input.reco} --output {output}
        """

rule plot_seeding_efficiency_mixed:
    input:
        script = "scripts/acts-odd-performance/plot_seeding_efficiency_mixed.py",
        reco = expand("data/acts-odd-performance/reco/1{ptype}-pt10GeV_{{sim_label}}_{{seeding_label}}/performance_seeding.root", ptype=["mu", "pi", "e"]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_mixed.pdf",
    shell:
        """
        scripts/activate_and_run.sh python {input.script} {input.reco} --output {output}
        """

rule plot_seeding_efficiency_ttbar:
    input:
        script = "scripts/acts-odd-performance/plot_seeding_efficiency_ttbar.py",
        reco = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_seeding.root", pu=[0, 60, 120, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_efficiency_ttbar.pdf",
    shell:
        """
        scripts/activate_and_run.sh python {input.script} {input.reco} --output {output}
        """

rule plot_seeding_fake_ttbar:
    input:
        script = "scripts/acts-odd-performance/plot_seeding_fake_ttbar.py",
        reco = expand("data/acts-odd-performance/reco/ttbar-pu200_{{sim_label}}_pu{pu}-{{seeding_label}}/performance_seeding.root", pu=[0, 60, 120, 200]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/seeding_fake_ttbar.pdf",
    shell:
        """
        scripts/activate_and_run.sh python {input.script} {input.reco} --output {output}
        """

rule plot_finding_duplication:
    input:
        script = "scripts/acts-odd-performance/plot_finding_duplication.py",
        reco = "data/acts-odd-performance/reco/1mu-pt1GeV_{sim_label}_{seeding_label}/performance_finding_ckf.root",
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_duplication.pdf",
    shell:
        """
        scripts/activate_and_run.sh python {input.script} {input.reco} --output {output}
        """

rule plot_finding_efficiency_mu:
    input:
        script = "scripts/acts-odd-performance/plot_finding_efficiency_mu.py",
        reco = expand("data/acts-odd-performance/reco/1mu-pt{pt}GeV_{{sim_label}}_{{seeding_label}}/performance_finding_ckf.root", pt=[1,10,100]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_efficiency_mu.pdf",
    shell:
        """
        scripts/activate_and_run.sh python {input.script} {input.reco} --output {output}
        """

rule plot_finding_efficiency_mixed:
    input:
        script = "scripts/acts-odd-performance/plot_finding_efficiency_mixed.py",
        reco = expand("data/acts-odd-performance/reco/1{ptype}-pt10GeV_{{sim_label}}_{{seeding_label}}/performance_finding_ckf.root", ptype=["mu", "pi", "e"]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/finding_efficiency_mixed.pdf",
    shell:
        """
        scripts/activate_and_run.sh python {input.script} {input.reco} --output {output}
        """

rule plot_fitting_resolution_d0_vs_eta_mu:
    input:
        script = "scripts/acts-odd-performance/plot_fitting_resolution_d0_vs_eta_mu.py",
        reco = expand("data/acts-odd-performance/reco/1mu-pt{pt}GeV_{{sim_label}}_{{seeding_label}}/performance_fitting_ckf.root", pt=[1,10,100]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/plot_fitting_resolution_d0_vs_eta_mu.pdf",
    shell:
        """
        scripts/activate_and_run.sh python {input.script} {input.reco} --output {output}
        """

rule plot_fitting_resolution_z0_vs_pt_mixed:
    input:
        script = "scripts/acts-odd-performance/plot_fitting_resolution_z0_vs_pt_mixed.py",
        reco = expand("data/acts-odd-performance/reco/1{ptype}-pt1-100GeV_{{sim_label}}_{{seeding_label}}/performance_fitting_ckf.root", ptype=["mu", "pi", "e"]),
    output:
        "plots/acts-odd-performance/{sim_label}_{seeding_label}/plot_fitting_resolution_z0_vs_pt_mixed.pdf",
    shell:
        """
        scripts/activate_and_run.sh python {input.script} {input.reco} --output {output}
        """
