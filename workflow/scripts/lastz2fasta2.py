# lastz2fasta.py takes a directory of .maf alignments for each species, parses, and outputs the alignmnents into k gene fastas
# filtering and stat-gathering steps are concurrently done that are discussed further in README.md
# REQUIREMENTS: Biopython, seaborn, matplotlib
# USAGE: `python workflow/scripts/lastz2fasta.py {args}`
import re
import os, glob
import sys
import argparse
from Bio import SeqIO
from operator import itemgetter
import seaborn as sns
import matplotlib.pyplot as plt
from collections import OrderedDict
from Bio.Seq import Seq

# get arguments
parser = argparse.ArgumentParser(
    description="lastz2fasta.py takes a directory of .maf alignments for each species, parses, and outputs the alignmnents into k gene fastas"
)
parser.add_argument("-k", type=int, default=200, help="Number of genes")
parser.add_argument("--path", default="results/alignments")
parser.add_argument("--outdir", default="results/genes")
parser.add_argument("-m", type=int, default=4)
parser.add_argument("--plotdir", default="results/plots")
parser.add_argument("--statdir", default="results/statistics")
parser.add_argument("-d", type=int, default=100)
args = parser.parse_args()
path = args.path
outdir = args.outdir
plotdir = args.plotdir
statdir = args.statdir
m = args.m
k = args.k
d = args.d
num_genes = {}
num_homologues = {}
gene_count = {}
for i in range(1,k+1):
    gene_count[str(i)] = 0
for i in range(1, k + 1):
    os.system("touch {0}/gene_{1}.fa".format(outdir, i))
# open all lastz alignment outputs
for filename in glob.glob(os.path.join(path, "*.maf")):
    with open(os.path.join(os.getcwd(), filename), "r") as f:
        # get species name
        s = filename.split("/")
        name = s[len(s) - 1]
        species = name.replace(".maf", "")
        lines = f.readlines()
        # make dict of genes for each species
        genes = {}
        # go through every 4th line due to maf format
        for i in range(15, len(lines)):
            if '#' in lines[i]:
                continue
            elif 'gene' in lines[i]:
                l = i-1
                # get gene id
                #print(lines[l])
                gene_line = lines[l + 1].split()
                #print(gene_line)
                gene = gene_line[1]
                gene_s = gene.split("_")
                gene_id = str(gene_s[1])
                # get score of that alignment
                score_line = lines[l - 1].split()
                score_expr = score_line[1].split("=")
                score = int(score_expr[1])
                # get position in species fasta
                seq_line = lines[l].split()
                position = int(seq_line[2])
                # add to dict of genes
                if gene_id not in genes:
                    print(gene_id,"not in ")
                    genes[gene_id] = [(score, l, position)]
                else:
                    genes[gene_id].append((score, l, position))
        #print(genes)
        # get number of genes for that species
        num_genes[species] = len(genes)
        # get number of homologues for that gene (#species)
        for gene in genes:
            
            if gene in num_homologues:
                num_homologues[gene] += 1
            else:
                num_homologues[gene] = 1
            # make list of genes
            gene_list = genes[gene]
            # skip if no homologue
            # sort homologues by score
            gene_list.sort(reverse=True)
            # initialize with highest score
            max_scores = [0]
            positions = [gene_list[0][2]]
            idx = 1
            # go through gene list
            while idx < len(gene_list):
                # get position of that alignment
                pos = gene_list[idx][2]
                # if it's within 2000 bp of another higher scoring alignment skip that alignment
                tooClose = False
                for p in positions:
                    if abs(p - pos) < (2 * k):
                        tooClose = True
                        break
                if not tooClose:
                    positions.append(pos)
                    max_scores.append(idx)
                    tooClose = False
                idx = idx + 1
            # limits the number of alignments
            n = len(max_scores)
            if n > d:
                n = d
            # for highest scoring alignments
            for i in range(n):
                # get line number
                l = gene_list[i][1]
                # get sequence
                orient_line = lines[l + 1].split()
                orientation = orient_line[4]
                seq = ""
                seq_line = lines[l].split()
                seq = seq_line[len(seq_line) - 1]
                seq = seq.replace("-", "")
                genome_pos = str(i)
                if orientation == "-":
                    seq = str(Seq(seq).reverse_complement())
                index = species + "_" + str(i)
                # output to gene fasta
                allowed = ["a", "t", "c", "g", "A", "T", "C", "G"]
                good_seq = True
                for j in range(len(seq)):
                    if seq[j] not in allowed:
                        good_seq = False
                        break
                if not good_seq:
                    continue
                print(gene_count)
                print("gene",gene,gene_count[gene])
                with open(outdir + "/gene_" + gene +'.temp.'+str(gene_count[gene])+".fasta", "w") as w:
                    w.write(">" + index + "\n")
                    w.write(seq + "\n")
                with open(outdir + "/gene_" + gene +".fa", "a") as w:
                    w.write(">" + index + "\n")
                    w.write(seq + "\n")
                # add to mapping file
                nm = "gene_{0}.temp.{1}".format(gene,gene_count[gene])
                with open(outdir + "/mapping.txt", "a") as w2:
                    w2.write(nm+ " " + species + "\n")
                gene_count[gene] += 1
                w2.close()
