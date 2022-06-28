#!/usr/bin/env python
#
# parse_sra_metadata.py v1 created by WRF 2018-04-24
# v1.3 2022-04-27  more verbose, some bug fixes
#

'''parse_long_sra_metadata.py v1.3 last modified 2022-06-28
    parses the SRA metadata tar.gz file, makes a 12-column text table

    you must unzip the .tar.gz file
    NOTE: the compression is probably about 97%, so a 4Gb .tar.gz will expand to 130Gb

mkdir 20210404_samples
tar -zxpf 20210404_samples/NCBI_SRA_Metadata_Full_20210404.tar.gz -C 20210404_samples/
parse_long_sra_metadata.py 20210404_samples/ > NCBI_SRA_Metadata_Full_20210404.sample_w_exp.tab 2> NCBI_SRA_Metadata_Full_20210404.sample_w_exp.log

    original mode would directly parse the .tar.gz, this is still allowed
parse_long_sra_metadata.py NCBI_SRA_Metadata_Full_20191130.tar.gz >  NCBI_SRA_Metadata_Full_20191130.sample_ext.tab
    NOTE: parsing metadata can be slow due to the tar.gz size
      above run took between 6-30 days (as SRA increased 4x between 2018 and 2021)

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
import os
import time
import tarfile
import unicodedata
from glob import iglob
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
	noexptcounter = 0 # no expt info file
	nosamplecounter = 0 # no sample info file
	broken_xml_counter = 0 #
	empty_sample_counter = 0 # file exists, but contains no attributes, so make TypeError
	unicode_error_counter = 0 # track weird unicode problems, usually either location name or latlon


	WARNMAX = 100

	sra_is_glob = False
	sra_is_tar = False

	verbose = False

	expt_attribute_counter = Counter()
	sample_attribute_counter = Counter()

	# check for .gz
	sra_metadata_source = sys.argv[1]

	# set up multiple variables and functions differently
	# after the XML parsing step, everything is the same
	if os.path.isdir(sra_metadata_source): # is unzipped dir, so must glob
		metadata = os.path.join(sra_metadata_source, "*")
		if verbose:
			sys.stderr.write("### glob {}\n".format(metadata) )
		sra_iter_obj = iglob(metadata)
		sra_is_glob = True
		member_dir_check = lambda x: os.path.isdir(x)
		fex_open = lambda x: open(x, 'r')
		get_membername = lambda x: os.path.basename(x)
		leading_folder = sra_metadata_source # so .xml names read as NCBI_SRA_Metadata_Full_20200924/SRA070055/SRA070055.sample.xml

	# is .tar or .tar.gz
	elif os.path.isfile(sra_metadata_source):
		if sra_metadata_source.rsplit(".",1)[-1]==".gz":
			tar_openmode = "r:gz"
		else:
			tar_openmode = "r"
		metadata = tarfile.open(name=sra_metadata_source, mode=tar_openmode)
		sra_iter_obj = metadata.getmembers()
		sra_is_tar = True
		member_dir_check = lambda x: x.isdir()
		fex_open = lambda x: metadata.extractfile(x)
		get_membername = lambda x: x.name
		leading_folder = "" # so that .xml names read as SRA070055/SRA070055.sample.xml

	else: # should never occur
		sys.exit("ERROR: cannot find file or folder {}".format(sra_metadata_source) )

	sys.stderr.write("# parsing metadata from {}  {}\n".format( sra_metadata_source, time.asctime() ) )
	for member in sra_iter_obj:
		membercounter += 1
		membername = get_membername(member)
		if member_dir_check(member):
			foldercounter += 1
			if not foldercounter % 100000:
				sys.stderr.write("# {} folders  {}\n".format(foldercounter, time.asctime() ) )

			# extract experiment information, to allow later sorting of genomic, RNAseq, amplicon, etc
			# library strategy possibilities include:
			# WGA WGS WXS RNA-Seq miRNA-Seq WCS CLONE POOLCLONE AMPLICON CLONEEND
			# whole genome assembly; whole genome sequencing; whole exome sequencing; RNA-Seq; micro RNA sequencing
			# whole chromosome random sequencing;
			experimentname = "{1}{0}/{0}.experiment.xml".format( membername, leading_folder )
			try:
				exp_fex = fex_open(experimentname)
			except (IOError, KeyError) as ex: # meaning using glob mode, or tar.gz mode, respectively
				noexptcounter += 1
				exp_fex = None
				# do not skip entry, check sample first
			library_attrs = {} # reset each folder
			if exp_fex is not None:
				exp_xmltree = ET.fromstring(exp_fex.read())
				exptcounter += 1
				for exp_elem in exp_xmltree.iter():
					if exp_elem.text:
						library_attrs[exp_elem.tag] = exp_elem.text.strip()
			# .getchildren() DEPRICATED in python3
			#	expxl = exp_xmltree.getchildren()
			#	for exptdata in expxl:
			#		el = exptdata.getchildren()
			#		for einfo in el: # iterate through IDENTIFIERS TITLE STUDY_REF DESIGN PLATFORM PROCESSING
			#			if einfo.tag=="DESIGN":
			#				for subattr in einfo.getchildren():
			#					if subattr.tag=="LIBRARY_DESCRIPTOR":
			#						for subsubattr in subattr.getchildren(): # contains LIBRARY_LAYOUT LIBRARY_NAME LIBRARY_STRATEGY LIBRARY_SOURCE LIBRARY_SELECTION}
			#							subsubattr_text = subsubattr.text
			#							if subsubattr_text is not None:
			#								library_attrs[subsubattr.tag] = subsubattr.text.strip()
				expt_attribute_counter.update( library_attrs.keys() )
			# library source
			# GENOMIC TRANSCRIPTOMIC METAGENOMIC METATRANSCRIPTOMIC SYNTHETIC VIRAL RNA OTHER

			# extract sample information, metagenome categories, latlon, date, etc
			samplename = "{1}{0}/{0}.sample.xml".format( membername, leading_folder )
			try:
				sam_fex = fex_open(samplename)
			except (IOError, KeyError) as ex: # meaning using glob mode, or tar.gz mode, respectively
				nosamplecounter += 1
				if nosamplecounter < WARNMAX:
					sys.stderr.write("WARNING: CANNOT FIND ITEM {}, {}, SKIPPING  {}\n".format(foldercounter, samplename, time.asctime() ) )
				elif nosamplecounter == WARNMAX:
					sys.stderr.write("# {} WARNINGS, WILL NOT DISPLAY MORE  {}\n".format(WARNMAX, time.asctime() ) )
				continue
			#sys.stderr.write("# reading sample info from {}\n".format(samplename))
			try:
				sam_xmltree = ET.fromstring( sam_fex.read() )
			except ET.ParseError: # xml.etree.ElementTree.ParseError: unclosed token: line 12232, column 4
				broken_xml_counter += 1
				sys.stderr.write("WARNING: BROKEN XML {} FOLDER {}\n".format(accession, foldercounter) )
				continue

			#samxl = sam_xmltree.getchildren() # should be SAMPLE_SET of 1 or more SAMPLE
			#sys.stderr.write("{}\n".format(samplename))
			for sample in list(sam_xmltree):
				samplecounter += 1
				#sl = sample.getchildren()
				# should be [<Element 'IDENTIFIERS' at 0x7fe2b5879dd0>, <Element 'TITLE' at 0x7fe2b5879e90>, <Element 'SAMPLE_NAME' at 0x7fe2b5879ed0>, <Element 'DESCRIPTION' at 0x7fe2b5879fd0>, <Element 'SAMPLE_LINKS' at 0x7fe2b5885050>, <Element 'SAMPLE_ATTRIBUTES' at 0x7fe2b58851d0>]
				# >>> sample.attrib
				# {'alias': 'SAMD00028700', 'accession': 'DRS023861'}
				namedict = {}
				sampleattrs = {}
				for sinfo in list(sample):
					if sinfo.tag=="SAMPLE_ATTRIBUTES":
						for subattr in list(sinfo):
							subsubattr = list(subattr) # should be list
							if len(subsubattr) > 1:
								sampleattrs[subsubattr[0].text] = subsubattr[1].text
							else: # this may become a warning later
								sampleattrs[subsubattr[0].text] = "NO_VALUE"
					if sinfo.tag=="SAMPLE_NAME":
						for subinfo in list(sinfo):
							namedict[subinfo.tag] = subinfo.text
						try:
							rawsamplealias = sample.attrib.get("alias",None)
							if rawsamplealias is not None:
								#samplealias = unicodedata.normalize('NFKD', unicode(rawsamplealias)).encode("ascii",errors="replace")
								#samplealias = rawsamplealias.encode("ascii",errors="replace")
								# remove any tabs within aliases, for appx 100 samples, but still screws up counts
								samplealias = str(rawsamplealias).replace("\t"," ")
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

				# combine all columns
				# namedict should have attributes, even if sample is a metagenome
				sample_columns = [ membername, samplealias, accession, namedict.get('TAXON_ID',None), namedict.get('SCIENTIFIC_NAME',None), sampleattrs.get("lat_lon","VOID"), sampleattrs.get("collection_date","NA"), sampleattrs.get("isolation_source","NA"), sampleattrs.get("geo_loc_name","NA") ]
				expt_columns = [ library_attrs.get("LIBRARY_STRATEGY","NA"), library_attrs.get("LIBRARY_SOURCE","NA"), library_attrs.get("LIBRARY_SELECTION","NA") ]
				out_columns = sample_columns + expt_columns
				# print line
				try:
					outline = "{}\n".format( "\t".join(out_columns) )
					norm_outline = str(outline).encode("ascii",errors="replace").decode()
					sys.stdout.write( outline )
				except TypeError: # sequence item 4: expected str instance, NoneType found
					# occurs when sample XML file exists, but has no attributes
					empty_sample_counter += 1
					sys.stderr.write("WARNING: NO SAMPLE OR EXPT DATA {} FOLDER {}\n".format(accession, foldercounter) )
				except UnicodeEncodeError: # probably mojibake from bad encoding on old sample attributes
					unicode_error_counter += 1
					#norm_outline = str(outline).decode("utf-8").encode("ascii",errors="replace")
					sys.stderr.write("WARNING: UNICODE ISSUE {} FOLDER {}\n".format(accession, foldercounter) )
		else: # meaning isdir() is false, so may be a file
			lastnonfolder = membername
			nonfolders += 1


	# report stats of total run
	if nosamplecounter > WARNMAX:
		sys.stderr.write("# Last folder was {}, {}  {}\n".format(foldercounter, samplename, time.asctime() ) )
	sys.stderr.write("# Process completed in {:.1f} minutes\n".format( (time.time()-starttime)/60 ) )
	sys.stderr.write("# Found {} members with {} folders, for {} samples and {} experiments\n".format( membercounter, foldercounter , samplecounter, exptcounter ) )
	if nonfolders: # if any files were not in the normal SRA format folders
		sys.stderr.write("# Found {} non-folder-files, last one was {}\n".format( nonfolders, lastnonfolder) )
	if noexptcounter:
		sys.stderr.write("# Could not experimental details for {} folders\n".format( noexptcounter ) )
	if nosamplecounter:
		sys.stderr.write("# Could not find samples for {} folders\n".format( nosamplecounter ) )
	if broken_xml_counter:
		sys.stderr.write("# Samples with corrupted XML {}\n".format( broken_xml_counter ) )
	if empty_sample_counter:
		sys.stderr.write("# No attributes for {} samples\n".format( empty_sample_counter ) )
	if unicode_error_counter:
		sys.stderr.write("# Unicode encoding problems for {} samples\n".format( unicode_error_counter ) )
	# report table of attributes
	sys.stderr.write("### Common sample attributes included:\n")
	for k,v in sample_attribute_counter.items():
		try:
			sys.stderr.write("_SAMPLE_ATTR\t{}\t{}\n".format( k, v ) )
		except UnicodeEncodeError: # skip entry, including at least u'\xb0' (degree)
			sys.stderr.write("_SAMPLE_ATTR\t{}\t{}\n".format( str(k).encode("utf-8"), v ) )
	sys.stderr.write("### Common expt design attributes included:\n")
	for k,v in expt_attribute_counter.items():
		try:
			sys.stderr.write("_EXPT_ATTR\t{}\t{}\n".format( k, v ) )
		except UnicodeEncodeError:
			sys.stderr.write("_EXPT_ATTR\t{}\t{}\n".format( str(k).encode("utf-8"), v ) )

#
