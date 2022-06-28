#!/usr/bin/env python
# coding: utf-8
# polish_metagenome_table.py
# v2022-01-07
# v2022-06-28 catch for double-decimal deg-min-sec format

'''polish_metagenome_table.py  last modified 2022-01-07
    tidy up formats, fix lat-long info

polish_metagenome_table.py -i metagenomes_ext.tab > metagenomes_latlon-fixed.tab

    table generated from parse_ncbi_taxonomy.py, as:
parse_ncbi_taxonomy.py -n names.dmp -o nodes.dmp -i NCBI_SRA_Metadata_Full_20191130.sample_w_cat.tab --metagenomes-only --numbers --samples > NCBI_SRA_Metadata_Full_20191130.metagenomes_w_cat.tab

    for placenames:
    http://www.geonames.org/export/
    https://download.geonames.org/export/dump/

    download both: allCountries.zip   countryInfo.txt

./polish_metagenome_table.py -i NCBI_SRA_Metadata_Full_20210404.metagenomes.tab -g allCountries.txt -c countryInfo.txt > NCBI_SRA_Metadata_Full_20210404.metagenomes_latlon-fixed.tab

    NOTE: peak memory using geonames is about 15G

'''

import sys
import re
import argparse
import time
from collections import defaultdict,Counter

def two_part_latlon(latlon, debug=False):
	'''take latlon with any two part split, and return the true latitude and longitude'''

	# cases are given below #
	#########################

	# most basic case
	#55.398487 10.420596
	#SRA172288	8L	SRS646256	749907	sediment metagenome	49.33598. 57.49939	Aug-2009	NA	Canada: Newfoundland	sediment metagenome
	rematch = re.search("(-?[.\d]+) (-?[.\d]+)", latlon)
	if rematch:
		latitude = "{}".format(rematch.group(1))
		longitude = "{}".format(rematch.group(2))
		if latitude[-1]==".":
			latitude = latitude[:-1]
		return latitude, longitude

	# mostly correct, but punctuation problems
	#SRA062712	H1C	SRS464092	938273	hydrocarbon metagenome	57.02, -111.55	2012-06-09	NA	Horse River, Fort McMurray, AB	hydrocarbon metagenome
	#SRA047479	GC6-296	SRS285023	412755	marine sediment metagenome	73.3565 7.565	NA	NA	NA	marine sediment metagenome
	#SRA096192	PR5_2012	SRS465068	433727	hot springs metagenome	57.6526333?, -124.0236833?	2012	NA	Canada: Prophet River	hot springs metagenome
	#SRA123268	LAO-A03-16S	SRS526732	527639	wastewater metagenome	49.5134139o, 006.0179250o	2011-02-23	NA	Luxembourg: Schifflange	wastewater metagenome
	#SRA123258	LAO-A01-16S	SRS526724	527639	wastewater metagenome	49.5134139?, 006.0179250?	2010-10-04	NA	Luxembourg: Schifflange	wastewater metagenome
	#SRA175088	BC4_2012_CH4SIP	SRS659670	433727	hot springs metagenome	49.9642500A??, -116.0266500A??		2012	NA	Canada: Buhl Creek	hot springs metagenome
	rematch = re.search("(-?[.\d]+)[A\?,o]+ (-?[.\d]+)[A\?o]?", latlon)
	if rematch:
		latitude = "{}".format(rematch.group(1))
		longitude = "{}".format(rematch.group(2))
		return latitude, longitude

	# using underscores to separate numbers, and no decimal place
	#SRA172088	673Cage	SRS645239	1436733	rat gut metagenome	4075_N, 11188_W	2/27/14	NA	Salt Lake City UT	rat gut metagenome
	rematch = re.search("(\d+)_?([NS]), (\d+)_?([EW])", latlon)
	if rematch:
		latitude = "{}.{}".format(rematch.group(1)[:-2], rematch.group(1)[-2:])
		lat_hemi = rematch.group(2)
		longitude = "{}.{}".format(rematch.group(3)[:-2], rematch.group(3)[-2:])
		long_hemi = rematch.group(4)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	# use of question mark as degree sign, or after minutes
	#SRA050547	PLANT_1	SRS450931	1348798	terrestrial metagenome	60?58N, 7?31E	NA	Plant root	Norway: Finse	terrestrial metagenome
	#SRA143595	RedSea_2.5m_mixing	SRS619147	408172	marine metagenome	29?28N 34?55E	05.02.2012	10 liters marine bulk water	Gulf of Aqaba	marine metagenome
	#SRA095215	V6	SRS463186	452919	ice metagenome	77?30?S 106?00?E	Jan-1995/Jan-1998	NA	Antarctica: Lake Vostok	ice metagenome
	rematch = re.search("(\d+)\?(\d+)\??([NS]),? (\d+)\?(\d+)\??([EW])", latlon)
	if rematch:
		latitude = "{}.{}".format(rematch.group(1),rematch.group(2))
		lat_hemi = rematch.group(3)
		longitude = "{}.{}".format(rematch.group(4),rematch.group(5))
		long_hemi = rematch.group(6)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	# question mark separator to NS or EW
	#SRA092129	Athabasca_biofilm	SRS455051	718308	biofilm metagenome	56.72?N, 111.40?W	23-Sep-2010	NA	Canada	biofilm metagenome
	#SRA129301	Influent sewage	SRS543595	527639	wastewater metagenome	31.3?N 121.5?E	2013-1-7	NA	China: Shanghai, Quyang	wastewater metagenome
	#21.5A??N 100.5A??E
	rematch = re.search("([.\d]+)[A\?]+([NS]),? ([.\d]+)[A\?]+([EW])", latlon)
	if rematch:
		latitude = "{}".format(rematch.group(1))
		lat_hemi = rematch.group(2)
		longitude = "{}".format(rematch.group(3))
		long_hemi = rematch.group(4)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	# where NS and EW are switched
	#SRA073595	Thr-B	SRS415117	527640	microbial mat metagenome	7649W, 2443N	2/27/10	NA	Bahamas: Highborne Cay	microbial mat metagenome
	rematch = re.search("(\d+)_?([EW]), (\d+)_?([NS])", latlon)
	if rematch:
		latitude = "{}.{}".format(rematch.group(3)[:-2], rematch.group(3)[-2:])
		lat_hemi = rematch.group(4)
		longitude = "{}.{}".format(rematch.group(1)[:-2], rematch.group(1)[-2:])
		long_hemi = rematch.group(2)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	# where o is used as degree sign
