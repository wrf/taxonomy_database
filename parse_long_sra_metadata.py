#!/usr/bin/env python
#
# parse_sra_metadata.py v1 created by WRF 2018-04-24

'''parse_long_sra_metadata.py v1.1 last modified 2021-04-23
    parses the SRA metadata tar.gz file, makes a 12-column text table

parse_long_sra_metadata.py NCBI_SRA_Metadata_Full_20191130.tar.gz >  NCBI_SRA_Metadata_Full_20191130.sample_ext.tab

    NOTE: parsing metadata can be slow due to the tar.gz size
      above run took appx 6 days

    download SRA metadata from:
ftp://ftp.ncbi.nlm.nih.gov/sra/reports/Metadata/

    to generally view the .tar.gz
tar -tzf NCBI_SRA_Metadata_Full_20180402.tar.gz | more

    some folders do not have sample information
    this will print up to 100 warnings
    to inspect individual elements in the .tar.gz, use -zxf
tar -zxf NCBI_SRA_Metadata_Full_20190914.tar.gz SRA406976
tar -zxf NCBI_SRA_Metadata_Full_20210104.tar.gz ERS861219
'''

import sys
import time
import tarfile
import unicodedata
from collections import Counter
import xml.etree.ElementTree as ET

# for interactive Python debug:
debug='''
import tarfile
import xml.etree.ElementTree as ET
srafile = "NCBI_SRA_Metadata_Full_20210104.tar.gz"
metadata = tarfile.open(name=srafile, mode="r:gz")
member = metadata.next()
member.isdir()
samplename = "{0}/{0}.sample.xml".format(member.name)
sam_fex = metadata.extractfile(samplename)
xmltree = ET.fromstring(sam_fex.read())
xl = xmltree.getchildren()
sample = xl[0]
sl = sample.getchildren()
'''

debug2='''
import xml.etree.ElementTree as ET
member = "SRA694253"
samplename = "{0}/{0}.sample.xml".format(member)
xmltree = ET.fromstring(open(samplename,'r').read())
xl = xmltree.getchildren()
sample = xl[0]
sl = sample.getchildren()
sl[4].getchildren()[0].getchildren()[0].text
sl[4].getchildren()[0].getchildren()[1].text
'''

if len(sys.argv) < 2:
	sys.stderr.write(__doc__)
