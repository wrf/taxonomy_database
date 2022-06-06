#!/usr/bin/env python
#
# parse_ncbi_taxonomy.py  created by WRF 2018-04-05

'''parse_ncbi_taxonomy.py  last modified 2022-06-06

parse_ncbi_taxonomy.py -n names.dmp -o nodes.dmp -i species_list.txt

    NCBI Taxonomy files can be downloaded at the FTP:
    ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/

    if using the short output format of metagenomes, omit --samples
parse_ncbi_taxonomy.py -i ncbi_ids.txt -n names.dmp -o nodes.dmp --metagenomes-only --numbers --header > metagenomes.tab

    if using the extended output (9-column), include --samples
parse_ncbi_taxonomy.py -i sample_ext.tab -n names.dmp -o nodes.dmp --metagenomes-only --numbers --samples > metagenomes_ext.tab

    if using the .csv file directly from NCBI WGS
    https://www.ncbi.nlm.nih.gov/Traces/wgs/?page=1&view=tsa
    use the --csv tag as:

parse_ncbi_taxonomy.py -n names.dmp -o nodes.dmp --csv -i wgs_selector.csv
'''

import csv
import sys
import os
import time
import gzip
import argparse

#nodes.dmp
#---------
#This file represents taxonomy nodes. The description for each node includes 
#the following fields:
#	tax_id					-- node id in GenBank taxonomy database
# 	parent tax_id				-- parent node id in GenBank taxonomy database
# 	rank					-- rank of this node (superkingdom, kingdom, ...) 
# 	embl code				-- locus-name prefix; not unique
# 	division id				-- see division.dmp file
# 	inherited div flag  (1 or 0)		-- 1 if node inherits division from parent
# 	genetic code id				-- see gencode.dmp file
# 	inherited GC  flag  (1 or 0)		-- 1 if node inherits genetic code from parent
# 	mitochondrial genetic code id		-- see gencode.dmp file
# 	inherited MGC flag  (1 or 0)		-- 1 if node inherits mitochondrial gencode from parent
# 	GenBank hidden flag (1 or 0)            -- 1 if name is suppressed in GenBank entry lineage
# 	hidden subtree root flag (1 or 0)       -- 1 if this subtree has no sequence data yet
# 	comments				-- free-text comments and citations

#names.dmp
#---------
#Taxonomy names file has these fields:
#	tax_id					-- the id of node associated with this name
#	name_txt				-- name itself
#	unique name				-- the unique variant of this name if name not unique
#	name class				-- (synonym, common name, ...)

def names_to_nodes(namesfile, metagenomes_only=False):
	'''read names.dmp and return a dict where name is key and value is the node number'''
	name_to_node = {}
	node_to_name = {}
	sys.stderr.write("# reading species names from {}  {}\n".format(namesfile, time.asctime() ) )
	for line in open(namesfile,'r'):
		line = line.strip()
		if line:
			lsplits = [s.strip() for s in line.split("|")]
			nameclass = lsplits[3]
			if nameclass=="scientific name":
				node = lsplits[0]
				species = lsplits[1]
				# if in metagenome mode, skip species names that do not have "metagenome"
				if metagenomes_only and species.find("metagenome") == -1:
					continue
				name_to_node[species] = node
				node_to_name[node] = species
	sys.stderr.write("# counted {} scientific names from {}  {}\n".format( len(name_to_node), namesfile, time.asctime() ) )
	return name_to_node, node_to_name

def nodes_to_parents(nodesfilelist):
	'''read nodes.dmp and return two dicts where keys are node numbers'''
	node_to_rank = {}
	node_to_parent = {}
	for nodesfile in nodesfilelist:
		sys.stderr.write("# reading nodes from {}  {}\n".format(nodesfile, time.asctime() ) )
		for line in open(nodesfile,'r'):
			line = line.strip()
			if line:
				lsplits = [s.strip() for s in line.split("|")]
				node = lsplits[0]
				parent = lsplits[1]
				rank = lsplits[2]
				node_to_rank[node] = rank
				node_to_parent[node] = parent
	sys.stderr.write("# counted {} nodes from {}  {}\n".format( len(node_to_rank), nodesfile, time.asctime() ) )
	return node_to_rank, node_to_parent

def get_parent_tree(nodenumber, noderanks, nodeparents):
	'''given the node number, and the two dictionaries, traverse the tree until you end with kingdom and return a list of the numbers of the kingdom, phylum and class'''
	parent = "0"
	kingdom = None
	phylum = None
	pclass = None
	while nodenumber != "1":
		try:
			if noderanks[nodenumber] =="kingdom":
				kingdom = nodenumber
			elif noderanks[nodenumber] =="phylum":
				phylum = nodenumber
			elif noderanks[nodenumber] =="class":
				pclass = nodenumber
			if nodenumber=="2" or nodenumber=="2157": # for bacteria and archaea
				kingdom = nodenumber
		except KeyError:
			sys.stderr.write("WARNING: NODE {} MISSING, CHECK delnodes.dmp\n".format(nodenumber) )
			return ["Deleted","Deleted","Deleted"]
		parent = nodeparents[nodenumber]
		nodenumber = parent
	return [kingdom, phylum, pclass]

def clean_name(seqname):
	'''read string, return the same string removing most symbols that disrupt downstream analysis'''
	symbollist = "#[]()+=&'\""
	for s in symbollist:
		seqname = seqname.replace(s,"")
	return seqname

