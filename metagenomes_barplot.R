#!/usr/bin/env Rscript
# make barplot of common metagenome types
# v1 created by WRF 2019-09-16

args = commandArgs(trailingOnly=TRUE)

inputfile = args[1]
#inputfile = "~/git/misc-analyses/taxonomy_database/NCBI_SRA_Metadata_Full_20181203.metagenomes.tab"
#inputfile = "~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20200924.metagenomes_ext.tab"
#inputfile = "~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20210404.metagenomes.tab"
outputfile = gsub("([\\w/]+)\\....$","\\1.pdf",inputfile,perl=TRUE)

print(paste("Reading",inputfile,Sys.time()))
taxondata_raw = read.table(inputfile, header=FALSE, sep="\t")
print(paste("Done reading from file",Sys.time()))

if ( dim(taxondata_raw)[2] > 1 ) {
	print(paste("Detected extended format, using column",dim(taxondata_raw)[2],Sys.time()))
}
taxondata = taxondata_raw[,dim(taxondata_raw)[2]]

# remove items that are None, as those have actual species
taxondata_filt = taxondata[taxondata!="None"]
taxondata_rename = sub(" metagenome", "", taxondata_filt)

metagenomes = sort(table(taxondata_rename),decreasing=FALSE)
#metagenomes

xmax = max(metagenomes)

num_meta = length(metagenomes)

# set up color categories
humancols = c("human", "human oral", "human nasopharyngeal", "human skin", "human vaginal", "human reproductive system", "human lung", "human milk", "human blood", "human tracheal", "human saliva", "human eye", "human bile", "human sputum", "human semen", "human skeleton", "human urinary tract", "human brain","human viral")
gutscols = c("gut", "feces", "human gut", "human feces", "mouse gut", "rat gut", "bovine gut", "pig gut", "sheep gut", "chicken gut", "insect gut", "fish gut", "invertebrate gut", "shrimp gut", "termite gut")
miscbodycols = c("skin", "lung", "stomach", "vaginal", "oral", "milk", "respiratory tract", "upper respiratory tract", "oral-nasopharyngeal", "urogenital", "reproductive system", "placenta", "urine", "eye", "blood", "liver", "internal organ", "semen", "urinary tract", "granuloma", "ear")
mar_animalcols = c("coral", "coral reef", "fish", "gill", "sponge", "crustacean", "crab", "mollusc", "oyster", "marine plankton", "sea anemone", "jellyfish", "hydrozoan", "echinoderm", "starfish", "sea urchin", "zebrafish", "sea squirt", "cetacean", "annelid", "ctenophore", "egg")
ter_animalcols = c("primate", "mouse", "mouse skin", "rat", "rodent", "shrew", "bat", "canine", "feline", "bovine", "ovine", "sheep", "pig", "horse", "musk", "marsupial", "koala", "frog", "amphibian", "bird", "snake", "insect", "insect nest", "honeybee", "wasp", "tick", "mite", "ant", "mosquito", "spider", "beetle", "termite", "termitarium", "invertebrate", "nematode", "parasite", "whole organism")
plantcols = c("plant", "rhizosphere", "root", "rhizoplane", "phyllosphere", "leaf", "leaf litter", "root associated fungus", "hyphosphere", "wood decay", "compost", "pollen", "seed", "tobacco", "flower", "floral nectar", "tree", "moss", "phytotelma", "ant fungus garden", "shoot", "psyllid", "termite fungus garden", "plant fiber")
algaecols = c("algae", "dinoflagellate", "macroalgae", "seagrass", "phycosphere", "periphyton")
saltwatercols = c("seawater", "marine", "estuary", "hydrothermal vent", "cold seep")
watercols = c("freshwater", "aquatic", "groundwater", "rock porewater", "aquifer", "lake water", "pond", "lagoon", "oasis", "riverine", "tidal flat", "wetland", "hot springs", "cold spring", "salt marsh", "rice paddy", "mangrove", "soda lake", "salt lake", "hypersaline lake", "saline spring", "saltern", "brine", "ice", "snow", "glacier", "glacier lake", "permafrost", "anchialine")
earthcols = c("soil", "soil crust", "terrestrial", "rock", "sediment", "marine sediment", "freshwater sediment", "alkali sediment", "subsurface", "sand", "beach sand", "peat", "bog", "halite", "volcano", "stromatolite", "cave", "fossil", "mud", "hypolithon", "clay", "bentonite")
industcols = c("wastewater", "bioreactor", "fermentation", "retting", "activated sludge", "anaerobic digester", "sludge", "bioreactor sludge", "decomposition", "biogas fermenter", "cow dung", "manure", "biofilter", "silage", "mine", "mine drainage", "mine tailings", "landfill", "industrial waste", "solid waste", "bioleaching", "biosolids", "poultry litter", "soda lime", "activated carbon", "drinking water", "salt mine", "salt pan", "fertilizer", "biofloc", "ballast water", "interstitial water", "aquaculture", "chemical production", "runoff")
petrolcols = c("hydrocarbon", "oil", "crude oil", "oil field", "oil sands", "oil production facility", "gas well", "fuel tank", "coal", "tar pit", "shale gas")
electriccols = c("microbial fuel cell", "bioanode", "biocathode", "electrolysis cell")
citycols = c("indoor", "dust", "urban", "hospital", "clinical", "surface", "money", "steel", "factory", "concrete", "paper pulp", "painting", "parchment", "HVAC", "museum specimen", "medical device", "tomb wall", "book", "power plant")
aircols = c("air", "aerosol", "outdoor", "cloud")
microbecols = c("biofilm", "fungus", "endophyte", "microbial mat", "mixed culture", "viral", "symbiont", "epibiont", "lichen", "lichen crust", "aquatic viral", "eukaryotic plankton", "ciliate", "ecological", "ecologicals", "eukaryotic", "microbial eukaryotic", "organismals")
foodcols = c("food", "food production", "food fermentation", "honey", "wine", "probiotic", "dietary supplements", "grain", "food contamination", "herbal medicine")
plasticcols = c("plastisphere", "plastic", "flotsam", "nutrient bag")
synthcols = c("synthetic")
unclasscols = c("metagenome", "metagenomes")