else:
	starttime = time.time()

	membercounter = 0
	foldercounter = 0
	nonfolders = 0 # probably other files like run.xml submission.xml
	lastnonfolder = ""

	samplecounter = 0
	exptcounter = 0
	noexptcounter = 0
	nosamplecounter = 0

	WARNMAX = 100

	expt_attribute_counter = Counter()
	sample_attribute_counter = Counter()

	sys.stderr.write("# parsing metadata from {}  {}\n".format( sys.argv[1], time.asctime() ) )
	metadata = tarfile.open(name=sys.argv[1], mode="r:gz")
	for member in metadata.getmembers():
		membercounter += 1
		if member.isdir():
			foldercounter += 1
			if not foldercounter % 100000:
				sys.stderr.write("# {} folders  {}\n".format(foldercounter, time.asctime() ) )

			# extract experiment information, to allow later sorting of genomic, RNAseq, amplicon, etc
			# library strategy possibilities include:
			# WGA WGS WXS RNA-Seq miRNA-Seq WCS CLONE POOLCLONE AMPLICON CLONEEND
			# whole genome assembly; whole genome sequencing; whole exome sequencing; RNA-Seq; micro RNA sequencing
			# whole chromosome random sequencing;
			experimentname = "{0}/{0}.experiment.xml".format(member.name)
			try:
				exp_fex = metadata.extractfile(experimentname)
			except KeyError:
				noexptcounter += 1
				exp_fex = None
				# do not skip entry, check sample first
			if exp_fex is not None:
				library_attrs = {} # reset each folder
				exp_xmltree = ET.fromstring(exp_fex.read())
				expxl = exp_xmltree.getchildren()
				for exptdata in expxl:
					exptcounter += 1
					el = exptdata.getchildren()
					for einfo in el: # iterate through IDENTIFIERS TITLE STUDY_REF DESIGN PLATFORM PROCESSING
						if einfo.tag=="DESIGN":
							for subattr in einfo.getchildren():
								if subattr.tag=="LIBRARY_DESCRIPTOR":
									for subsubattr in subattr.getchildren(): # contains LIBRARY_LAYOUT LIBRARY_NAME LIBRARY_STRATEGY LIBRARY_SOURCE LIBRARY_SELECTION}
										subsubattr_text = subsubattr.text
										if subsubattr_text is not None:
											library_attrs[subsubattr.tag] = subsubattr.text.strip()
				expt_attribute_counter.update( library_attrs.keys() )
			# library source
			# GENOMIC TRANSCRIPTOMIC METAGENOMIC METATRANSCRIPTOMIC SYNTHETIC VIRAL RNA OTHER

			# extract sample information, metagenome categories, latlon, date, etc
			samplename = "{0}/{0}.sample.xml".format(member.name)
			try:
				sam_fex = metadata.extractfile(samplename)
			except KeyError:
				nosamplecounter += 1
				if nosamplecounter < WARNMAX:
					sys.stderr.write("WARNING: CANNOT FIND ITEM {}, {}, SKIPPING  {}\n".format(foldercounter, samplename, time.asctime() ) )
				elif nosamplecounter == WARNMAX:
					sys.stderr.write("# {} WARNINGS, WILL NOT DISPLAY MORE  {}\n".format(WARNMAX, time.asctime() ) )
				continue
			#sys.stderr.write("# reading sample info from {}\n".format(samplename))
			sam_xmltree = ET.fromstring(sam_fex.read())
			samxl = sam_xmltree.getchildren() # should be SAMPLE_SET of 1 or more SAMPLE
			#sys.stderr.write("{}\n".format(samplename))
			for sample in samxl:
				samplecounter += 1
				sl = sample.getchildren()
				# should be [<Element 'IDENTIFIERS' at 0x7fe2b5879dd0>, <Element 'TITLE' at 0x7fe2b5879e90>, <Element 'SAMPLE_NAME' at 0x7fe2b5879ed0>, <Element 'DESCRIPTION' at 0x7fe2b5879fd0>, <Element 'SAMPLE_LINKS' at 0x7fe2b5885050>, <Element 'SAMPLE_ATTRIBUTES' at 0x7fe2b58851d0>]
				# >>> sample.attrib
				# {'alias': 'SAMD00028700', 'accession': 'DRS023861'}
				namedict = {}
				sampleattrs = {}
				for sinfo in sl:
					if sinfo.tag=="SAMPLE_ATTRIBUTES":
						for subattr in sinfo.getchildren():
							subsubattr = subattr.getchildren() # should be list
							if len(subsubattr) > 1:
								sampleattrs[subsubattr[0].text] = subsubattr[1].text
							else: # this may become a warning later
								sampleattrs[subsubattr[0].text] = "NO_VALUE"
					if sinfo.tag=="SAMPLE_NAME":
						for subinfo in sinfo.getchildren():
							namedict[subinfo.tag] = subinfo.text
						try:
							rawsamplealias = sample.attrib.get("alias",None)
							if rawsamplealias is not None:
								samplealias = unicodedata.normalize('NFKD', unicode(rawsamplealias)).encode("ascii",errors="replace")
								# remove any tabs within aliases, for appx 100 samples, but still screws up counts
								samplealias = samplealias.replace("\t"," ")
						# ERROR WITH ERA542436/ERA542436.sample.xml, {'center_name': 'ANIMAL HEALTH TRUST', 'alias': u'\xd3sk E', 'accession': 'ERS1013701'}
						except UnicodeEncodeError:
						# caused UnicodeEncodeError due to '\xa0' in some strings
						# '\xa0' apparently is a non-standard space
							samplealias = "ERROR"
				# add attributes to Counter
				# this may be necessary for future debugging, as some attibutes may not be identical between meta data packages on SRA
				sample_attribute_counter.update( sampleattrs.keys() )

				# accession should be the SRA number, like SRA070055
				accession = sample.attrib.get("accession",None)

				# if somehow neither exists, skip
				if accession is None and samplealias is None:
					continue
				# print line
				try:
					sample_columns = u"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format( member.name, samplealias, accession, namedict.get('TAXON_ID',None), namedict.get('SCIENTIFIC_NAME',None), sampleattrs.get("lat_lon","VOID"), sampleattrs.get("collection_date","NA"), sampleattrs.get("isolation_source","NA"), sampleattrs.get("geo_loc_name","NA") )
					expt_columns = u"{}\t{}\t{}".format( library_attrs.get("LIBRARY_STRATEGY","NA"), library_attrs.get("LIBRARY_SOURCE","NA"), library_attrs.get("LIBRARY_SELECTION","NA") )
					outline = u"{}\t{}\n".format(sample_columns, expt_columns)
					norm_outline = unicodedata.normalize('NFKD', outline).encode("ascii",errors="replace")
					sys.stdout.write( norm_outline )
				except UnicodeEncodeError:
					sys.stderr.write("WARNING: COULD NOT PROCESS UNICODE FOR {} ENTRY {}\n".format(accession, foldercounter) )
		else: # meaning isdir() is false, so may be a file
			lastnonfolder = member.name
			nonfolders += 1

	# close tarfile
	metadata.close()

	# report stats of total run
	if nosamplecounter > WARNMAX:
		sys.stderr.write("# Last folder was {}, {}  {}\n".format(foldercounter, samplename, time.asctime() ) )
	sys.stderr.write("# Process completed in {:.1f} minutes\n".format( (time.time()-starttime)/60 ) )
	sys.stderr.write("# Found {} members with {} folders, for {} samples and {} experiments\n".format( membercounter, foldercounter , samplecounter, exptcounter ) )
	if nonfolders: # if any files were not in the normal SRA format folders
		sys.stderr.write("# Found {} files, last one was {}\n".format( nonfolders, lastnonfolder) )
	if noexptcounter:
		sys.stderr.write("# Could not experimental details for {} folders\n".format( noexptcounter ) )
	if nosamplecounter:
		sys.stderr.write("# Could not find samples for {} folders\n".format( nosamplecounter ) )
	# report table of attributes
	sys.stderr.write("### Common sample attributes included:\n")
	for k,v in sample_attribute_counter.items():
		sys.stderr.write("{}\t{}\n".format( k,v ) )
	sys.stderr.write("### Common expt design attributes included:\n")
	for k,v in expt_attribute_counter.items():
		sys.stderr.write("{}\t{}\n".format( k,v ) )

