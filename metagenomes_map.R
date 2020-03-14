# metagenomes_map.R
# created by WRF 2020-03-04

library(maps)

inputfilename = "~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon.tab"
metagenomedata = read.table(inputfilename, header=FALSE, sep="\t", stringsAsFactors=FALSE)

#head(metagenomedata)

# to view sorted table of counts by category
#sort(table(metagenomedata[["V11"]]), decreasing=TRUE)
#table(metagenomedata[["V11"]])

latitude = as.numeric(metagenomedata[["V6"]])
longitude = as.numeric(metagenomedata[["V7"]])

meta_year = metagenomedata[["V8"]]

# table of years of samples
#table(meta_year)

# remove metagenome from the name of each
metagenome_type = sub(" metagenome", "", metagenomedata[["V13"]])


# NOTES on categories
#
# humancols       is defined as all human, excluding gut or feces
# gutscols        is guts from all other animals
# miscbodycols    is undefined organisms, but is treated as human, possibly mislabeled
# mar_animalcols  is marine animals, though includes freshwater animals, and possibly some land
#                 includes some unclear terms: "mollusc" (could be snail/slug?), "annelid" (same), "crustacean" (could be land isopods?)
#                 "marine plankton" (could be any microbe?), "egg" (might be larva or bird eggs?)
# ter_animalcols  is all generic land animal samples, not clearly gut or organ, and most arthropods
#                 includes mouse and rat, which may load it up with laboratory samples
#                 includes 4 ambiguous terms" "invertebrate", "nematode", "parasite", "whole organism"
# plantcols       is plants or plant-related materials, include roots, associated fungi, degradation of plant material
# watercols       is all aquatic habitats, lakes, rivers, and frozen water bodies "ice" "snow" etc
#                 includes "groundwater", "rock porewater", "hydrothermal vent", "cold seep" (could be with earth)
# earthcols       is all land or earth sources
#                 includes some ambiguous terms: "sediment", "marine sediment", "freshwater sediment", "alkali sediment"
#                 "soil" (could be agricultural?), "peat" "bog" (could be aquatic)
# industcols      is anything of manmade processes, environmental cleaning, industrial operations
#                 also includes things related to petrol, fuels
#                 includes "wastewater", "drinking water", "ballast water" (aquatic sources?)
#                 and "cow dung", "manure" (could be with guts?)
# electriccols    effectively a subset of industcols, things explicitly related to electrically active environments
# citycols        is manmade environments, surfaces, and common objects
# aircol          is air and related
# microbecols     is some microbial terms like biofilms or mats, but also microbial interactions
#                 includes some ambiguous terms: "eukaryotic plankton" (could be plant or animal?), "ecological" (no idea)
# foodcols        is specific food processes or foodstuffs
# plasticcols     is just to separate plastics from citycols
# synthcols       is probably experimental/artificial microbial communities

