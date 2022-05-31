#!/usr/bin/env python
#
# download_ncbi_tsa.py  created 2018-05-04
# 2022-05-31 python3 update

'''download_ncbi_tsa.py  last modified 2022-05-31
  download NCBI transcriptome assemblies and rename fasta sequences

download_ncbi_tsa.py -i arachnida_codes

    codes file contains 1 code per line, as:
GANL.gz
GANP
GFVZ.gz
# comments are allowed
...etc

    check that all automatically assigned names are correct:
head -n 1 *renamed.fasta

    translate all sequences in a single command using:
for FILE in *.renamed.fasta ; do BASE="${FILE%.renamed.fasta}"; prottrans.py -a 50 $FILE | commonseq.py -1 - -e > $BASE.prot.fasta ; done
'''

import sys
import subprocess
import time
import os
import argparse
import gzip

def make_wget_command(ncbicode, ncbiversion):
	'''make link for wget'''
	# ftp://ftp.ncbi.nlm.nih.gov/sra/wgs_aux/GF/GY/GFGY01/GFGY01.1.fsa_nt.gz
	codesplits = [ncbicode[0:2], ncbicode[2:4], ncbicode[0:4], ncbicode[0:4]]
	wgetstring = "ftp://ftp.ncbi.nlm.nih.gov/sra/wgs_aux/{1}/{2}/{3}{0}/{4}{0}.1.fsa_nt.gz".format(ncbiversion, *codesplits)
	# TODO make alternate link for newer format
	# https://sra-download.ncbi.nlm.nih.gov/traces/wgs01/wgs_aux/GH/BD/GHBD02/GHBD02.1.fsa_nt.gz
	# https://sra-download.ncbi.nlm.nih.gov/traces/wgs04/wgs_aux/GJ/HC/GJHC01/GJHC01.1.fsa_nt.gz
	return wgetstring

def run_wget(wgetstring):
	'''run wget as subprocess'''
	wget_args = ["wget", wgetstring]
	sys.stderr.write("Making system call:\n{}\n".format( " ".join(wget_args) ) )
	subprocess.call(wget_args)
	# no return

def rename_sequences(downloadfile, renamedfile):
	"""read gzipped fasta file, and rename the fasta headers"""
	seqcounter = 0
	with open(renamedfile,'w') as rf:
		for gfline in gzip.open(downloadfile,'rt'):
			if gfline[0]==">":
				headersplits = gfline.split(",",1)[0].split() # split at comma
			#	genus, species, comp = headersplits[2:5]
				newheader = ">{}_{}|{}\n".format( headersplits[2], headersplits[3], headersplits[-1] )
				newheader = newheader.replace("TRINITY_","")
				newheader = newheader.replace("Locus_","l")
				newheader = newheader.replace("Transcript_","t")
				newheader = newheader.replace(":","_")
				newheader = newheader.replace(".","_")
				newheader = newheader.replace("/","_")
				rf.write( newheader )
				seqcounter += 1
			else:
				rf.write( gfline )
	return seqcounter

def main(argv, wayout):
	if not len(argv):
		argv.append('-h')
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)
	parser.add_argument('-i','--input', help="text file of species codes, one per line (e.g. GGLO)")
	parser.add_argument('-v','--version', default="01", help="default version of txome [01], change to 02 or 03 in some cases")
	args = parser.parse_args(argv)

	species_collected = {}
	errorcount = 0
	filecollector = []
	sys.stderr.write( "# reading species IDs from {}  {}\n".format(args.input, time.asctime() ) )
	for line in open(args.input,'r'): # each line should be a 4-letter code
		line = line.strip()
		if line and line[0]!="#": # ignore empty and comment lines
			speciescode = line[0:4] # chop any endings like .gz or 01
			if speciescode in species_collected:
				sys.stderr.write( "# SKIPPING CODE {}, ALREADY IN LIST\n".format(speciescode) )
				continue

			# download file with wget
			dlfile = "{}{}.1.fsa_nt.gz".format(speciescode, args.version)
			wgetstring = make_wget_command(line[0:4], args.version)
			if not os.path.exists(dlfile):
				run_wget(wgetstring)
			else:
				sys.stderr.write( "# SKIPPING CODE {}, ALREADY DOWNLOADED\n".format(speciescode) )

			# once downloaded, rename
			if os.path.exists(dlfile) and os.path.isfile(dlfile):
				species_collected[speciescode] = True
				sys.stderr.write( "# downloaded {} , renaming sequences  {}\n".format(dlfile, time.asctime() ) )
				with gzip.open(dlfile,'rt') as gf:
					firstline = gf.readline()
				firstheader = firstline.split()
				speciesname = "{}_{}".format(*firstheader[2:4]).replace(".","") # replace . for cases of sp.
				renamedfile = "{}_{}{}.renamed.fasta".format(speciesname, speciescode, args.version)
				seqcounter = rename_sequences(dlfile, renamedfile)
				filecollector.append(renamedfile)
				sys.stderr.write( "# file {} had {} seqs\n".format(renamedfile, seqcounter) )
			else:
				errorcount += 1
	sys.stderr.write( "# found data for {} codes, could not find for {}  {}\n".format( len(species_collected), errorcount, time.asctime() ) )
	sys.stderr.write( "# renamed sequences for:\n{}\n".format( "\n".join(filecollector) ) )

if __name__ == "__main__":
	main(sys.argv[1:], sys.stdout)