# turn number of genes dict into list
x = list(num_genes.keys())
y = list(num_genes.values())
# make csv
with open(statdir + "/num_genes.csv", "w") as f:
    for i in range(len(x)):
        f.write(x[i] + "," + str(y[i]) + "\n")
# make barplot of number of genes for each species
ax = sns.barplot(x=x, y=y)
ax.set_xticklabels(ax.get_xticklabels(), rotation=60, ha="right")
ax.set_title("Number of Genes Aligned To Each Genome")
plt.tight_layout()
fig = ax.get_figure()
fig.savefig(plotdir + "/num_genes.png")
# make ordered dict of number of homologues (ordered by gene #)
od = OrderedDict(sorted(num_homologues.items()))
# write to csv for homologues
with open(statdir + "/homologues.csv", "w") as f:
    for key, val in od.items():
        f.write("gene_" + str(key) + "," + str(val) + "\n")
# only need values (# homologues)
x2 = od.values()
# make histogram
ax2 = sns.displot(x=x2, kde=True)
# fig2 = ax2.get_figure()
ax2.savefig(plotdir + "/homologues.png")
count = 0
# array for counting duplicity
gene_dup = []
# iterate through gene fastas
for filename in glob.glob(os.path.join(outdir, "*.fa")):
    if "temp" in filename:
        continue
    # get gene#
    fs = filename.split("/")
    fs2 = fs[len(fs) - 1]
    fs2 = fs2.replace("gene_", "")
    fs2 = fs2.replace(".fa", "")
    # get the sequences
    if os.stat(filename).st_size == 0:
        continue
    records = list(SeqIO.parse(filename, "fasta"))
    # get the duplicity by diving #sequences by # species
    avg = len(records) / int(num_homologues[fs2])
    gene_dup.append((int(fs2), avg))
    found = []
    # iterate through seqs
    for record in records:
        # get species name
        n = record.name
        ns = n.split("_")
        name = ""
        for i in range(len(ns) - 1):
            name += ns[i]
        if name not in found:
            found.append(name)
    # if number of species is > threhold count it
    if len(found) >= m:
       # print(len(found), found)
        count += 1
    else:
        with open(filename, "w") as w:
            w.write("")
sorted(gene_dup)
# output duplicity as csv]
with open(statdir + "/gene_dup.csv", "w") as f:
    for i in range(len(gene_dup)):
        f.write(str(gene_dup[i][0]) + "," + str(gene_dup[i][1]) + "\n")
x3 = []
for i in range(len(gene_dup)):
    x3.append(gene_dup[i][1])
# make histogram
ax3 = sns.displot(x=x3, kde=True)
# fig2 = ax2.get_figure()
ax3.savefig(plotdir + "/gene_dup.png")
# print("Number of gene trees: ",count)
with open(statdir + "/num_gt.txt", "w") as f:
    f.write("Number of gene trees: " + str(count) + "\n")
    # if len(records)< m:
    #   print(filename)
    #  os.remove(filename)