def main(argv, wayout):
	if not len(argv):
		argv.append('-h')
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)
	parser.add_argument('-i','--input', help="text file of species names, can be .gz")
	parser.add_argument('-n','--names', help="NCBI taxonomy names.dmp")
	parser.add_argument('-o','--nodes', nargs="*", help="NCBI taxonomy nodes.dmp, and possibly merged.dmp")
	parser.add_argument('--csv', action="store_true", help="read directly from NCBI WGS csv file")
	parser.add_argument('--header', action="store_true", help="write header line for output")
	parser.add_argument('--metagenomes-only', action="store_true", help="only count metagenomic samples")
	parser.add_argument('--numbers', action="store_true", help="input lines are NCBI ID numbers, not names")
	parser.add_argument('--samples', action="store_true", help="read directly from parsed samples file")
	parser.add_argument('--unique', action="store_true", help="only count first occurrence of a speices")
	args = parser.parse_args(argv)

	name_to_node, node_to_name = names_to_nodes(args.names, args.metagenomes_only)
	node_to_rank, node_to_parent = nodes_to_parents(args.nodes)

	# metagenome mode overrides making a header
	if args.header and not args.metagenomes_only:
		sys.stdout.write("species\tkingdom\tphylum\tclass\n")

	node_tracker = {} # keys are node IDs, values are counts

	nullentries = 0 # information cannot be found
	skippedentries = 0 # skipped for --unique or --metagenomes-only
	foundentries = 0
	writecount = 0

	inputfilename = args.input
	if inputfilename.rsplit('.',1)[-1]=="gz": # autodetect gzip format
		opentype = gzip.open
		sys.stderr.write("# reading species IDs from {} as gzipped  {}\n".format(inputfilename, time.asctime() ) )
	else: # otherwise assume normal open for fasta format
		opentype = open
		sys.stderr.write("# reading species IDs from {}  {}\n".format(inputfilename, time.asctime() ) )
	# meaning parse NCBI WGS csv file
	if args.csv:
		with opentype(inputfilename,'rt') as csvfile:
			ncbicsv = csv.reader(csvfile)
			for lsplits in ncbicsv:
				speciesname = lsplits[4]
				node_id = name_to_node.get(speciesname,None)
				if speciesname is not None: # remove any # that would disrupt downstream analyses
					speciesname = clean_name(speciesname)
				node_tracker[node_id] = node_tracker.get(node_id, 0) + 1
				if node_id is not None:
					foundentries += 1
					finalnodes = get_parent_tree(node_id, node_to_rank, node_to_parent)
					finalnodes = [node_to_name.get(n,"None") for n in finalnodes]
					outputlist = lsplits[0:5] + finalnodes + lsplits[6:]
					# check for deleted nodes, add to null entries
					if finalnodes[0]=="Deleted":
						nullentries += 1
				elif speciesname == "organism_an":
					outputlist = lsplits[0:5] + ["kingdom", "phylum", "class"] + lsplits[6:]
				else:
					nullentries += 1
					outputlist = lsplits[0:5] + ["None", "None", "None"] + lsplits[6:]
				outputstring = "{}\n".format( clean_name("\t".join(outputlist)) )
				writecount += 1
				sys.stdout.write( outputstring )
	# parse tabular output
	else:
		for line in opentype(inputfilename,'rt'):
			line = line.strip()
			if line:
				# if reading directly from 4-column samples file, extract sample ID
				if args.samples:
					lsplits = line.split("\t")
					if len(lsplits) < 4: # columns missing somehow, skip
						sys.stderr.write("# ERROR: MISSING COLUMNS IN:\n" + line + os.linesep)
						continue
					if args.numbers:
						taxid = lsplits[2]
						if len(lsplits) > 4: # likely tabs in sample alias
							taxid = lsplits[3]
					else: # use species name
						taxid = lsplits[3]
				else: # otherwise each line is a sample name or number
					taxid = line

				# input lines are NCBI numbers, meaning get species name from that
				if args.numbers:
					speciesname = node_to_name.get(taxid,None)
					node_id = taxid
				else: # meaning input lines are species names, like Danio rerio
					speciesname = taxid
					node_id = name_to_node.get(speciesname,None)
				if speciesname is not None: # remove any # that would disrupt downstream analyses
					speciesname = clean_name(speciesname)
				# add one for each node
				node_tracker[node_id] = node_tracker.get(node_id, 0) + 1
				# in unique mode, if node has been seen before then skip it
				if args.unique and node_tracker.get(node_id,0) > 1:
					skippedentries += 1
					continue

				if node_id is not None:
					foundentries += 1
					if args.metagenomes_only:
						if speciesname is None:
							skippedentries += 1
							continue
						cleaned_line = clean_name(line)
						# column is redundant with ncbi_category, remove "metagenome" for ease of later indexing
						metagenome_category = speciesname.replace(" metagenome","").strip()
						outputstring = "{}\t{}\n".format( cleaned_line, metagenome_category )
					else: # normal mode
						finalnodes = get_parent_tree(node_id, node_to_rank, node_to_parent)
						outputstring = "{}\t{}\t{}\t{}\n".format( speciesname, node_to_name.get(finalnodes[0],"None"), node_to_name.get(finalnodes[1],"None"), node_to_name.get(finalnodes[2],"None") )

						# check for deleted nodes, add to null entries
						if finalnodes[0]=="Deleted":
							nullentries += 1
				else:
					nullentries += 1
					outputstring = "{}\tNone\tNone\tNone\n".format( speciesname )
				writecount += 1
				sys.stdout.write( outputstring )
	sys.stderr.write("# found tree for {} nodes, could not find for {}  {}\n".format( foundentries, nullentries, time.asctime() ) )
	if skippedentries:
		sys.stderr.write("# wrote {} entries, skipped {} entries\n".format( writecount, skippedentries ) )

if __name__ == "__main__":
	main(sys.argv[1:], sys.stdout)
