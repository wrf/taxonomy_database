# metagenomes_map.R
# created by WRF 2020-03-04

library(maps)

inputfilename = "~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon.tab"
metagenomedata = read.table(inputfilename, header=FALSE, sep="\t", stringsAsFactors=FALSE)

# to view sorted table of counts by category
#sort(table(metagenomedata[["V11"]]), decreasing=TRUE)

latitude = metagenomedata[["V6"]]
longitude = metagenomedata[["V7"]]

which(latitude > 90)

# remove metagenome from the name of each
metagenome_type = sub(" metagenome", "", metagenomedata[["V11"]])

# set up color categories
humancols = c("human gut", "human", "human oral", "human skin", "human lung", "human nasopharyngeal", "human vaginal", "human saliva", "human reproductive system", "human blood", "human milk", "human bile", "human tracheal")
gutscols = c("gut", "feces", "mouse gut", "pig gut", "bovine gut", "sheep gut", "fish gut", "chicken gut", "insect gut", "rat gut", "invertebrate gut")
mar_animalcols = c("coral", "sponge", "fish", "oyster", "coral reef", "crustacean", "sea anemone", "echinoderm", "ctenophore", "sea squirt")
ter_animalcols = c("primate", "mouse", "rodent", "marsupial", "insect", "bird", "pig", "ant", "tick", "sheep", "ovine", "bovine", "canine", "feline", "spider", "mosquito", "bat", "mollusc", "spider", "mite", "nematode")
plantcols = c("rhizosphere", "plant", "root", "phyllosphere", "leaf", "flower", "leaf litter", "wood decay", "algae", "root associated fungus", "floral nectar")
watercols = c("marine", "freshwater", "aquatic", "seawater", "lake water", "hot springs", "riverine", "wetland", "estuary", "salt lake", "groundwater", "hypersaline lake", "ice", "snow")
earthcols = c("soil", "soil crust", "rock", "sediment", "marine sediment", "freshwater sediment", "peat", "beach sand", "terrestrial", "bog", "volcano")
industcols = c("bioreactor", "bioreactor sludge", "wastewater", "activated sludge", "sludge", "anaerobic digester", "hydrocarbon", "manure", "fermentation", "bioreactor sludge", "compost", "gas well", "oil", "oil field", "oil sands", "paper pulp", "parchment")
aircol = c("air", "dust", "indoor", "urban", "aerosol", "cloud")
microbecols = c("viral", "biofilm", "fungus", "endophyte", "microbial mat")
plasticcols = c("plastisphere", "plastic", "flotsam")

colorvec = rep("#989898", length(metagenome_type))
colorvec[which(!is.na(match(metagenome_type, humancols)))] = "#bf04a7"
colorvec[which(!is.na(match(metagenome_type, gutscols)))] = "#ed9aea88"
colorvec[which(!is.na(match(metagenome_type, mar_animalcols)))] = "#9354cf"
colorvec[which(!is.na(match(metagenome_type, ter_animalcols)))] = "#d10b0b"
colorvec[which(!is.na(match(metagenome_type, plantcols)))] = "#18d025"
colorvec[which(!is.na(match(metagenome_type, watercols)))] = "#45c5f4"
colorvec[which(!is.na(match(metagenome_type, earthcols)))] = "#8e8662"
colorvec[which(!is.na(match(metagenome_type, industcols)))] = "#7c4e0d"
colorvec[which(!is.na(match(metagenome_type, aircol)))] = "#6cbd96"
colorvec[which(!is.na(match(metagenome_type, microbecols)))] = "#de851b"

# for all categories
# WARNING MAP IS LARGE
#pdf( file="~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon.pdf", height=12, width=24)
#png( file="~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon.png", height=1080, width=2160)
#worldmap = map('world', fill=TRUE, col="#dedede", mar=c(0.1,0.1,0.1,0.1),)
#points( longitude, latitude, bg=colorvec, pch=16, cex=1.5)
#dev.off()


# for individual terms
pdf( file="~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-sponge_only.pdf", height=12, width=24)
worldmap = map('world', fill=TRUE, col="#dedede", mar=c(0.1,0.1,0.1,0.1),)
spongeset = which(!is.na(match(metagenome_type, c("sponge") ) ) )
points( longitude[spongeset], latitude[spongeset], bg="#9354cf88", pch=21, cex=3)
dev.off()

# for categories of terms, above
pdf( file="~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-plant_only.pdf", height=12, width=24)
worldmap = map('world', fill=TRUE, col="#dedede", mar=c(0.1,0.1,0.1,0.1),)
plantset = which(!is.na(match(metagenome_type, plantcols ) ) )
points( longitude[plantset], latitude[plantset], bg="#18d02588", pch=21, cex=3)
dev.off()

# for overlay of multiple categories
pdf( file="~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-sponge_water.pdf", height=12, width=24)
#png( file="~/git/taxonomy_database/images/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-sponge_water.png", height=540, width=1080)
worldmap = map('world', fill=TRUE, col="#dedede", mar=c(0.1,0.1,0.1,0.1),)
waterset = which(!is.na(match(metagenome_type, watercols ) ) )
points( longitude[waterset], latitude[waterset], col="#45c5f488", pch=16, cex=1)
spongeset = which(!is.na(match(metagenome_type, c("sponge") ) ) )
points( longitude[spongeset], latitude[spongeset], bg="#9354cf88", pch=21, cex=3)
legend(-130,-45, legend=c("Sponge", "Any water type"), col=c("#9354cf", "#45c5f4"), pch=16, cex=2)
dev.off()





#