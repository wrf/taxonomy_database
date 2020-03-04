#!/usr/bin/env python
#
# parse_sra_metadata.py v1 created by WRF 2018-04-24

'''parse_long_sra_metadata.py v1.0 last modified 2020-03-04

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

'''

import sys
import time
import tarfile
import unicodedata
import xml.etree.ElementTree as ET

# for interactive Python debug:
debug='''
import tarfile
import xml.etree.ElementTree as ET
srafile = "NCBI_SRA_Metadata_Full_20191130.tar.gz"
metadata = tarfile.open(name=srafile, mode="r:gz")
member = metadata.next()
member.isdir()
samplename = "{0}/{0}.sample.xml".format(member.name)
fex = metadata.extractfile(samplename)
xmltree = ET.fromstring(fex.read())
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
	sys.stderr.write(sys.stderr)
else:
	starttime = time.time()
	sys.stderr.write("# parsing metadata from {}  {}\n".format( sys.argv[1], time.asctime() ) )
	metadata = tarfile.open(name=sys.argv[1], mode="r:gz")
	samplecounter = 0
	foldercounter = 0
	nonfolders = 0
	nosamplecounter = 0
	WARNMAX = 100
	lastnonfolder = ""
	for member in metadata.getmembers():
		if member.isdir():
			foldercounter += 1
			samplename = "{0}/{0}.sample.xml".format(member.name)
			if not foldercounter % 100000:
				sys.stderr.write("# {} folders  {}\n".format(foldercounter, time.asctime() ) )
			try:
				fex = metadata.extractfile(samplename)
			except KeyError:
				nosamplecounter += 1
				if nosamplecounter < WARNMAX:
					sys.stderr.write("WARNING: CANNOT FIND ITEM {}, {}, SKIPPING  {}\n".format(foldercounter, samplename, time.asctime() ) )
				elif nosamplecounter == WARNMAX:
					sys.stderr.write("# {} WARNINGS, WILL NOT DISPLAY MORE  {}\n".format(WARNMAX, time.asctime() ) )
				continue
			#sys.stderr.write("# reading sample info from {}\n".format(samplename))
			xmltree = ET.fromstring(fex.read())
			xl = xmltree.getchildren() # should be SAMPLE_SET of 1 or more SAMPLE
			#sys.stderr.write("{}\n".format(samplename))
			for sample in xl:
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
							sampleattrs[subsubattr[0].text] = subsubattr[1].text
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
				# accession should be the SRA number, like SRA070055
				accession = sample.attrib.get("accession",None)

				# if somehow neither exists, skip
				if accession is None and samplealias is None:
					continue
				# print line
				try:
					outline = u"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( member.name, samplealias, accession, namedict.get('TAXON_ID',None), namedict.get('SCIENTIFIC_NAME',None), sampleattrs.get("lat_lon","VOID"), sampleattrs.get("collection_date","NA"), sampleattrs.get("isolation_source","NA"), sampleattrs.get("geo_loc_name","NA") )
					norm_outline = unicodedata.normalize('NFKD', outline).encode("ascii",errors="replace")
					sys.stdout.write( norm_outline )
				except UnicodeEncodeError:
					sys.stderr.write("WARNING: COULD NOT PROCESS UNICODE FOR {} ENTRY {}\n".format(accession, foldercounter) )
		else: # meaning isdir() is false, so may be a file
			lastnonfolder = member.name
			nonfolders += 1

	# report stats of total run
	if nosamplecounter > WARNMAX:
		sys.stderr.write("# Last folder was {}, {}  {}\n".format(foldercounter, samplename, time.asctime() ) )
	sys.stderr.write("# Process completed in {:.1f} minutes\n".format( (time.time()-starttime)/60 ) )
	sys.stderr.write("# Found {} folders, and {} samples\n".format( foldercounter , samplecounter ) )
	if nonfolders: # if any files were not in the normal SRA format folders
		sys.stderr.write("# Found {} members not in folders, last one was {}\n".format(nonfolders, lastnonfolder) )
	if nosamplecounter:
		sys.stderr.write("# Could not find samples for {} folders\n".format( nosamplecounter ) )
	metadata.close()

