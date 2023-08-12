num = len(SAMPLES)*config["GENE_MULT"]
IDS = list(range(1,num+1))

rule mergeTrees:
	input:
		expand(config["OUT_DIR"]+"/genes/gene_{id}.dnd",id=IDS)
	output:
		config["OUT_DIR"]+"/genetrees/gene_tree_merged.nwk"
	params:
		msa_dir = config["OUT_DIR"]+"/genes",
	conda: 
		"../envs/tree.yaml"
	shell:
		'''
		cat {params.msa_dir}/*.dnd > {output}
		'''

