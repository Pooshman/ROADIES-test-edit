num_species = len(os.listdir(config["GENOMES"]))
if config["TO_ALIGN"] != num_species:
	g = config["OUT_DIR"]+"/samples/{sample}_genes.fa"
else:
	g = config["OUT_DIR"]+"/samples/out.fa"
subset_file = config["SUBSET"]
subset_dir = config["SUBSET_DIR"]
#if subset file does not exist before run
print("subset",config["SUBSET"])
if config["SUBSET"] == None or config["SUBSET"] == "0" or config["SUBSET"] == 0:
	subset_file = "subsets/subsets.txt"
	subset_dir = "subsets"
rule lastz2fasta:
	input:
		expand(config["OUT_DIR"]+"/alignments/{sample}.maf",sample=SAMPLES)   
	output:
		expand(config["OUT_DIR"]+"/genes/gene_{id}.fa",id=IDS),
		report(config["OUT_DIR"]+"/plots/num_genes.png",caption="../report/num_genes_p.rst",category="Genes Report"),
		report(config["OUT_DIR"]+"/statistics/homologues.csv",caption="../report/homologues.rst",category="Genes Report"),
		report(config["OUT_DIR"]+"/statistics/num_genes.csv",caption="../report/num_genes_t.rst",category="Genes Report"),
		report(config["OUT_DIR"]+"/statistics/num_gt.txt",caption="../report/num_gt.rst",category="Genes Report"),
		report(config["OUT_DIR"]+"/plots/gene_dup.png",caption="../report/gene_dup.rst",category="Genes Report"),
		report(config["OUT_DIR"]+"/plots/homologues.png",caption="../report/homologues_p.rst",category="Genes Report")


	params:
		k = num,
		out = config["OUT_DIR"]+"/genes",
		p = config["OUT_DIR"]+"/alignments",
		m = config["MIN_ALIGN"],
		plotdir = config["OUT_DIR"]+"/plots",
		statdir = config["OUT_DIR"]+"/statistics",
		d = config["MAX_DUP"]
	conda:
		"../envs/plots.yaml"
	shell:
		"python workflow/scripts/lastz2fasta.py -k {params.k} --path {params.p} --outdir {params.out} -m {params.m} --plotdir {params.plotdir} --statdir {params.statdir} -d {params.d}" 
		
		
rule lastz:
	input:
		genes = g,
		genome = config["GENOMES"]+"/{sample}.fa"
	output:
		config["OUT_DIR"]+"/alignments/{sample}.maf"
	benchmark:
		config["OUT_DIR"]+"/benchmarks/{sample}.lastz.txt"
	conda:
		"../envs/lastz.yaml"
	params:
		species = "{sample}",
		identity = config['IDENTITY'],
		coverage = config['COVERAGE'],
		continuity = config['CONTINUITY'],
		align_dir = config['OUT_DIR']+ "/alignments",
		max_dup = 2*int(config['MAX_DUP']),
		steps = config["STEPS"],
		subset = lambda wildcards: is_mapped(wildcards.sample),
		sf = subset_file,
		map_e = lambda wildcards: does_map_exist(),
		subset_dir = subset_dir
	shell:
		'''
		#if no preexisting map
		if [[ {params.map_e} -eq 0  ]]; then
			mkdir -p {params.subset_dir}
			echo "No mapping computing size for {input.genome}"
			#compute genome size
			size=$(./faSize {input.genome} | awk '{{if (NR==1) {{print $1}}}}')
			#if over size limit
			if [[ $size -gt 2000000000 ]]; then 
				echo "{input.genome} has size ${{size}} which is over the size limit subsetting"
    			echo -n "" > {output}
    			prefix=$(basename {input.genome} .fa);
				echo "splitting fasta to {params.subset_dir}/${{prefix}}_"
				faSplit about {input.genome} 1000000000 {params.subset_dir}/${{prefix}}_ 
				for f in $(ls {params.subset_dir}/${{prefix}}_*.fa); do
					echo "aligning ${{f}}"
					echo "${{f}} {input.genome}"
					echo "${{f}} {input.genome}" >> {params.sf}
					lastz_32 ${{f}}[multiple] {input.genes} --coverage={params.coverage} --continuity={params.continuity} --filter=identity:{params.identity} --format=maf --output=${{f}}_out.maf --ambiguous=iupac --step={params.steps} --notransition --queryhspbest={params.max_dup}
				done
				for f in $(ls {params.subset_dir}/${{prefix}}_*_out.maf); do
					cat ${{f}} >> {output}
				done
			else
				echo "aligning {input.genome} with size ${{size}} normally"
				lastz_32 {input.genome}[multiple] {input.genes} --coverage={params.coverage} --continuity={params.continuity} --filter=identity:{params.identity} --format=maf --output={output} --ambiguous=iupac --step={params.steps} --notransition --queryhspbest={params.max_dup}
			fi																																				
		else
			echo "{params.subset} subsets"
			echo {params.subset_dir}
			if [[ {params.subset} -eq 0 ]]; then
				echo "mapping is 0 aligning {input.genome} normally"
				lastz_32 {input.genome}[multiple] {input.genes} --coverage={params.coverage} --continuity={params.continuity} --filter=identity:{params.identity} --format=maf --output={output} --ambiguous=iupac --step={params.steps} --notransition --queryhspbest={params.max_dup}
			else
				echo "using subset for {input.genome}"
				prefix=$(basename {input.genome} .fa);
				dir="$(dirname {input.genome})" 
				for f in $(ls {params.subset_dir}/${{prefix}}_*.fa); do
					echo "aligning ${{f}}"
					lastz_32 ${{f}}[multiple] {input.genes} --coverage={params.coverage} --continuity={params.continuity} --filter=identity:{params.identity} --format=maf --output=${{f}}_out.maf --ambiguous=iupac --step={params.steps} --notransition --queryhspbest={params.max_dup}
				done
				for f in $(ls {params.subset_dir}/${{prefix}}_*_out.maf); do
					cat ${{f}} >> {output}
				done      
			fi
		fi
		'''


rule pasta:
	input:
		config["OUT_DIR"]+"/genes/gene_{id}.fa"
	output:
		config["OUT_DIR"]+"/genes/gene_{id}.dnd"
	params:
		m=config["MIN_ALIGN"],
		n=config["OUT_DIR"],
		max_len=int(1.5*config["LENGTH"]),
		prefix = "gene_{id}",
		suffix = "fa.aln",
        gene_dir = config["OUT_DIR"]+"/genes"
	benchmark:
		config["OUT_DIR"]+"/benchmarks/{id}.pasta.txt"
	threads: 8
	conda: 
		"../envs/msa.yaml"
	shell:
		'''
		''if [[ `grep -n '>' {input} | wc -l` -gt {params.m} ]] || [[ `awk 'BEGIN{{l=0;n=0;st=0}}{{if (substr($0,1,1) == ">") {{st=1}} else {{st=2}}; if(st==1) {{n+=1}} else if(st==2) {{l+=length($0)}}}} END{{if (n>0) {{print int((l+n-1)/n)}} else {{print 0}} }}' {input}` -gt {params.max_len} ]]
		then
			mashtree --numcpus 8 {params.gene_dir}/gene_{id}.temp.* [*.fasta] > {output}

		fi
		touch {output}''
