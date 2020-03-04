#!/usr/bin/env python

# polish_metagenome_table.py

'''polish_metagenome_table.py  last modified 2020-03-04
    tidy up formats, fix lat-long info

polish_metagenome_table.py metagenomes_ext.tab > metagenomes_latlon-fixed.tab

    table generated from parse_ncbi_taxonomy.py, as:
parse_ncbi_taxonomy.py -n names.dmp -o nodes.dmp -i NCBI_SRA_Metadata_Full_20191130.sample_w_cat.tab --metagenomes-only --numbers --samples > NCBI_SRA_Metadata_Full_20191130.metagenomes_w_cat.tab

'''

import sys
import re

if len(sys.argv) < 2:
	sys.exit( __doc__ )
else:
	# counters for various missing data
	dms_counter = 0
	range_counter = 0

	non_nsew_counter = 0
	na_counter = 0
	missing_counter = 0
	nc_counter = 0

	entry_count = 0
	print_count = 0
	sys.stderr.write("# Reading {}\n".format(sys.argv[1]) )
	for line in open(sys.argv[1],'r'):
		entry_count += 1
#    sample    alias    accession  taxonID   scientific name   lat-lon  date  source  location   sample type
#       0         1          2         3              4           5     6     7        8         9
#SRA191450	112451830	SRS723069	646099	human metagenome	NA	NA	stool	NA	human metagenome
#SRA594737	C2b.24.015	SRS2396010	556182	freshwater sediment metagenome	46.512 N 6.587 E	May-2012	Lake sediment_21	Switzerland: Lake Geneva	freshwater sediment metagenome
		lsplits = line.split("\t")
		latlon = lsplits[5]

		# remove obvious ones
		if latlon=="NA":
			na_counter += 1
			continue
		if latlon=="missing":
			missing_counter += 1
			continue
		if latlon=="not collected":
			nc_counter += 1
			continue

#SRA179448	E31	SRS685676	1169740	aquatic metagenome	63A? 33 23.2, 12A? 37 44.4	6/13/10	NA	Sweden: Digern_st_rnen	aquatic metagenome
#SRA175088	BC4_2012_CH4SIP	SRS659670	433727	hot springs metagenome	49.9642500A??, -116.0266500A??	2012	NA	Canada: Buhl Creek	hot springs metagenome
#SRA184378	PA4P1_2009B4_Fungi	SRS703799	410658	soil metagenome	not applicable	25-Aug-2009	NA	Canada: South Farm of the Semiarid Prairie Agricultural Research Centre in Swift Current, Saskatchewan, 50A??16`N 107A??44` W	soil metagenome
#SRA173834	201107FF13	SRS652490	410658	soil metagenome	60A??581.59N; 15A??4759.30E	juil-11	NA	Lamborn	soil metagenome
#SRA169412	Kariega_Water_mouth	SRS628654	1169740	aquatic metagenome	33A?? 406 Lat, 26A?? 410 Long	19-Apr-2011	Water column	South Africa: Kariega Estuary	aquatic metagenome
		# check for weird symbols, indicator of wrong format
		if latlon.count("?") > 0:
			non_nsew_counter += 1
			continue

		# lat-lon is generally YY.YY NS XX.XX EW
		# should split into 4 pieces to [YY.YY, NS, XX.XX, EW]
		raw_latlon = latlon.split(" ")
		# if not, skip
		if len(raw_latlon) != 4:
			non_nsew_counter += 1
			continue
		else:
			latitude, lat_hemi, longitude, long_hemi = raw_latlon

			# check for degree minute seconds
#SRA141824	187_1.sff	SRS560593	749906	gut metagenome	42-02-05 N, 93-37-12 W	NA	NA	USA: Ames, Iowa	gut metagenome
#SRA159216	fungioaklitter	SRS597132	556182	freshwater sediment metagenome	41.44-41.61 N 8.04-8.32 W	2012	NA	Portugal: Northwest	freshwater sediment metagenome

			if latitude.count("-")==2:
				dms_counter += 1
				degree, minutes, seconds = map(float,latitude.split("-"))
				latitude = str(degree + minutes/60 + seconds/3600)
			elif latitude.count("-")==1:
				range_counter += 1
				latitude = latitude.split("-")[0]
			if longitude.count("-")==2:
				degree, minutes, seconds = map(float,longitude.split("-"))
				longitude = str(degree + minutes/60 + seconds/3600)
			elif longitude.count("-")==1:
				longitude = longitude.split("-")[0]

			# fix hemispheres to coordinates
			lat_hemi = lat_hemi.replace(",","")
			if lat_hemi=="S":
				latitude = "-"+latitude
			if long_hemi=="W":
				longitude = "-"+longitude


		lsplits[5] = "{}\t{}".format(latitude, longitude)

		# print line
		print_count += 1
		sys.stdout.write( "\t".join(lsplits) )
	sys.stderr.write("# Counted {} entries, wrote {} entries\n".format(entry_count, print_count) )
	if na_counter:
		sys.stderr.write("# {} entries had 'NA' as lat-lon, removed\n".format(na_counter) )
	if missing_counter:
		sys.stderr.write("# {} entries had 'missing' as lat-lon, removed\n".format(missing_counter) )
	if nc_counter:
		sys.stderr.write("# {} entries had 'not collected' as lat-lon, removed\n".format(nc_counter) )
	if non_nsew_counter:
		sys.stderr.write("# {} entries had an unknown format of lat-lon, removed\n".format(non_nsew_counter) )
	if dms_counter:
		sys.stderr.write("# {} entries had lat-lon as deg-min-sec format, fixed\n".format(dms_counter) )
	if range_counter:
		sys.stderr.write("# {} entries had lat-lon as a range, fixed\n".format(range_counter) )
#