# take only top 100 out of 250 or so
top100 = metagenomes[(num_meta-99):num_meta]

# reassign colors, default is gray
colorvec = rep("#989898", length(top100))
colorvec[match(humancols, names(top100))] = "#bf04a7"
colorvec[match(gutscols, names(top100))] = "#ed9aea"
colorvec[match(miscbodycols, names(top100))] = "#bf04a7"
colorvec[match(mar_animalcols, names(top100))] = "#9354cf"
colorvec[match(ter_animalcols, names(top100))] = "#d10b0b"
colorvec[match(plantcols, names(top100))] = "#18d025"
colorvec[match(algaecols, names(top100))] = "#18d025"
colorvec[match(saltwatercols, names(top100))] = "#45c5f4"
colorvec[match(watercols, names(top100))] = "#45c5f4"
colorvec[match(earthcols, names(top100))] = "#8e8662"
colorvec[match(industcols, names(top100))] = "#7c4e0d"
colorvec[match(petrolcols, names(top100))] = "#7c4e0d"
colorvec[match(electriccols, names(top100))] = "#fed976"
# citycols stay gray
colorvec[match(aircols, names(top100))] = "#6cbd96"
colorvec[match(microbecols, names(top100))] = "#de851b"
colorvec[match(foodcols, names(top100))] = "#de851b"
# plasticcols stay gray
# synthcols stay gray


# check for new categories with each db iteration
all_categories = c(humancols, gutscols, miscbodycols, mar_animalcols, ter_animalcols, plantcols, algaecols, saltwatercols, watercols, earthcols, industcols, petrolcols, electriccols, citycols, aircols, microbecols, foodcols, plasticcols, synthcols, unclasscols)
not_found_categories = is.na( match( names(metagenomes), all_categories ) )
new_categories = names(metagenomes)[not_found_categories]
if (length(new_categories) > 0){new_categories}


# break into two halves, for main and sub graphs
top50 = top100[51:100]
bottom50 = top100[1:50]

# draw graph
print(paste("Generating .pdf",outputfile))
pdf(file=outputfile, width=8, height=11)
par(mar=c(4,10,2,1.6))
bp1 = barplot(top50, horiz=TRUE, las=1, xlim=c(0,xmax), col=colorvec[51:100], main=inputfile, cex.lab=0.7, cex.axis=1.3)
mg_positions = top50/2
mg_positions[top50<xmax*0.1] = top50[top50<xmax*0.1]+xmax*0.05
text(mg_positions, bp1[,1], top50, cex=0.8) # draws numbers next to bars
text(xmax,bp1[1,1]-1, paste("Total:",sum(metagenomes)), cex=1.5, pos=2)

par(fig = c(grconvertX(c(xmax*0.6,xmax), from="user", to="ndc"), grconvertY(c(0,0.9)*max(bp1), from="user", to="ndc")), mar = c(0,0,0,0), new = TRUE)
bp2 = barplot(bottom50, horiz=TRUE, las=1, xlim=c(0,xmax/2), col=colorvec[1:50], cex.lab=0.6, axes=FALSE)
mg2_pos = bottom50
mg2_pos[mg2_pos>xmax/2] = mg2_pos[mg2_pos>xmax/2]/3
text(mg2_pos, bp2, bottom50, pos=4, cex=0.9) # draws numbers next to bars

dev.off()






#

