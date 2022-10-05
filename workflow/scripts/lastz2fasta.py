#each gene plot 
import re
import os, glob
import sys
import argparse
from Bio import SeqIO
from operator import itemgetter
import seaborn as sns
import matplotlib.pyplot as plt
from collections import OrderedDict
parser = argparse.ArgumentParser(description='get gene fasta')
parser.add_argument('-k',type=int,default=400)
parser.add_argument('--path')
parser.add_argument('--outdir')
parser.add_argument('-m',type=int,default=4)
parser.add_argument('-d',type=int,default=5)
args = parser.parse_args()
path = args.path
outdir = args.outdir
m = args.m
k = args.k
d= args.d
num_genes = {}
num_homologues = {}
for filename in glob.glob(os.path.join(path,'*.maf')):
    with open(os.path.join(os.getcwd(),filename),'r') as f:
        s = filename.split('/')
        name = s[len(s)-1]
        species = name.replace(".maf","")
        lines = f.readlines()
        found = []
        genes = {}
        for l in range(15,len(lines)):
            if (l-15)%4 == 0:
                gene_line = lines[l+1].split()
                gene = gene_line[1]
                gene_s = gene.split('_')
                gene_id = gene_s[1]
                score_line = lines[l-1].split()
                score_expr = score_line[1].split('=')
                score = int(score_expr[1])
                seq_line = lines[l].split()
                position = int(seq_line[2])
                if gene_id not in genes:
                    genes[gene_id] = [(score,l,position)]
                else:
                    genes[gene_id].append((score,l,position))
        num_genes[species] = len(genes)
        for gene in genes:
            if gene in num_homologues:
                num_homologues[gene] += 1
            else:
                num_homologues[gene] = 1
            print(gene,num_homologues[gene])
            gene_list = genes[gene]
            #skip if no homologue
            #sort homologues by score
            gene_list.sort(reverse=True)
            max_scores = [0]
            positions = [gene_list[0][2]]
            idx = 1
            while(idx < len(gene_list) and len(max_scores)<d):
                pos = gene_list[idx][2]
                tooClose = False
                for p in positions:
                    if abs(p-pos)<(2*1000):
                        tooClose = True
                        break
                if not tooClose:
                    positions.append(pos)
                    max_scores.append(idx)
                    tooClose = False
                idx = idx+1
            for i in range(len(max_scores)):
                l = gene_list[i][1]
                seq_line = lines[l].split()
                seq = seq_line[len(seq_line)-1]
                seq = seq.replace('-','')
                index = species+'_'+seq_line[2]
                #output to gene fasta
                with open(outdir+'/gene_'+gene+'.fa','a') as w:
                        w.write('>'+index+'\n')
                        w.write(seq+'\n')
                w.close()
                #add to mapping file 
                with open(outdir+"/mapping.txt",'a') as w2:
                    w2.write(index+' ' +species+'\n')
                w2.close()
                #print(max_scores)
                
                #print(species,gene,counts[gene])
#print(num_genes)
#print(num_homologues)
x = list(num_genes.keys())
y = list(num_genes.values())
with open('results/statistics/num_genes.csv','w') as f:
    for i in range(len(x)):
        f.write(x[i]+','+str(y[i])+'\n')
ax = sns.barplot(x=x,y=y)
ax.set_xticklabels(ax.get_xticklabels(),rotation=40,ha='right')
ax.set_title('Number of Genes Aligned To Each Genome')
plt.tight_layout()
fig = ax.get_figure()
fig.savefig("results/plots/num_genes.png")
od = OrderedDict(sorted(num_homologues.items()))
with open('results/statistics/homologues.csv','w') as f:
    for key, val in od.items():
        f.write('gene_'+str(key)+','+str(val)+'\n')
x2 = od.values()
ax2 = sns.displot(x=x2,kde=True)
#fig2 = ax2.get_figure()
ax2.savefig("results/plots/homologues.png")
count = 0
gene_dup = []
for filename in glob.glob(os.path.join(outdir,'*.fa')):
    #print(filename)
    fs = filename.split('/')
    fs2 = fs[len(fs)-1]
    fs2 = fs2.replace('gene_','')
    fs2 = fs2.replace('.fa','')
    #print(fs2)
    records = list(SeqIO.parse(filename,"fasta"))
    #print(fs2,len(records),num_homologues[fs2])
    avg = len(records)/num_homologues[fs2]
    #print(avg)
    gene_dup.append((int(fs2),avg))
    found = []
    for record in records:
        n = record.name
        ns = n.split('_')
        name = ns[0]+ns[1]
        if name not in found:
            found.append(name)
    if len(found)>m:
        #print(len(found),found)
        count += 1
sorted(gene_dup)
#print(gene_dup)
with open('results/statistics/gene_dup.csv','w') as f:
    for i in range(len(gene_dup)):
        f.write(str(gene_dup[i][0])+','+str(gene_dup[i][1])+'\n')
x3 = []
for i in range(len(gene_dup)):
    x3.append(gene_dup[i][1])
ax3 = sns.displot(x=x3,kde=True)
#fig2 = ax2.get_figure()
ax3.savefig("results/plots/gene_dup.png")
#print("Number of gene trees: ",count)
with open("results/statistics/num_gt.txt",'w') as f:
    f.write("Number of gene trees: "+str(count)+'\n')
    #if len(records)< m:
     #   print(filename)
      #  os.remove(filename)
