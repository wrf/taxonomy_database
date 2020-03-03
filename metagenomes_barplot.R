#!/usr/bin/env Rscript
# make barplot of common metagenome types
# v1 created by WRF 2019-09-16

args = commandArgs(trailingOnly=TRUE)

inputfile = args[1]
#inputfile = "~/git/misc-analyses/taxonomy_database/NCBI_SRA_Metadata_Full_20181203.metagenomes.tab"
outputfile = gsub("([\\w/]+)\\....$","\\1.pdf",inputfile,perl=TRUE)

print(paste("Reading",inputfile,Sys.time()))
taxondata = read.table(inputfile, header=FALSE, sep="\t")
print(paste("Done",Sys.time()))

# remove items that are None, as those have actual species
taxondata_filt = taxondata[taxondata!="None"]
taxondata_rename = sub(" metagenome", "", taxondata_filt)

metagenomes = sort(table(taxondata_rename),decreasing=FALSE)
#metagenomes

xmax = max(metagenomes)

num_meta = length(metagenomes)

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

# take only top 100 out of 250 or so
top100 = metagenomes[(num_meta-99):num_meta]

# reassign colors, default is gray
colorvec = rep("#989898", length(top100))
colorvec[match(humancols, names(top100))] = "#bf04a7"
colorvec[match(gutscols, names(top100))] = "#ed9aea"
colorvec[match(mar_animalcols, names(top100))] = "#9354cf"
colorvec[match(ter_animalcols, names(top100))] = "#d10b0b"
colorvec[match(plantcols, names(top100))] = "#18d025"
colorvec[match(watercols, names(top100))] = "#45c5f4"
colorvec[match(earthcols, names(top100))] = "#8e8662"
colorvec[match(industcols, names(top100))] = "#7c4e0d"
colorvec[match(aircol, names(top100))] = "#6cbd96"
colorvec[match(microbecols, names(top100))] = "#de851b"

# break into two halves, for main and sub graphs
top50 = top100[51:100]
bottom50 = top100[1:50]

# draw graph
print(paste("Generating .pdf",outputfile))
pdf(file=outputfile, width=8, height=11)
par(mar=c(4,10,2,1.6))
bp1 = barplot(top50, horiz=TRUE, las=1, xlim=c(0,xmax), col=colorvec[51:100], main=inputfile, cex.lab=1.1, cex.axis=1.3)
mg_positions = top50/2
mg_positions[top50<xmax*0.1] = top50[top50<xmax*0.1]+xmax*0.05
text(mg_positions, bp1[,1], top50, cex=0.8)
text(xmax,bp1[1,1]-1, paste("Total:",sum(metagenomes)), cex=1.5, pos=2)

par(fig = c(grconvertX(c(xmax*0.6,xmax), from="user", to="ndc"), grconvertY(c(0,0.85)*max(bp1), from="user", to="ndc")), mar = c(0,0,0,0), new = TRUE)
bp2 = barplot(bottom50, horiz=TRUE, las=1, xlim=c(0,xmax/2), col=colorvec[1:50], cex.lab=1.1, axes=FALSE)
mg2_pos = bottom50
mg2_pos[mg2_pos>xmax/2] = mg2_pos[mg2_pos>xmax/2]/3
text(mg2_pos, bp2, bottom50, pos=4, cex=0.9)

dev.off()






#