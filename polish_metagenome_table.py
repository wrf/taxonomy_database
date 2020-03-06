#!/usr/bin/env python

# polish_metagenome_table.py

'''polish_metagenome_table.py  last modified 2020-03-06
    tidy up formats, fix lat-long info

polish_metagenome_table.py metagenomes_ext.tab > metagenomes_latlon-fixed.tab

    table generated from parse_ncbi_taxonomy.py, as:
parse_ncbi_taxonomy.py -n names.dmp -o nodes.dmp -i NCBI_SRA_Metadata_Full_20191130.sample_w_cat.tab --metagenomes-only --numbers --samples > NCBI_SRA_Metadata_Full_20191130.metagenomes_w_cat.tab

'''

import sys
import re

def two_part_latlon(latlon, debug=False):
	'''take latlon with any two part split, and return the true latitude and longitude'''

	# cases are given below #
	#########################

	# most basic case
	#55.398487 10.420596
	rematch = re.search("(-?[.\d]+) (-?[.\d]+)", latlon)
	if rematch:
		latitude = "{}".format(rematch.group(1))
		longitude = "{}".format(rematch.group(2))
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
		print >> sys.stderr, latlon
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
		print >> sys.stderr, latlon
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
		print >> sys.stderr, latlon
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

	# appears to have A??A?? as decimal and switched order of EW, NS
	#SRA172986	Zhang_Yang	SRS659936	410658	soil metagenome	116A??A??5927 E, 30A??A??2808 N	Apr 20th and May 25th,2012	NA	Anqing, Anhui	soil metagenome

	#SRA127724	Reduced2	SRS534538	410658	soil metagenome	48?3013.50 N, 11?2650.80 E	26-Nov-2012	NA	Germany: Scheyern	soil metagenome

	# otherwise return None
	if debug:
		print >> sys.stderr, latlon
	return None, None






# BEGIN MAIN CODE BLOCK
##################################################
##################################################


if len(sys.argv) < 2:
	sys.exit( __doc__ )
else:
	# counters for various missing data
	dms_counter = 0
	range_counter = 0
	one_part_fix = 0
	two_part_fix = 0
	four_part_fix = 0
	six_part_fix = 0

	non_nsew_counter = 0
	void_counter = 0
	missing_counter = 0

	# includes typo of 'not availalble' and 'missisng_1'
	missing_variants = ["missing", "Missing", "MISSING", "NA", "N/A", "na", "n/a", "n/A", "NOT APPLICABLE", "Not Applicable", "Not applicable", "not applicable", "not determined", "not recorded", "not collected", "Not collected", "Not Collected", "NOT COLLECTED", "not available", "Not available", "Not Available", "not availalble", "not provided", "Unknown", "unknown", "-", "None", "none", "missisng_1", "missisng_2", "missisng_3", "missisng_4", "NULL", "?", "AE"]

	nc_variants = ["large intestine", "blood", "Vosges", "V5-V9", "Kolkata", "diverse", "bacteria", "Morvan mountains"]
	nc_counter = 0

	entry_count = 0
	print_count = 0
	sys.stderr.write("# Reading {}\n".format(sys.argv[1]) )
	for line in open(sys.argv[1],'r'):
		entry_count += 1

		# basic pattern should split line into 10 columns
#    sample    alias    accession  taxonID   scientific name   lat-lon  date  source  location   sample type
#       0         1          2         3              4           5     6     7        8         9
#SRA191450	112451830	SRS723069	646099	human metagenome	NA	NA	stool	NA	human metagenome
#SRA594737	C2b.24.015	SRS2396010	556182	freshwater sediment metagenome	46.512 N 6.587 E	May-2012	Lake sediment_21	Switzerland: Lake Geneva	freshwater sediment metagenome
		lsplits = line.split("\t")
		raw_latlon = lsplits[5]

		# remove obvious ones
		if raw_latlon=="VOID": # VOID should derive from previous steps
			void_counter += 1
			continue
		if raw_latlon in missing_variants:
			missing_counter += 1
			continue
		if raw_latlon in nc_variants:
			nc_counter += 1
			continue
		if raw_latlon == "":
			missing_counter += 1
			continue

		# lat-lon is generally YY.YY NS XX.XX EW
		# should split into 4 pieces to [YY.YY, NS, XX.XX, EW]
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

#SRA173038	MLAC_113_031008BA01	SRS650331	433733	human lung metagenome	15.7861A??A?? S, 35.0058A??A?? E	21-Sep-2010	NA	Malawi: Blantyre	human lung metagenome

			# check for further weird cases
#SRA134133	29	SRS564079	662107	phyllosphere metagenome	36A? 37.669, -121A? 32.350	2012	NA	USA: Salinas Valley	phyllosphere metagenome
			if lat_hemi not in ["N", "S"]:
				non_nsew_counter += 1
				continue

			# remove terminal ? for cases below
#SRA074245	LM300	SRS1239132	410658	soil metagenome	45.5081? N, 73.5550? W	2011-06-15	NA	Canada: Montreal	soil metagenome
			if latitude[-1]=="?":
				latitude = latitude.replace("?","")
			if longitude[-1]=="?":
				longitude = longitude.replace("?","")

		# for entries with weird splits
		elif len(latlonsp) == 2:
			latitude, longitude = two_part_latlon(raw_latlon)
			if latitude is None:
				non_nsew_counter += 1
				continue
			two_part_fix += 1
		elif len(latlonsp) == 6:
			latitude, longitude = six_part_latlon(raw_latlon)
			if latitude is None:
				non_nsew_counter += 1
				continue
			six_part_fix += 1
		elif len(latlonsp) == 1:
			latitude, longitude = one_part_latlon(raw_latlon)
			if latitude is None:
				non_nsew_counter += 1
				continue
			one_part_fix += 1
		else:
			non_nsew_counter += 1
			continue

		# check for final errors in 4-part
		latmatch = re.search("^(-?[.\d]+)$", latitude)
		lonmatch = re.search("^(-?[.\d]+)$", longitude)
		if not latmatch or not lonmatch:
			latitude, longitude = four_part_latlon(raw_latlon)
			if latitude is None:
				non_nsew_counter += 1
				continue
			four_part_fix += 1

		# reassign split
		lsplits[5] = "{}\t{}".format(latitude, longitude)
		# print line
		print_count += 1
		sys.stdout.write( "\t".join(lsplits) )
	# count fixes of non standard formats
	weird_fixes = one_part_fix + two_part_fix + four_part_fix + six_part_fix

	# report final stats
	sys.stderr.write("# Counted {} entries, wrote {} entries\n".format(entry_count, print_count) )
	if void_counter:
		sys.stderr.write("# {} entries had 'VOID' as lat-lon from previous steps, removed\n".format(na_counter) )
	if missing_counter:
		sys.stderr.write("# {} entries did not include lat-lon (missing, not collected, etc.), removed\n".format(missing_counter) )
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
#