#SRA140230	D_42	SRS559158	410658	soil metagenome	37o37N, 101o12E	29-Aug-2011	NA	China: Qinghai-Tibetan Plateau	soil metagenome
	rematch = re.search("(\d+)o(\d+)([NS]), (\d+)o(\d+)([EW])", latlon)
	if rematch:
		latitude = "{}.{}".format(rematch.group(1),rematch.group(2))
		lat_hemi = rematch.group(3)
		longitude = "{}.{}".format(rematch.group(4),rematch.group(5))
		long_hemi = rematch.group(6)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	# way off, as NS:EW XX:YY
	#SRA092006	BLKP83	SRS470040	410658	soil metagenome	N:E 42.4021:128.0947	2010-06-05	NA	China	soil metagenome
	rematch = re.search("([NS]):([EW]) ([.\d]+):([.\d]+)", latlon)
	if rematch:
		latitude = "{}".format(rematch.group(3))
		lat_hemi = rematch.group(1)
		longitude = "{}".format(rematch.group(4))
		long_hemi = rematch.group(2)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	# degree minute second separated by ?, with NS EW
	#SRA045429	pig65_colon_med_16S_muc	SRS455279	1176744	pig metagenome	42?02?05?N 93?37?12?W	2010-01-12	NA	USA: Ames, Iowa	pig metagenome
	rematch = re.search("(\d+)\?(\d+)\?(\d+)\?([NS]) (\d+)\?(\d+)\?(\d+)\?([EW])", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60 + float(rematch.group(3))/3600
		lonmin = float(rematch.group(6))/60 + float(rematch.group(7))/3600
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		lat_hemi = rematch.group(4)
		longitude = "{}.{}".format(rematch.group(5), str(latmin)[2:8])
		long_hemi = rematch.group(8)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	# degree minute second by ? then nothing for min-sec
	#37??3610N, 127??0740E
	rematch = re.search("(\d+)\?\?(\d\d)(\d\d)([NS]), (\d+)\?\?(\d\d)(\d\d)([EW])", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60 + float(rematch.group(3))/3600
		lonmin = float(rematch.group(6))/60 + float(rematch.group(7))/3600
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		lat_hemi = rematch.group(4)
		longitude = "{}.{}".format(rematch.group(5), str(latmin)[2:8])
		long_hemi = rematch.group(8)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	#
	#SRA173834	201107FF13	SRS652490	410658	soil metagenome	60A??581.59N; 15A??4759.30E	juil-11	NA	Lamborn	soil metagenome
	#54A??1832,24N; 2A??414,78W
	#41A??1338.93S 175A??2848.81E
	rematch = re.search("(\d+)A\?\?(\d\d)([,.\d]+)([NS]);? (\d+)A\?\?(\d\d)([,.\d]+)([EW])", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60 + float(rematch.group(3).replace(",","."))/3600
		lonmin = float(rematch.group(6))/60 + float(rematch.group(7).replace(",","."))/3600
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		lat_hemi = rematch.group(4)
		longitude = "{}.{}".format(rematch.group(5), str(latmin)[2:8])
		long_hemi = rematch.group(8)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	#N20?a?33?a?57.9?a? E110?a?04?a?25.2?a?
	rematch = re.search("([NS])(\d+)\?a\?(\d+)\?a\?([.\d]+) ([EW])(\d+)\?a\?(\d+)\?a\?([.\d]+)", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60 + float(rematch.group(3))/3600
		lonmin = float(rematch.group(6))/60 + float(rematch.group(7))/3600
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		lat_hemi = rematch.group(4)
		longitude = "{}.{}".format(rematch.group(5), str(latmin)[2:8])
		long_hemi = rematch.group(8)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	#SRA206241	A	SRS775673	1348798	terrestrial metagenome	34?35.80?N, 104?30.05?E	08-Jan-2013	NA	China: Jinjia Cave, Zhang County, Gansu Province	terrestrial metagenome
	rematch = re.search("(\d+)\?([.\d]+)\?([NS]), (\d+)\?([.\d]+)\?([EW])", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60
		lonmin = float(rematch.group(5))/60
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		lat_hemi = rematch.group(3)
		longitude = "{}.{}".format(rematch.group(4), str(latmin)[2:8] )
		long_hemi = rematch.group(6)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, latitude

	#TODO
	#SRA168388	4banana6 months-10D8	SRS650705	870726	food metagenome	15S 130-140E	Jun-2013	NA	Australia: northern prawn fishery	food metagenome

	#SRA059385	ISATAB-MBL-4:source:PAL_5_1_2008_01_23 orig	SRS367608	408172	marine metagenome	-66.45-73.03 orig	2008-01-23T04:15:00-06	NA	NA	marine metagenome

	#SRA171032	Mu/10/1796	SRS644255	749906	gut metagenome	52529611; 13.401343	03. Mai 10	NA	Germany: Berlin	gut metagenome

	# for all other cases, return None
	if debug:
		print( latlon, file=sys.stderr )
	return None, None




def one_part_latlon(latlon, debug=False):
	'''take latlon that does not split at space, and return the true latitude and longitude'''
	# cases are given below #
	#########################

	# A?? separated degrees with decimal minutes
	#SRA169453	VAG_001	SRS628861	412755	marine sediment metagenome	-36A??30.783,-73A??01.083	14-Dec-2011	NA	Chile:Concepcion	marine sediment metagenome
	rematch = re.search("(-?\d+)A\?\?([.\d]+),(-?\d+)A\?\?([.\d]+)", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60
		lonmin = float(rematch.group(4))/60
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		longitude = "{}.{}".format(rematch.group(3), str(latmin)[2:8] )
		return latitude, longitude

	# basically correct, / separator
	#SRA116868	N2	SRS518857	717931	groundwater metagenome	35.97730333/84.27347358	Nov-2008	NA	USA: Tennessee	groundwater metagenome
	rematch = re.search("(-?[.\d]+)/(-?[.\d]+)", latlon)
	if rematch:
		latitude = "{}".format(rematch.group(1))
		longitude = "{}".format(rematch.group(2))
		return latitude, longitude

	#SRA127585	municipalAS_12	SRS543795	942017	activated sludge metagenome	34?2824.45S_58?358.42W	2013.04.10	NA	Buenos Aires	activated sludge metagenome
	#SRA137650	pmoA_seep1	SRS557364	410658	soil metagenome	60?5318,14N,68?4205,75E	19-Jul-2012	NA	Russia: western siberia:khanty-mansiysk	soil metagenome
	rematch = re.search("(\d+)\?(\d\d)([,.\d]+)([NS])[,_](\d+)\?(\d\d)([,.\d]+)([EW])", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60 + float(rematch.group(3).replace(",","."))/3600
		lonmin = float(rematch.group(6))/60 + float(rematch.group(7).replace(",","."))/3600
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		lat_hemi = rematch.group(4)
		longitude = "{}.{}".format(rematch.group(5), str(latmin)[2:8])
		long_hemi = rematch.group(8)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	#SRA045571	BII-S-25:sample:MCR_11_1_2009_05_09	SRS258379	408172	marine metagenome	-17.4848-149.8336	2009-05-09T:10	NA	NA	marine metagenome
	#SRA059384	ISATAB-MBL-5:source:GNL	SRS367594	449393	freshwater metagenome	66.99-51.01	2007-06-20	NA	NA	freshwater metagenome

	#SRA123701	WX_EW_meta	SRS529931	527639	wastewater metagenome	32?a?0?a?56.10-120?a?19?a?50.60	Aug-2013	NA	China: Nanjing	wastewater metagenome

	#SRA030397	LTR_MRC_2008_Bacteria_16SRNA_gene_survey:sample:MOR4_2_011308	SRS173220	408172	marine metagenome	-166.5217	2008-01-13T08:5010	NA	NA	marine metagenome

	#SRA171856	SYSTCO2	SRS643555	412755	marine sediment metagenome	~50S	Feb-2012	NA	Southern Ocean	marine sediment metagenome

	# as above, for all other cases, return None
	if debug:
		print( latlon, file=sys.stderr )
	return None, None



def six_part_latlon(latlon, debug=False):
	# presumably degree minute second
	#SRA179448	Sed4	SRS685766	1169740	aquatic metagenome	63A? 33 23.4, 12A? 37 29.7	6/17/10	NA	Sweden: Digern_st_rnen	aquatic metagenome
	rematch = re.search("(\d+)A\? (\d+) ([.\d]+), (\d+)A\? (\d+) ([.\d]+)", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60 + float(rematch.group(3))/3600
		lonmin = float(rematch.group(5))/60 + float(rematch.group(6))/3600
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		longitude = "{}.{}".format(rematch.group(4), str(latmin)[2:8] )
		return latitude, longitude

	#48? 15 N 6? 22 E
	#10? 8 S, 145? 35 E
	#15? 36.675 S, 167? 01.258 E
	rematch = re.search("(\d+)\?? ([.\d]+) ([NS]),? (\d+)\?? ([.\d]+) ([EW])", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60
		lonmin = float(rematch.group(5))/60
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		lat_hemi = rematch.group(3)
		longitude = "{}.{}".format(rematch.group(4), str(latmin)[2:8] )
		long_hemi = rematch.group(6)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, latitude

	#22o 46O? S; 43o 41O? W
	rematch = re.search("(\d+)o (\d+)O\? ([NS]); (\d+)o (\d+)O\? ([EW])", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60
		lonmin = float(rematch.group(5))/60
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		lat_hemi = rematch.group(3)
		longitude = "{}.{}".format(rematch.group(4), str(latmin)[2:8] )
		long_hemi = rematch.group(6)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, latitude

	#S 20 3.229502 W 176 8.015363
	rematch = re.search("([NS]) (\d+) ([.\d]+) ([EW]) (\d+) ([.\d]+)", latlon)
	if rematch:
		latmin = float(rematch.group(3))/60
		lonmin = float(rematch.group(6))/60
		latitude = "{}.{}".format(rematch.group(2), str(latmin)[2:8] )
		lat_hemi = rematch.group(1)
		longitude = "{}.{}".format(rematch.group(5), str(latmin)[2:8] )
		long_hemi = rematch.group(4)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, latitude

	#VT grassland: 44.1.912 N 72.7.769 W
	rematch = re.search("(\d+)\.([.\d]+) ([NS]) (\d+)\.([.\d]+) ([EW])", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60
		lonmin = float(rematch.group(5))/60
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		lat_hemi = rematch.group(3)
		longitude = "{}.{}".format(rematch.group(4), str(latmin)[2:8] )
		long_hemi = rematch.group(6)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, latitude

	#N60 34 56.3 E14 38 20.5
	rematch = re.search("([NS])(\d+) (\d+) ([.\d]+) ([EW])(\d+) (\d+) ([.\d]+)", latlon)
	if rematch:
		latmin = float(rematch.group(3))/60 + float(rematch.group(4).replace(",","."))/3600
		lonmin = float(rematch.group(7))/60 + float(rematch.group(8).replace(",","."))/3600
		latitude = "{}.{}".format(rematch.group(2), str(latmin)[2:8] )
		lat_hemi = rematch.group(1)
		longitude = "{}.{}".format(rematch.group(6), str(latmin)[2:8])
		long_hemi = rematch.group(5)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	# presumably just degree and minutes, though this should be southern hemisphere
	# return None for now #TODO
	#SRA169412	Kariega_Water_mouth	SRS628654	1169740	aquatic metagenome	33A?? 406 Lat, 26A?? 410 Long	19-Apr-2011	Water column	South Africa: Kariega Estuary	aquatic metagenome
	rematch = re.search("(\d+)A\?\? (\d+) Lat, (\d+)A\?\? (\d+) Long", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60
		lonmin = float(rematch.group(4))/60
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		longitude = "{}.{}".format(rematch.group(3), str(latmin)[2:8] )
		return None, None
	#
	if debug:
		print( latlon, file=sys.stderr )
	return None, None






def four_part_latlon(latlon, debug=False):
	# presumably degree minute second separated by A?? with NS, EW
	#SRA172745	Tenerias	SRS647989	717931	groundwater metagenome	25A??32A??10 N, 100A??58A??55 W	Oct-2011NA	Mexico: State of Coahuila	groundwater metagenome
	rematch = re.search("(\d+)A\?\?(\d+)A\?\?(\d+) ([NS]), (\d+)A\?\?(\d+)A\?\?(\d+) ([EW])", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60 + float(rematch.group(3))/3600
		lonmin = float(rematch.group(6))/60 + float(rematch.group(7))/3600
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		lat_hemi = rematch.group(4)
		longitude = "{}.{}".format(rematch.group(5), str(latmin)[2:8] )
		long_hemi = rematch.group(8)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	# mostly normal, includes A?? NS, EW
	#SRA172235	C1	SRS649280	1515737	money metagenome	28.6100A?? N, 77.2300A?? E	2013	NA	India	money metagenome
	rematch = re.search("([.\d]+)A\?\? ([NS]), ([.\d]+)A\?\? ([EW])", latlon)
	if rematch:
		latitude = "{}".format(rematch.group(1))
		lat_hemi = rematch.group(2)
		longitude = "{}".format(rematch.group(3))
		long_hemi = rematch.group(4)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	# degree minute with o as degree symbol NS, EW
	#SRA170498	454Reads_06037.sff	SRS637056	1041057	sea squirt metagenome	17o55 S, 177o16 E	NA	NA	Fiji	sea squirt metagenome
	rematch = re.search("(\d+)o(\d+) ([NS]), (\d+)o(\d+) ([EW])", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60
		lonmin = float(rematch.group(5))/60
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		longitude = "{}.{}".format(rematch.group(4), str(latmin)[2:8] )
		lat_hemi = rematch.group(3)
		long_hemi = rematch.group(6)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	# degree minute with . as separator
	#DRA011885	SAMD00291244	DRS180442	412755	marine sediment metagenome	41.10.5983 N 142.12.0328 E	2011-11-14	NA	Japan:off Shimokita Peninsula	AMPLICON	METAGENOMIC	PCR
	rematch = re.search("(\d+)\.(\d+)\.(\d+) ([NS]), (\d+)\.(\d+)\.(\d+) ([EW])", latlon)
	if rematch:
		latmin = float(rematch.group(2))/60 + float(rematch.group(3))/3600
		lonmin = float(rematch.group(6))/60 + float(rematch.group(7))/3600
		latitude = "{}.{}".format(rematch.group(1), str(latmin)[2:8] )
		lat_hemi = rematch.group(4)
		longitude = "{}.{}".format(rematch.group(5), str(latmin)[2:8] )
		long_hemi = rematch.group(8)
		if lat_hemi=="S":
			latitude = "-"+latitude
		if long_hemi=="W":
			longitude = "-"+longitude
		return latitude, longitude

	# appears to have A??A?? as decimal and switched order of EW, NS
	#SRA172986	Zhang_Yang	SRS659936	410658	soil metagenome	116A??A??5927 E, 30A??A??2808 N	Apr 20th and May 25th,2012	NA	Anqing, Anhui	soil metagenome

	#SRA127724	Reduced2	SRS534538	410658	soil metagenome	48?3013.50 N, 11?2650.80 E	26-Nov-2012	NA	Germany: Scheyern	soil metagenome

	# otherwise return None
	if debug:
		print( latlon, file=sys.stderr )
	return None, None


################################################################################


def fix_date_formats(rawdate):

	# https://submit.ncbi.nlm.nih.gov/biosample/template/?package=Invertebrate.1.0&action=definition
	# supported formats include "DD-Mmm-YYYY", "Mmm-YYYY", "YYYY" or ISO 8601 standard "YYYY-mm-dd", "YYYY-mm", "YYYY-mm-ddThh:mm:ss"; 
	# e.g., 30-Oct-1990, Oct-1990, 1990, 1990-10-30, 1990-10, 21-Oct-1952/15-Feb-1953, 2015-10-11T17:53:03Z
	months = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"03", "May":"05", "Jun":"06", 
              "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12" }

	# if date is in YEAR-MO-DA format, but could include words on either side
	rematch = re.search("(\d\d\d\d)-(\d\d)-(\d\d)", rawdate)
	if rematch:
		year, month, day = rematch.groups()
		ymd_format = "{}-{}-{}".format( year, month, day )
		return ymd_format

	# if date is DD-Mmm-YYYY format
	# 4 \w are used to allow for mistaken use of full months
	rematch = re.search("^(\d\d)-(\w+)-(\d\d\d\d)$", rawdate)
	if rematch:
		day, month, year = rematch.groups()
		monthnum = months.get(month[0:3], "00")
		ymd_format = "{}-{}-{}".format( year, monthnum, day )
		return ymd_format

	# if date is only YEAR-MO format
	rematch = re.search("^(\d\d\d\d)-(\d\d)$", rawdate)
	if rematch:
		return rawdate + "-00"

	# if date is Mmm-YYYY format
	rematch = re.search("^(\w+)-(\d\d\d\d)$", rawdate)
	if rematch:
		month, year = rematch.groups()
		monthnum = months.get(month[0:3], "00")
		ymd_format = "{}-{}-00".format( year, monthnum )
		return ymd_format

	# if date is only YEAR
	rematch = re.search("^(\d\d\d\d)$", rawdate)
	if rematch:
		return rawdate + "-00-00"

	# for all other cases, return all zeroes
	return "0000-00-00"


################################################################################


def import_geonames_features(geofeatures_file):
	'''read featureCodes_en.txt, return a dict'''
	feature_desc_dict = {"A.":"administrative definition", "H.":"hydrological type", 
						"L.":"land use type", "P.":"populated type",
						"R.":"road type", "S.":"spot building type",
						"T.":"terrain type", "U.":"undersea type", "V.":"vegetation type" }
	sys.stderr.write("# Reading feature descriptions from {}\n".format(geofeatures_file) )
	for line in open(geofeatures_file,'r'):
		if line and line[0] != "#": # remove comments
			lsplits = line.split("\t")
	# features are 3 column tab delimited, of
	#code	name	description
	#H.LKO	oxbow lake	a crescent-shaped lake commonly found adjacent to meandering streams
			feature_code = lsplits[0]
			feature_type = lsplits[1]
			feature_desc = lsplits[2].strip()
			feature_desc_dict[feature_code] = feature_type
	sys.stderr.write("# Found {} feature codes\n".format( len(feature_desc_dict) ) )
	return feature_desc_dict

def import_geonames_country_codes(country_codes_file, verbose=False):
	'''read countryInfo.txt, return a dict'''
	#  0       1              2    3          4       5     6            7           8           9   10             11              12       13                 14                   15          16          17          18
	#ISO	ISO3	ISO-Numeric	fips	Country	Capital	Area(in sq km)	Population	Continent	tld	CurrencyCode	CurrencyName	Phone	Postal Code Format	Postal Code Regex	Languages	geonameid	neighbours	EquivalentFipsCode
	#AD	AND	020	AN	Andorra	Andorra la Vella	468	77006	EU	.ad	EUR	Euro	376	AD###	^(?:AD)*(\d{3})$	ca	3041565	ES,FR	
	#AE	ARE	784	AE	United Arab Emirates	Abu Dhabi	82880	9630959	AS	.ae	AED	Dirham	971			ar-AE,fa,en,hi,ur	290557	SA,OM	
	#AF	AFG	004	AF	Afghanistan	Kabul	647500	37172386	AS	.af	AFN	Afghani	93			fa-AF,ps,uz-AF,tk	1149361	TM,CN,IR,TJ,PK,UZ	
	codes_to_country_dict = {"USA" : "United States" , "UK" : "United Kingdom" , "UAE": "United Arab Emirates"}

	sys.stderr.write("# Reading country codes from {}  {}\n".format(country_codes_file, time.asctime() ) )
	for line in open(country_codes_file,'r'):
		line = line.rstrip()
		if line and line[0]!="#":
			lsplits = line.split("\t")
			two_letter_code = lsplits[0].strip()
			country_name = lsplits[4].strip()
			codes_to_country_dict[two_letter_code] = country_name
	sys.stderr.write("# Found {} country codes\n".format( len(codes_to_country_dict) ) )
	return codes_to_country_dict

def filter_unique_placenames( redundant_names_to_latlon, redundant_alternate_to_ascii ):
	'''return dictionary of unique names with latlon'''
	unique_name_latlon_dict = {} # key is non redundant names, value is latlon tuple

	unique_key_counter = 0
	redundant_key_counter = 0
	usable_alternates = 0
	redundant_alternates = 0
	alternate_without_unique = 0

	sys.stderr.write("# Filtering keys for unique place names  {}\n".format( time.asctime() ) )
	for k,v in redundant_names_to_latlon.items():
		if len(v) == 1:
			unique_name_latlon_dict[k] = v[0]
			unique_key_counter += 1
		else:
			redundant_key_counter += 1
	sys.stderr.write("# {} unique , {} redundant places  {}\n".format( unique_key_counter, redundant_key_counter, time.asctime() ) )
	sys.stderr.write("# Sorting alternate names  {}\n".format( time.asctime() ) )
	for k,v in redundant_alternate_to_ascii.items():
		if len(set(v)) == 1:	# meaning alternate links to 1 name
			alt_ascii_latlon = unique_name_latlon_dict.get(v[0],[])
			if alt_ascii_latlon: # meaning was in unique_name_latlon_dict as unique, use the latlon for this name
				usable_alternates += 1
				unique_name_latlon_dict[k] = alt_ascii_latlon
			else: # meaning was not in unique_name_latlon_dict
				alternate_without_unique += 1
		else: # alternate has multiple redundant ascii possibilities
			redundant_alternates += 1
	sys.stderr.write("# {} usable alternates , {} redundant alternates , {} alternates to non-unique main  {}\n".format( usable_alternates, redundant_alternates, alternate_without_unique, time.asctime() ) )
	return unique_name_latlon_dict

def import_geonames_all_countries(geodata_file, feature_desc_dict, country_code_dict, verbose=False):
	'''read allCountries.txt, return dict of unique placenames with latlon tuple'''

	us_state_abbvs_to_name = { "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "DC":"Washington DC" }

	ch_canton_abbvs_to_name = {"ZH":"Zürich", "BE":"Bern", "LU":"Luzern", "UR":"Uri", "SZ":"Schwyz", "OW":"Obwalden", "NW":"Nidwalden", "GL":"Glarus", "ZG":"Zug" , "FR":"Fribourg", "SO":"Solothurn", "BS":"Basel-Stadt", "BL":"Basel-Landschaft", "SH":"Schaffhausen", "AR":"Appenzell Ausserrhoden", "AI":"Appenzell Innerrhoden", "SG":"St. Gallen", "GR":"Graubünden", "AG":"Aargau", "TG":"Thurgau", "TI":"Ticino", "VD":"Vaud", "VS":"Valais", "NE":"Neuchâtel", "GE":"Geneva", "JU":"Jura" }

	entry_counter = 0 # total entries
	no_country_entries = 0 # features without a country tag, such as 
	feature_counter = defaultdict(int)
	state_name_counter = defaultdict(int)
	ascii_counts_dict = Counter() # counter for each ascii name, showing many are non-unique

	main_names_to_latlon = defaultdict(list) # key is name in ascii, value is list of lat-long strings
	# if list of strings contains 1 entry after parsing the entire file, then keep the name
	alternate_to_ascii = defaultdict(list) # key is unicode name, alternate names, value is ascii name
	top_level_latlon = {} # key is country, val is lat-lon as list

	countries_w_sra_states = [ "US" , "CH" ]
	# probaby exclude:
	#Belgium:BRU	502
	#Belgium:VLG	10173
	#Belgium:WAL	9462
	#United Kingdom:ENG	44470
	#United Kingdom:NIR	1596
	#United Kingdom:SCT	13105
	#United Kingdom:WLS	4680

	sys.stderr.write("# Reading place names and locations from {}  {}\n".format(geodata_file, time.asctime() ) )
	for line in open(geodata_file,'r'):
		line = line.strip()
		if line and line[0] != "#": # remove comments
			entry_counter += 1
			if entry_counter % 1000000 == 0:
				sys.stderr.write("# {}  {}\n".format(entry_counter, time.asctime() ) )

			lsplits = line.split("\t")

			asciiname = lsplits[2]

			unicodename = lsplits[1]
			alternate_names = set(lsplits[3].split(","))
			country_code = lsplits[8] # AQ for Antarctica
			if not country_code: # may be empty string
				no_country_entries += 1
			country_name = country_code_dict.get(country_code,None)

			admin_level_1 = lsplits[10] # for states
			if country_code == "US":
				state_name = us_state_abbvs_to_name.get(admin_level_1,None)
			elif country_code == "AU":
				state_name = admin_level_1.replace("State of ", "")
			elif country_code == "CH":
				state_name = ch_canton_abbvs_to_name.get(admin_level_1,None)
			else:
				state_name = admin_level_1
			country_state_str = "{}:{}".format( country_name , admin_level_1 )
			state_name_counter[country_state_str] += 1

			ascii_counts_dict[asciiname] += 1

			latitude = lsplits[4]
			longitude = lsplits[5]

			feature_class = lsplits[6]
			feature_code = lsplits[7]
			combined_feature = "{}.{}".format(feature_class, feature_code)
			feature_counter[combined_feature] += 1

			# build names for dictionary
			# any non-unique name will have a dict-list length of >1
			# and cannot be used to ID places
			if combined_feature=="A.PCLI": # meaning "independent political entity" or high level country ID
				# records do not have location, then skip and use capital
				alternate_to_ascii[asciiname].append( country_name )
				for alternate_name in alternate_names:
					alternate_to_ascii[alternate_name].append( country_name )
				continue

			#
			# set the lat lon
			#
			if not latitude or not longitude:
				continue

			# of place name alone
			# #TODO possibly only do this for A features, and only do country+place for P features
			main_names_to_latlon[asciiname].append( [latitude, longitude] )
			alternate_to_ascii[unicodename].append( asciiname )
			for alternate_name in alternate_names:
				alternate_to_ascii[alternate_name].append( asciiname )

			# meaning entry is the capital, so set each country
			if combined_feature=="P.PPLC":
			# 323786	Ankara	Ankara	ANK,Anakara,Ancara,Ancyra,Ang-ka-la,Angkara,Angora,Anguriyah,Ankar,Ankara,Ankara khot,Ankaro,Ankuara,Ankura,Ankyra,Ankyra (Ankyra),Anqara,Enguri,Engüri,Enqere,akara,an ka la,angkala,ankara,anqrh,anqrt,xangkara,Ăng-kā-lá,,,	39.91987	32.85427	P	PPLC	TR		68				3517182	850	874	Europe/Istanbul	2019-09-05
			# TR	TUR	792	TU	Turkey	Ankara	780580	82319724	AS	.tr	TRY	Lira	90	#####	^(\d{5})$	tr-TR,ku,diq,az,av	298795	SY,GE,IQ,IR,GR,AM,AZ,BG	
				# also set the country, using strict country pattern of "country:"
				# individual places should be set at "place" or "country:place"
				# to distinguish between VA: Vatican: and VA Virginia
				top_level_latlon["{}:".format(country_code)] = [latitude, longitude]
				top_level_latlon["{}:".format(country_name)] = [latitude, longitude]
				country_capital = "{}:{}".format( country_name , asciiname )
				top_level_latlon[country_capital] = [latitude, longitude]

			# try country name for most features, so "Lake Geneva" becomes "Switzerland:Lake Geneva"
			if country_name is not None:
				asciiname_w_country = "{}:{}".format( country_name , asciiname )
				main_names_to_latlon[asciiname_w_country].append( [latitude, longitude] )
				unicodename_w_country = "{}:{}".format( country_name , unicodename )
				alternate_to_ascii[unicodename_w_country].append( asciiname_w_country )
				for alternate_name in alternate_names:
					unicodename_w_country = "{}:{}".format( country_name , alternate_name )
					alternate_to_ascii[unicodename_w_country].append( asciiname_w_country )
				# only make longer name if country AND admin level 1 are given, mostly for US states 
				if admin_level_1 and country_code in countries_w_sra_states:
					asciiname_w_adm1 = "{}:{},{}".format( country_name , admin_level_1 , asciiname )
					main_names_to_latlon[asciiname_w_adm1].append( [latitude, longitude] )
					asciiname_w_state = "{}:{},{}".format( country_name , state_name , asciiname )
					main_names_to_latlon[asciiname_w_state].append( [latitude, longitude] )
					unicodename_w_adm1 = "{}:{},{}".format( country_name , state_name , unicodename )
					alternate_to_ascii[asciiname_w_adm1].append( asciiname_w_adm1 )
					for alternate_name in alternate_names:
						unicodename_w_adm1 = "{}:{},{}".format( country_name , state_name , alternate_name )
						alternate_to_ascii[unicodename_w_adm1].append( asciiname_w_adm1 )

	if verbose:
		for feature in sorted(feature_counter.keys()):
			ft_outline = "{0}\t{1}\t{2}\n".format( feature, feature_desc_dict.get(feature,"-"), feature_counter.get(feature,0) )
			sys.stderr.write(ft_outline)

		for state_name in sorted(state_name_counter.keys()):
			sn_outline = "{0}\t{1}\n".format(state_name, state_name_counter.get(state_name,0) )
			sys.stderr.write(sn_outline)

	feature_sum = sum(feature_counter.values())
	sys.stderr.write("# Found {} place names  {}\n".format(feature_sum, time.asctime() ) )

	# prove that each ascii name occurs exactly once
	# without country codes
	# Most common was [('San Antonio', 2791), ('San Jose', 2647), ('First Baptist Church', 2639), 
	# ('The Church of Jesus Christ of Latter Day Saints', 2175), ('Santa Rosa', 1896), ('San Francisco', 1862), 
	# ('San Isidro', 1791), ('La Esperanza', 1711), ('San Juan', 1710), ('Church of Christ', 1657), 
	# ('San Miguel', 1621), ('Mill Creek', 1533), ('Spring Creek', 1513), ('First Presbyterian Church', 1342), 
	# ('San Pedro', 1285), ('Dry Creek', 1266), ('Santa Cruz', 1251), ('Santa Maria', 1247), ('San Rafael', 1194), 
	# ('Rampur', 1171), ('Buenavista', 1140), ('Krajan', 1126), ('Stormyra', 1103), ('Mount Zion Church', 1098), 
	# ('Bear Creek', 1083), ('Bethel Church', 1075), ('Mud Lake', 1071), ('Santa Rita', 1001), ('El Porvenir', 990), 
	# ('La Palma', 989), ('Cerro Colorado', 973), ('First United Methodist Church', 954), ('Buenos Aires', 919), 
	# ('Kingdom Hall of Jehovahs Witnesses', 904), ('Haugen', 898), ('San Luis', 890), ('La Laguna', 886), 
	# ('Buena Vista', 868), ('Ojo de Agua', 860), ('Rock Creek', 849), ('Santa Ana', 848), ('El Carmen', 817), 
	# ('El Rincon', 815), ('Church of God', 812), ('Santa Lucia', 806), ('Indian Creek', 803), 
	# ('Long Lake', 798), ('Cedar Creek', 792), ('Santa Elena', 776), ('Saint Johns Church', 774)] 
	# need to prefix country code to make places unique
	if verbose:
		sys.stderr.write("# Most common was {} \n".format( ascii_counts_dict.most_common(50) ) )

	#
	# begin sorting the unique placenames
	#
	unique_name_to_latlon = filter_unique_placenames( main_names_to_latlon, alternate_to_ascii )
	sys.stderr.write("# Adding {} top level annotations\n".format( len(top_level_latlon) ) )
	unique_name_to_latlon.update( top_level_latlon )
	return unique_name_to_latlon



def get_geonames_latlon(location, geonames_places, debug=False):
	'''check if place has a geonames lat lon or use capital city by country, and return lat and lon'''
	if geonames_places.get(location, False):
		latitude, longitude = geonames_places.get(location)
		return latitude, longitude, location

	country_place_splits = location.split(":",1)
	country = country_place_splits[0].strip()
	place = country_place_splits[-1].strip()

	if country==place: # meaning country only, since splits[-1] is the same as splits[0]
		country_strict = "{}:".format(country)
		if geonames_places.get(country_strict, False):
			latitude, longitude = geonames_places.get(country_strict)
			return latitude, longitude, False # flag for country only
		place = False

	if country=="US" or country=="USA":
		country = "United States"
	elif country=="Viet nam" or country=="Viet Nam":
		country = "Vietnam"	
	elif country=="Czech Republic":
		country = "Czechia"
	elif country=="Korea":
		country = "South Korea"
	elif country=="The Gambia":
		country = "Gambia"
	elif country=="The Bahamas":
		country = "Bahamas"
	elif country=="Commonwealth of Puerto Rico" or country=="PuertoRico":
		country = "Puerto Rico"
	elif country=="Republic of Ireland":
		country = "Ireland"
	elif country=="Cote dIvoire":
		country = "Ivory Coast"

	if place=="Unspecified": # country given, but not place ERA815140 ERA1217322 ERA730222
		place = False

	if place:
		if geonames_places.get(place, False):
			latitude, longitude = geonames_places.get(place)
			return latitude, longitude, place

		location_no_space = "{}:{}".format( country, place )
		if geonames_places.get(location_no_space, False):
			latitude, longitude = geonames_places.get(location_no_space)
			return latitude, longitude, location_no_space

		if country=="China": # many cities are not annotated as "Shi" like "Beijing Shi"
			china_city_with_shi = "{}:{} Shi".format( country, place )
			if geonames_places.get(china_city_with_shi, False):
				latitude, longitude = geonames_places.get(china_city_with_shi)
				return latitude, longitude, china_city_with_shi

		place_comma_splits = [ x.strip() for x in place.split(",",1) ]
		co_pl_comma_no_space = "{}:{}".format( country, ",".join(place_comma_splits) )
		if geonames_places.get(co_pl_comma_no_space, False):
			latitude, longitude = geonames_places.get(co_pl_comma_no_space)
			return latitude, longitude, co_pl_comma_no_space
		elif geonames_places.get(place_comma_splits[-1], False):
			latitude, longitude = geonames_places.get(place_comma_splits[-1])
			return latitude, longitude, place_comma_splits[-1]
		if country=="United States":
			swap_US_state_and_city = "{}:{}".format( country, ",".join(place_comma_splits[::-1]) )
			if geonames_places.get(swap_US_state_and_city, False):
				latitude, longitude = geonames_places.get(swap_US_state_and_city)
				return latitude, longitude, swap_US_state_and_city

		place_dot_splits = [ x.strip() for x in place.split(":",1) ]
		co_pl_dot_no_space = "{}:{}".format( country, ",".join(place_dot_splits) )
		if geonames_places.get(co_pl_dot_no_space, False):
			latitude, longitude = geonames_places.get(co_pl_dot_no_space)
			return latitude, longitude, co_pl_dot_no_space
		elif geonames_places.get(place_dot_splits[-1], False):
			latitude, longitude = geonames_places.get(place_dot_splits[-1])
			return latitude, longitude, place_dot_splits[-1]

	# known exceptions #TODO
	# USA:Tennessee,Chattanooga,Tennessee Aquarium  # too many splits
	# Southern Ocean:Antarctic
	# Sourth America   # ERA1558713
	# France:Villeneuve dAscq  # should have '  SRA1073975  mouse guts
	# Portugal: BraganA??a
	# Commonwealth of Puerto Rico
	# S?r Rondane Mountains   # should be Sør Rondane Mountains, Antarctica
	# GAZ:00313293   # ERA625228  BioProject PRJEB14094 says Basque country 
	# sandiego   # ERA590863
	# GER: Karlsruhe   # ERA2760851
	# UCSD:CA:San Diego   # ERA2379720
	# University of Wisconsin   # high redundancy of this name due to branch campus alternate names
	# The Gambia  # SRA163452
	# Georgia Republic   # ERA739093 more UCSD microbiome, samples have excel copy error for NCBI tax ID
	# Guri, Republic of Korea   # SRA144546  crohns disease
	# Texcoco, Estado de Mexico, Mexico   # SRA059173
	# Vietman:Son Trac   # ERA673502
	# RSA   # ERA1978960  UCSD micro
	# United States of America of America   # ERA782693 UCSD on sponges
	# Chernobyl Nuclear Power Plant Exclusion Zone   # ERA1555442 UCSD on voles
	# Japan; Okinawa   # uses semicolon  DRA002424
	# 42.6667? N, 76.5333? W   # SRA101503
	# Cote dIvoire   #
	# Crete   # SRA059280
	# Europe   #
	# Ardley cove??Fildes Peninsula
	# San Francisco Bay Area, CA
	# 55.681166,12.276471   # SRA121966
	# Macau   # SRA808026

	# try country by itself
	no_line_country = "{}:".format( country.replace("_"," ") )
	if geonames_places.get(no_line_country, False):
		latitude, longitude = geonames_places.get(no_line_country)
		return latitude, longitude, False # flag for country only

	# meaning search did not work
	#print( "location {}   {}   {}".format(location, country, place), file=sys.stdout )
	return None, None, None


# BEGIN MAIN CODE BLOCK
##################################################
##################################################

def main(argv, wayout):
	if not len(argv):
		argv.append('-h')
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)
	parser.add_argument('-i','--input', help="raw SRA extended metadata file, from parse_ncbi_taxonomy.py")
	parser.add_argument('-c','--geonames-countries', help="optional GeoNames country info, from countryInfo.txt")
	parser.add_argument('-g','--geonames-data', help="optional GeoNames data, from allCountries.txt")
	parser.add_argument('--verbose', action="store_true", help="make verbose")
	args = parser.parse_args(argv)

	
	#
	# READ OPTIONAL GEONAMES DATABASE
	#
	geo_feature_descr_dict = {} # use blank to make things run anyway
	if args.geonames_data and args.geonames_countries:
		print( "# Importing optional geonames database for location searches  {}".format(time.asctime()), file=sys.stderr )
		geo_country_info_dict = import_geonames_country_codes( args.geonames_countries , args.verbose )
		unique_name_to_latlon = import_geonames_all_countries( args.geonames_data , geo_feature_descr_dict , geo_country_info_dict , args.verbose )


	#
	# FIX LAT-LON INFORMATION
	#

	# The geographical coordinates of the location where the sample was collected. 
	# Specify as degrees latitude and longitude in format "d[d.dddd] N|S d[dd.dddd] W|E", eg, 38.98 N 77.11 W
	# counters for various missing data
	dms_counter = 0
	range_counter = 0
	one_part_fix = 0
	two_part_fix = 0
	four_part_fix = 0
	six_part_fix = 0

	non_nsew_counter = 0 # latlon format is not NSEW
	void_counter = 0 # latlon is VOID from previous steps
	missing_latlon_counter = 0 # latlon is given as one of the missing_variants

	loc_field_counter = 0 # something is in the location field
	loc_na_counter = 0 # location is NA from previous steps
	missing_loc_counter = 0 # location is one of the missing_variants
	no_location_counter = 0 # location is blank

	match_any_loc_counter = 0 # number of times that the latlon was missing, but found some address in geonames
	found_exact_location = 0 # found precise location beyond just country
	country_only_names = 0 # number of cases that only had country level ID

	cannot_find_loc_counter = 0 # location given, but cannot get lat lon from geonames

	# samples with EITHER a valid lat-lon (even if bad) or valid location (even if not found)
	any_source_position = 0
	# this should be forbidden, but happens anyway
	no_source_position_given = 0 # counter for samples with not latlon AND no given location

	# counters for date correction
	no_date_counter = 0
	has_date_counter = 0
	strange_date = 0

	# includes typo of 'not availalble' and 'missisng_1'
	missing_variants = ["missing", "Missing", "MISSING", "NA", "N/A", "na", "n/a", "n/A", "N.A.", "NOT APPLICABLE", "Not Applicable", "Not applicable", "not applicable", "not appicable", "not determined", "not recorded", "not collected", "Not collected", "Not Collected", "NOT COLLECTED", "not available", "Not available", "Not Available", "not availalble", "not provided", "Not provided", "Unknown", "unknown", "-", "None", "none", "missisng_1", "missisng_2", "missisng_3", "missisng_4", "NULL", "?", "AE", "Unspecified", "NO_VALUE"]

	nc_variants = ["large intestine", "blood", "Vosges", "V5-V9", "Kolkata", "diverse", "bacteria", "Morvan mountains", "lab", "Synthetic mixture of 18 yeast/bacteria/archaeal species", ""]
	nc_counter = 0

	entry_count = 0
	print_count = 0
	sys.stderr.write("# Reading {}\n".format(args.input) )
	for line in open(args.input,'r'):
		entry_count += 1
		has_latlon_field = True
		has_location_field = True
		bad_latlon = False
		location_found = False

		# basic pattern should split line into 10 columns
#    sample    alias    accession  taxonID   scientific name   lat-lon  date  source  location   sample type
#       0         1          2         3              4           5     6     7        8         9
#SRA191450	112451830	SRS723069	646099	human metagenome	NA	NA	stool	NA	human metagenome
#SRA594737	C2b.24.015	SRS2396010	556182	freshwater sediment metagenome	46.512 N 6.587 E	May-2012	Lake sediment_21	Switzerland: Lake Geneva	freshwater sediment metagenome
		lsplits = line.split("\t")
		raw_latlon = lsplits[5]
		location_name = lsplits[8]

		# remove obvious ones
		if raw_latlon=="VOID": # VOID should derive from previous steps
			void_counter += 1
			has_latlon_field = False
		elif raw_latlon in missing_variants:
			missing_latlon_counter += 1
			has_latlon_field = False
		elif raw_latlon in nc_variants:
			nc_counter += 1
			has_latlon_field = False
		elif raw_latlon == "":
			missing_latlon_counter += 1
			has_latlon_field = False

		# check if the sample at least has a location
		if location_name == "NA":
			loc_na_counter += 1
			has_location_field = False
		elif location_name in nc_variants: # table entry is blank
			no_location_counter += 1
			has_location_field = False
		elif location_name in missing_variants:
			missing_loc_counter += 1
			has_location_field = False
		else:
			loc_field_counter += 1

		# sample cannot be plotted, remove from table
		if has_latlon_field is False and has_location_field is False:
			no_source_position_given += 1
			continue
		any_source_position += 1

################################################################################

		# parse NCBI format lat-lon
		# all entries should be like this
		# lat-lon is generally YY.YY NS XX.XX EW
		# should split into 4 pieces to [YY.YY, NS, XX.XX, EW]
		if has_latlon_field is True:
			latlonsp = raw_latlon.split(" ")
			# if not, skip
			if len(latlonsp) == 4:
				latitude, lat_hemi, longitude, long_hemi = latlonsp

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
				elif latitude.count(".")==2 and latitude.count("-")==0:
					dms_counter += 1
					degree, minutes, seconds = map(float,latitude.split("."))
					latitude = str(degree + minutes/60 + seconds/3600)
				if longitude.count("-")==2:
					degree, minutes, seconds = map(float,longitude.split("-"))
					longitude = str(degree + minutes/60 + seconds/3600)
				elif longitude.count("-")==1:
					longitude = longitude.split("-")[0]
				elif longitude.count(".")==2 and longitude.count("-")==0:
					degree, minutes, seconds = map(float,longitude.split("."))
					longitude = str(degree + minutes/60 + seconds/3600)

				# fix hemispheres to coordinates
				lat_hemi = lat_hemi.replace(",","")
				if lat_hemi=="S":
					latitude = "-"+latitude
				if long_hemi=="W":
					longitude = "-"+longitude

	#SRA173038	MLAC_113_031008BA01	SRS650331	433733	human lung metagenome	15.7861A??A?? S, 35.0058A??A?? E	21-Sep-2010	NA	Malawi: Blantyre	human lung metagenome

				# check for further weird cases
	#SRA134133	29	SRS564079	662107	phyllosphere metagenome	36A? 37.669, -121A? 32.350	2012	NA	USA: Salinas Valley	phyllosphere metagenome
				if lat_hemi not in ["N", "S"]:
					non_nsew_counter += 1
					bad_latlon = True

				# remove terminal ? for cases below
	#SRA074245	LM300	SRS1239132	410658	soil metagenome	45.5081? N, 73.5550? W	2011-06-15	NA	Canada: Montreal	soil metagenome
				if latitude and latitude[-1]=="?":
					latitude = latitude.replace("?","")
				if longitude and longitude[-1]=="?":
					longitude = longitude.replace("?","")

	#SRA189798	LAO-D49	SRS720730	527639	wastewater metagenome	49.5134139 N 0.006.0179250 E	10/5/11	NA	Luxembourg: Schifflange	wastewater metagenome
				if longitude.find("0.006")==0:
					longitude = longitude.replace("0.00","")

			# for entries with weird splits
			elif len(latlonsp) == 2:
				latitude, longitude = two_part_latlon(raw_latlon)
				if latitude is None:
					non_nsew_counter += 1
					bad_latlon = True
				else:
					two_part_fix += 1
			elif len(latlonsp) == 6:
				latitude, longitude = six_part_latlon(raw_latlon)
				if latitude is None:
					non_nsew_counter += 1
					bad_latlon = True
				else:
					six_part_fix += 1
			elif len(latlonsp) == 1:
				latitude, longitude = one_part_latlon(raw_latlon)
				if latitude is None:
					non_nsew_counter += 1
					bad_latlon = True
				else:
					one_part_fix += 1
			else:
				non_nsew_counter += 1
				bad_latlon = True

			if bad_latlon is False:
				# check for final errors in 4-part
				latmatch = re.search("^(-?[.\d]+)$", latitude)
				lonmatch = re.search("^(-?[.\d]+)$", longitude)
				if not latmatch or not lonmatch:
					latitude, longitude = four_part_latlon(raw_latlon)
					if latitude is None:
						non_nsew_counter += 1
						bad_latlon = True
					else:
						four_part_fix += 1


		# if using geonames
		if args.geonames_data and args.geonames_countries:
			if has_location_field is True:
				# no latlon given in the first place or is erroneous
				if has_latlon_field is False or bad_latlon is True:
					latitude, longitude, geonames_flag = get_geonames_latlon( location_name, unique_name_to_latlon )
					if latitude is None: # meaning found the latitude
						cannot_find_loc_counter += 1
						continue
					else:
						location_found = True
						match_any_loc_counter += 1
						if geonames_flag is True: # meaning exact match found
							found_exact_location += 1
						else: # flag for country only found
							country_only_names += 1
		else: # no geonames
			if bad_latlon is True or has_latlon_field is False: # could not use latlon and no location given
				continue

		if bad_latlon is True and location_found is False:
			cannot_find_loc_counter += 1
			continue

	

		# fix the date to the same format
		rawdate = lsplits[6]
		fixed_date = fix_date_formats(rawdate)
		if fixed_date=="0000-00-00":
			no_date_counter += 1
		else:
			has_date_counter += 1
		fixed_year = int(fixed_date.split("-")[0])
		if 0000 < fixed_year < 1990 or fixed_year > 2100:
			strange_date += 1
		lsplits[6] = "{}\t{}\t{}".format( *fixed_date.split("-") )

		# reassign split
		lsplits[5] = "{}\t{}".format(latitude, longitude)
		# print line
		print_count += 1
		sys.stdout.write( "\t".join(lsplits) )


	# count fixes of non standard formats
	weird_fixes = one_part_fix + two_part_fix + four_part_fix + six_part_fix



	# report final latlon stats
	sys.stderr.write("# Counted {} entries, wrote {} entries\n".format(entry_count, print_count) )
	sys.stderr.write("# {}/{} entries had either latlon position or location\n".format(any_source_position, entry_count) )
	sys.stderr.write("# {}/{} entries had no latlon position or location given\n".format(no_source_position_given, entry_count) )
	print( "#" , file=sys.stderr )
	# based on latlon info
	if void_counter:
		sys.stderr.write("# {} entries had 'VOID' as lat-lon from previous steps, removed\n".format(void_counter) )
	if missing_latlon_counter:
		sys.stderr.write("# {} entries did not include lat-lon (missing, not collected, etc.), removed\n".format(missing_latlon_counter) )
	if nc_counter:
		sys.stderr.write("# {} entries had other values as lat-lon, removed\n".format(nc_counter) )
	if non_nsew_counter:
		sys.stderr.write("# {} entries had an unknown format of lat-lon, removed\n".format(non_nsew_counter) )
	if dms_counter:
		sys.stderr.write("# {} entries had lat-lon as deg-min-sec format, fixed\n".format(dms_counter) )
	if range_counter:
		sys.stderr.write("# {} entries had lat-lon as a range, fixed\n".format(range_counter) )
	if weird_fixes:
		sys.stderr.write("# {} entries had unusual formats, fixed\n".format(weird_fixes) )
	print( "#" , file=sys.stderr )

	# report location stats
	if loc_na_counter:
		sys.stderr.write("# {} entries had 'NA' as location from previous steps\n".format(loc_na_counter) )
	if missing_loc_counter:
		sys.stderr.write("# {} entries had other (missing) values as lat-lon\n".format(missing_loc_counter) )
	if no_location_counter:
		sys.stderr.write("# {} entries had a blank location\n".format(no_location_counter) )
	if loc_field_counter:
		sys.stderr.write("# {}/{} total samples had a valid location given\n".format(loc_field_counter, entry_count) )
	if match_any_loc_counter:
		sys.stderr.write("# {} entries had no lat-lon, but found something from geonames\n".format(match_any_loc_counter) )
	if country_only_names:
		sys.stderr.write("# {} entries had no lat-lon, but found only country ID from geonames\n".format(country_only_names) )
	if cannot_find_loc_counter:
		sys.stderr.write("# {} entries had a location, but the latlon could not be determined\n".format(cannot_find_loc_counter) )
	print( "#" , file=sys.stderr )

	# report date stats
	if has_date_counter:
		sys.stderr.write("# {} entries had acceptable date format, {} were missing date\n".format( has_date_counter, no_date_counter ) )
	if strange_date:
		sys.stderr.write("# {} entries had improbable sample dates (before 1990)\n".format(strange_date) )


if __name__ == "__main__":
	main(sys.argv[1:], sys.stdout)
