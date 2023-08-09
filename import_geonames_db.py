#!/usr/bin/env python
#
# import_geonames_db.py  created 2020-10-27

'''import_geonames_db.py  last modified 2022-01-05
    get stats on geonames database

~/git/taxonomy_database/import_geonames_db.py featureCodes_en.txt countryInfo.txt allCountries.txt > geonames_placenames_latlon.tab

    wc geonames_placenames_latlon.tab
  24341155  105196946 1000579979 geonames_placenames_latlon.tab


    download allCountries.zip from
    https://download.geonames.org/export/dump/
'''

import sys
import time
from collections import defaultdict,Counter


column_defs = '''
The main 'geoname' table has the following fields :
---------------------------------------------------
geonameid         : integer id of record in geonames database
name              : name of geographical point (utf8) varchar(200)
asciiname         : name of geographical point in plain ascii characters, varchar(200)
alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
latitude          : latitude in decimal degrees (wgs84)
longitude         : longitude in decimal degrees (wgs84)
feature class     : see http://www.geonames.org/export/codes.html, char(1)
feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
country code      : ISO-3166 2-letter country code, 2 characters
cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80) 
admin3 code       : code for third level administrative division, varchar(20)
admin4 code       : code for fourth level administrative division, varchar(20)
population        : bigint (8 byte int) 
elevation         : in meters, integer
dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
modification date : date of last modification in yyyy-MM-dd format
'''

example_defs = '''
geonameid         2986043
name              Pic de Font Blanca
asciiname         Pic de Font Blanca
alternatenames    Pic de Font Blanca,Pic du Port
latitude          42.64991
longitude         1.53335
feature class     T
feature code      PK
country code      AD
cc2               
admin1 code       00
admin2 code       
admin3 code       
admin4 code       
population        0
elevation         
dem               2860
timezone          Europe/Andorra
modification date 2014-11-05
'''

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


if len(sys.argv)<2:
	sys.exit(__doc__)
else:
	geo_feature_descr_dict = import_geonames_features( sys.argv[1] )
	geo_country_info_dict = import_geonames_country_codes( sys.argv[2] )
	unique_name_to_latlon = import_geonames_all_countries( sys.argv[3] , geo_feature_descr_dict , geo_country_info_dict )

	make_table = True
	if make_table:
		sys.stderr.write("# Writing geonames {}\n".format( make_table ) )
		for k,v in unique_name_to_latlon.items():
			print( "{}\t{}\t{}".format( k,v[0],v[1] ) , file=sys.stdout )