# set up color categories
humancols = c("human", "human oral", "human nasopharyngeal", "human skin", "human vaginal", "human reproductive system", "human lung", "human milk", "human blood", "human tracheal", "human saliva", "human eye", "human bile", "human sputum", "human semen")
gutscols = c("gut", "feces", "human gut", "mouse gut", "rat gut", "bovine gut", "pig gut", "sheep gut", "chicken gut", "insect gut", "fish gut", "invertebrate gut", "shrimp gut", "termite gut")
miscbodycols = c("skin", "lung", "stomach", "vaginal", "oral", "milk", "respiratory tract", "upper respiratory tract", "oral-nasopharyngeal", "urogenital", "reproductive system", "placenta", "urine", "eye", "blood", "liver", "internal organ")
mar_animalcols = c("coral", "coral reef", "fish", "gill", "sponge", "crustacean", "crab", "mollusc", "oyster", "marine plankton", "sea anemone", "jellyfish", "echinoderm", "starfish", "sea urchin", "zebrafish", "sea squirt", "cetacean", "annelid", "ctenophore", "egg")
ter_animalcols = c("primate", "mouse", "mouse skin", "rat", "rodent", "shrew", "bat", "canine", "feline", "bovine", "ovine", "sheep", "pig", "marsupial", "koala", "frog", "amphibian", "bird", "snake", "insect", "insect nest", "honeybee", "tick", "mite", "ant", "mosquito", "spider", "beetle", "termite", "invertebrate", "nematode", "parasite", "whole organism")
plantcols = c("plant", "rhizosphere", "root", "rhizoplane", "phyllosphere", "leaf", "leaf litter", "root associated fungus", "hyphosphere", "wood decay", "compost", "algae", "dinoflagellate", "macroalgae", "seagrass", "pollen", "seed", "tobacco", "flower", "floral nectar", "tree", "moss", "phytotelma", "ant fungus garden", "shoot")
watercols = c("marine", "freshwater", "aquatic", "seawater", "groundwater", "rock porewater", "aquifer", "lake water", "pond", "lagoon", "oasis", "riverine", "estuary", "tidal flat", "wetland", "hot springs", "cold spring", "salt marsh", "rice paddy", "mangrove", "soda lake", "salt lake", "hypersaline lake", "saline spring", "saltern", "brine", "hydrothermal vent", "cold seep", "ice", "snow", "glacier", "glacier lake", "permafrost", "anchialine")
earthcols = c("soil", "soil crust", "terrestrial", "rock", "sediment", "marine sediment", "freshwater sediment", "alkali sediment", "subsurface", "sand", "beach sand", "peat", "bog", "halite", "volcano", "stromatolite", "cave", "fossil", "mud", "hypolithon")
industcols = c("wastewater", "bioreactor", "fermentation", "retting", "activated sludge", "anaerobic digester", "sludge", "bioreactor sludge", "decomposition", "biogas fermenter", "cow dung", "manure", "biofilter", "silage", "hydrocarbon", "oil", "crude oil", "oil field", "oil sands", "oil production facility", "gas well", "fuel tank", "coal", "tar pit", "mine", "mine drainage", "mine tailings", "landfill", "industrial waste", "solid waste", "bioleaching", "biosolids", "poultry litter", "soda lime", "activated carbon", "drinking water", "salt mine", "salt pan", "fertilizer", "biofloc", "ballast water")
electriccols = c("microbial fuel cell", "bioanode", "biocathode", "electrolysis cell")
citycols = c("indoor", "dust", "urban", "hospital", "clinical", "surface", "money", "steel", "factory", "concrete", "paper pulp", "painting", "parchment", "HVAC", "museum specimen")
aircol = c("air", "aerosol", "outdoor", "cloud")
microbecols = c("biofilm", "fungus", "endophyte", "microbial mat", "mixed culture", "viral", "symbiont", "epibiont", "lichen", "lichen crust", "aquatic viral", "eukaryotic plankton", "ciliate", "ecological")
foodcols = c("food", "food production", "food fermentation", "honey", "wine", "probiotic", "dietary supplements", "grain")
plasticcols = c("plastisphere", "plastic", "flotsam")
synthcols = c("synthetic")

# determine colors for all points
colorvec = rep("#989898", length(metagenome_type))
colorvec[which(!is.na(match(metagenome_type, humancols)))] = "#bf04a7"
colorvec[which(!is.na(match(metagenome_type, gutscols)))] = "#ed9aea"
colorvec[which(!is.na(match(metagenome_type, miscbodycols)))] = "#bf04a7"
colorvec[which(!is.na(match(metagenome_type, mar_animalcols)))] = "#9354cf"
colorvec[which(!is.na(match(metagenome_type, ter_animalcols)))] = "#d10b0b"
colorvec[which(!is.na(match(metagenome_type, plantcols)))] = "#18d025"
colorvec[which(!is.na(match(metagenome_type, watercols)))] = "#45c5f4"
colorvec[which(!is.na(match(metagenome_type, earthcols)))] = "#8e8662"
colorvec[which(!is.na(match(metagenome_type, industcols)))] = "#7c4e0d"
colorvec[which(!is.na(match(metagenome_type, electriccols)))] = "#fed976"
# citycols stay gray
colorvec[which(!is.na(match(metagenome_type, aircol)))] = "#6cbd96"
colorvec[which(!is.na(match(metagenome_type, microbecols)))] = "#de851b"
colorvec[which(!is.na(match(metagenome_type, foodcols)))] = "#de851b"
# plasticcols stay gray
# synthcols stay gray



