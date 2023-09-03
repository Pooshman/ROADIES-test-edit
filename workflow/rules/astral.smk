rule astral:
	input:
		config["OUT_DIR"]+"/genetrees/gene_tree_merged.nwk"
	output:
		config["OUT_DIR"]+"/roadies.nwk"
	params:
		genes = config["OUT_DIR"]+"/genes",
		stats = config["OUT_DIR"]+"/roadies_stats.nwk"
	benchmark:
		config["OUT_DIR"]+"/benchmarks/astral.txt"
	shell:
		'''
		ASTER-Linux/bin/astral-pro -i {input} -o {output} -a {params.genes}/mapping.txt
		ASTER-Linux/bin/astral-pro -u 3 -i {input} -o {params.stats} -a {params.genes}/mapping.txt
		'''