# draw the maps


# for all categories
# WARNING MAP IS LARGE
# DUE TO APPX 600k POINTS
# AND DOES NOT RENDER QUICKLY
#
#pdf( file="~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon.pdf", height=12, width=24)
#png( file="~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon.png", height=1080, width=2160)
#worldmap = map('world', fill=TRUE, col="#ededed", border="#898989", mar=c(0.1,0.1,0.1,0.1) )
#points( longitude, latitude, bg=colorvec, pch=21, cex=1.5)
#dev.off()



# for individual terms
# i.e. any term in the col categories above
pdf( file="~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-sponge_only.pdf", height=12, width=24)
worldmap = map('world', fill=TRUE, col="#ededed", border="#898989", mar=c(0.1,0.1,0.1,0.1) )
spongeset = which(!is.na(match(metagenome_type, c("sponge") ) ) )
points( longitude[spongeset], latitude[spongeset], bg="#9354cf88", pch=21, cex=3)
mtext(paste( length(spongeset), "total samples" ), side=3, cex=3)
dev.off()

# for whole categories of terms, above
pdf( file="~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-plant_only.pdf", height=12, width=24)
worldmap = map('world', fill=TRUE, col="#ededed", border="#898989", mar=c(0.1,0.1,0.1,0.1) )
plantset = which(!is.na(match(metagenome_type, plantcols ) ) )
points( longitude[plantset], latitude[plantset], bg="#18d02588", pch=21, cex=3)
dev.off()

# for overlay of multiple categories
pdf( file="~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-sponge_water.pdf", height=12, width=24)
#png( file="~/git/taxonomy_database/images/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-sponge_water.png", height=540, width=1080)
worldmap = map('world', fill=TRUE, col="#ededed", border="#898989", mar=c(0.1,0.1,0.1,0.1) )
waterset = which(!is.na(match(metagenome_type, watercols ) ) )
points( longitude[waterset], latitude[waterset], col="#45c5f488", pch=16, cex=1)
spongeset = which(!is.na(match(metagenome_type, c("sponge") ) ) )
points( longitude[spongeset], latitude[spongeset], bg="#9354cf88", pch=21, cex=3)
legend(-130,-45, legend=c("Sponge", "Any water type"), col=c("#9354cf", "#45c5f4"), pch=16, cex=2, bty='n')
dev.off()




# make multiple plots, one for each year
#
yearset = c("2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019")
num_years = length(yearset)
for (i in seq(1,num_years)) {
	png_by_year_file = paste0("~/git/taxonomy_database/images/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon.earth-",yearset[i],".png")
	png( file=png_by_year_file, height=500, width=1000)
	worldmap = map('world', fill=TRUE, col="#ededed", border="#898989", mar=c(0.1,0.1,0.1,0.1) )
	# color past years dark
	earthset = which(!is.na(match(metagenome_type, earthcols ) ) & meta_year > 2000 & meta_year < yearset[i] )
	points( longitude[earthset], latitude[earthset], bg="#4e2602", pch=21, cex=1)
	# color current year orange
	earthset = which(!is.na(match(metagenome_type, earthcols ) ) & meta_year==yearset[i] )
	points( longitude[earthset], latitude[earthset], bg="#feb24c", pch=21, cex=1)
	# write samples in current year, and year to the plot
	text(-180,80,paste( length(earthset), "new samples" ), cex=1.5, pos=4)
	text(-180,-80,yearset[i], cex=3, pos=4)
	dev.off()
}

# then run convert from imagemagick
# cd ~/git/taxonomy_database/images/
# convert -delay 90 NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon.earth-20??.png -loop 0 NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon.earth_01-19.gif








#