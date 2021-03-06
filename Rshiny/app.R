# sra/app.R
# make interactive map of SRA metagenomic samples
# created by WRF 2020-11-05

library(shiny)
library(maps)

# current host of this file at:
# https://bitbucket.org/wrf/subsurface2017/downloads/
inputfilename = "~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20200924.metagenomes_latlon-fixed.tab"

#                  1              2               3             4                 5              6           7
mgd_colunm_headers = c("sra_sample", "sample_alias", "accession", "ncbi_id", "ncbi_category","latitude","longitude",
                   "year","month","day", "isolation_source", "location", "category")
#                   8       9       10         11              12           13

#print(paste("# Reading", inputfilename))
metagenomedata = read.table(inputfilename, header=FALSE, sep="\t", stringsAsFactors=FALSE, col.names=mgd_colunm_headers )
#print(paste("# File contains", dim(metagenomedata)[1], "items with", dim(metagenomedata)[2], "columns"))

# pull sorting variables from datatable
meta_latitude = as.numeric(metagenomedata[["latitude"]])
meta_longitude = as.numeric(metagenomedata[["longitude"]])
meta_year = as.integer(metagenomedata[["year"]])

# remove the word metagenome from the categories
metagenome_type = sub(" metagenome", "", metagenomedata[["category"]])

# set up color categories
humancols = c("human", "human oral", "human nasopharyngeal", "human skin", "human vaginal", "human reproductive system", "human lung", "human milk", "human blood", "human tracheal", "human saliva", "human eye", "human bile", "human sputum", "human semen", "human skeleton", "human urinary tract")
gutscols = c("gut", "feces", "human gut", "mouse gut", "rat gut", "bovine gut", "pig gut", "sheep gut", "chicken gut", "insect gut", "fish gut", "invertebrate gut", "shrimp gut", "termite gut")
miscbodycols = c("skin", "lung", "stomach", "vaginal", "oral", "milk", "respiratory tract", "upper respiratory tract", "oral-nasopharyngeal", "urogenital", "reproductive system", "placenta", "urine", "eye", "blood", "liver", "internal organ", "semen", "urinary tract")
mar_animalcols = c("coral", "coral reef", "fish", "gill", "sponge", "crustacean", "crab", "mollusc", "oyster", "marine plankton", "sea anemone", "jellyfish", "echinoderm", "starfish", "sea urchin", "zebrafish", "sea squirt", "cetacean", "annelid", "ctenophore", "egg")
ter_animalcols = c("primate", "mouse", "mouse skin", "rat", "rodent", "shrew", "bat", "canine", "feline", "bovine", "ovine", "sheep", "pig", "marsupial", "koala", "frog", "amphibian", "bird", "snake", "insect", "insect nest", "honeybee", "tick", "mite", "ant", "mosquito", "spider", "beetle", "termite", "termitarium", "invertebrate", "nematode", "parasite", "whole organism")
plantcols = c("plant", "rhizosphere", "root", "rhizoplane", "phyllosphere", "leaf", "leaf litter", "root associated fungus", "hyphosphere", "wood decay", "compost", "pollen", "seed", "tobacco", "flower", "floral nectar", "tree", "moss", "phytotelma", "ant fungus garden", "shoot", "psyllid")
algaecols = c("algae", "dinoflagellate", "macroalgae", "seagrass", "phycosphere")
saltwatercols = c("seawater", "marine", "estuary", "hydrothermal vent", "cold seep")
watercols = c("freshwater", "aquatic", "groundwater", "rock porewater", "aquifer", "lake water", "pond", "lagoon", "oasis", "riverine", "tidal flat", "wetland", "hot springs", "cold spring", "salt marsh", "rice paddy", "mangrove", "soda lake", "salt lake", "hypersaline lake", "saline spring", "saltern", "brine", "ice", "snow", "glacier", "glacier lake", "permafrost", "anchialine")
earthcols = c("soil", "soil crust", "terrestrial", "rock", "sediment", "marine sediment", "freshwater sediment", "alkali sediment", "subsurface", "sand", "beach sand", "peat", "bog", "halite", "volcano", "stromatolite", "cave", "fossil", "mud", "hypolithon", "clay")
industcols = c("wastewater", "bioreactor", "fermentation", "retting", "activated sludge", "anaerobic digester", "sludge", "bioreactor sludge", "decomposition", "biogas fermenter", "cow dung", "manure", "biofilter", "silage", "mine", "mine drainage", "mine tailings", "landfill", "industrial waste", "solid waste", "bioleaching", "biosolids", "poultry litter", "soda lime", "activated carbon", "drinking water", "salt mine", "salt pan", "fertilizer", "biofloc", "ballast water", "interstitial water", "aquaculture")
petrolcols = c("hydrocarbon", "oil", "crude oil", "oil field", "oil sands", "oil production facility", "gas well", "fuel tank", "coal", "tar pit", "shale gas")
electriccols = c("microbial fuel cell", "bioanode", "biocathode", "electrolysis cell")
citycols = c("indoor", "dust", "urban", "hospital", "clinical", "surface", "money", "steel", "factory", "concrete", "paper pulp", "painting", "parchment", "HVAC", "museum specimen", "medical device", "tomb wall")
aircols = c("air", "aerosol", "outdoor", "cloud")
microbecols = c("biofilm", "fungus", "endophyte", "microbial mat", "mixed culture", "viral", "symbiont", "epibiont", "lichen", "lichen crust", "aquatic viral", "eukaryotic plankton", "ciliate", "ecologicals", "eukaryotic")
foodcols = c("food", "food production", "food fermentation", "honey", "wine", "probiotic", "dietary supplements", "grain", "food contamination")
plasticcols = c("plastisphere", "plastic", "flotsam")
synthcols = c("synthetic")
unclasscols = c("metagenome")

# determine colors for all points
colorvec = rep("#989898", length(metagenome_type))
colorvec[which(!is.na(match(metagenome_type, humancols)))] = "#bf04a7"
colorvec[which(!is.na(match(metagenome_type, gutscols)))] = "#ed9aea"
colorvec[which(!is.na(match(metagenome_type, miscbodycols)))] = "#bf04a7"
colorvec[which(!is.na(match(metagenome_type, mar_animalcols)))] = "#9354cf"
colorvec[which(!is.na(match(metagenome_type, ter_animalcols)))] = "#d10b0b"
colorvec[which(!is.na(match(metagenome_type, plantcols)))] = "#18d025"
colorvec[which(!is.na(match(metagenome_type, algaecols)))] = "#18d025"
colorvec[which(!is.na(match(metagenome_type, saltwatercols)))] = "#45c5f4"
colorvec[which(!is.na(match(metagenome_type, watercols)))] = "#45c5f4"
colorvec[which(!is.na(match(metagenome_type, earthcols)))] = "#8e8662"
colorvec[which(!is.na(match(metagenome_type, industcols)))] = "#7c4e0d"
colorvec[which(!is.na(match(metagenome_type, petrolcols)))] = "#7c4e0d"
colorvec[which(!is.na(match(metagenome_type, electriccols)))] = "#fed976"
# citycols stay gray
colorvec[which(!is.na(match(metagenome_type, aircols)))] = "#6cbd96"
colorvec[which(!is.na(match(metagenome_type, microbecols)))] = "#de851b"
colorvec[which(!is.na(match(metagenome_type, foodcols)))] = "#de851b"
# plasticcols stay gray
# synthcols stay gray
# unclass stay gray
colorvec_trans = paste0(colorvec,"44")

# establish some values for downstream processing
#
all_categories = c(humancols, gutscols, miscbodycols, mar_animalcols, ter_animalcols, plantcols, algaecols, saltwatercols, watercols, earthcols, industcols, petrolcols, electriccols, citycols, aircols, microbecols, foodcols, plasticcols, synthcols, unclasscols)
# get number of items per category
all_categories_list = list(humancols, gutscols, miscbodycols, mar_animalcols, ter_animalcols, plantcols, algaecols, saltwatercols, watercols, earthcols, industcols, petrolcols, electriccols, citycols, aircols, microbecols, foodcols, plasticcols, synthcols, unclasscols)
items_per_cat = unlist(lapply(all_categories_list,length))
# assign numbers for each category to all metagenomes
all_cat_numerical_values = rep( seq(1,length(all_categories_list),1), items_per_cat)
metagenome_type_code = all_cat_numerical_values[match(metagenome_type,all_categories)]

# Define UI for app that draws a histogram ----
ui <- fluidPage(
  
  # App title ----
  titlePanel("NCBI SRA Metagenomic Samples"),
  
  # Sidebar layout with input and output definitions ----
  verticalLayout(
    
    fluidRow(
      
      column(4,
             sliderInput(inputId = "lat",
                         label = "Latitude",
                         min = -90,
                         max = 90,
                         value = c(-90,90)
                        ),
             sliderInput(inputId = "long",
                         label = "Longitude",
                         min = -180,
                         max = 180,
                         value = c(-180,180)
                        ),
             sliderInput(inputId = "year",
                         label = "Year",
                         min = 1990,
                         max = 2020,
                         value = c(1990,2020),
                         sep=""
             )
             ),
      column(3,
             checkboxGroupInput("cats1", 
                                h3("Metagenome categories"), 
                                choices = list("Human" = 1, "Guts" = 2, "Other body" = 3,
                                               "Aquatic animals" = 4, "Terrestrial animals" = 5, "Plants" = 6,
                                               "Algae" = 7),
                                selected = 7) ),
      column(2, 
             checkboxGroupInput("cats2", "",
                                choices = list("Ocean waters" = 8, "Fresh waters or ice" = 9, 
                                               "Earth (any)" = 10, "Industrial process" = 11, "Oil and gas" = 12,
                                               "Electrical process" = 13),
                               )),
      column(2, 
             checkboxGroupInput("cats3", "",
                                choices = list("City environment" = 14, "Air" = 15,
                                               "Microbial process" = 16, "Food" = 17, "Plastic" = 18,
                                               "Synthetic" = 19, "Unclassified" = 20)
             ))
    ),

    # Main panel for displaying outputs ----
    mainPanel(width=12,
      h3("Each point is a sample. Click and drag over points to display stats"),
      plotOutput(outputId = "worldMap",
                 click = "plot_click",
                 brush = brushOpts(id = "plot_brush")
                 ),
      tableOutput("sampleInfo")
    #  verbatimTextOutput("sampleInfo")
    )
  )
)

#
server <- function(input, output) {

  output$worldMap <- renderPlot({
    # define map bounds from the imputs
    longrange = input$long
    latrange = input$lat
    yearrange = input$year

    # make subset of points
    user_selected_values = c(input$cats1, input$cats2, input$cats3)
    is_selected = which( match(metagenome_type_code, user_selected_values ) & ( meta_year >= yearrange[1] ) & (meta_year <= yearrange[2]) )
    sub_lats = meta_latitude[is_selected]
    sub_longs = meta_longitude[is_selected]
    sub_colors = colorvec_trans[is_selected]
    
    # generate the map
    worldmap = map('world', xlim=longrange, ylim=latrange, fill=TRUE, col="#dedede", mar=c(0.1,0.1,0.1,0.1) )
    lines( input$long, c(0,0), lwd=0.5,col="#00000022")
    lines( c(0,0), input$lat, lwd=0.5,col="#00000022")
    points( sub_longs, sub_lats, bg=sub_colors, pch=21, cex=1.5)
    text(longrange[1], latrange[2]-diff(latrange)*0.01, paste("samples:", length(sub_colors)), pos=4)
  })
  
  output$sampleInfo <- renderTable({
    # make subset of the big table, so only selected categories are brushed over
    user_selected_values = c(input$cats1, input$cats2, input$cats3)
    yearrange = input$year
    is_selected = which( match(metagenome_type_code, user_selected_values ) & ( meta_year >= yearrange[1] ) & (meta_year <= yearrange[2]) )
    sub_table = metagenomedata[is_selected,]

    brushedPoints(sub_table, input$plot_brush, xvar = "longitude", yvar = "latitude")
  },
  hover = TRUE,
  spacing = 'xs',
  width = "100%"
  )
}

# Create Shiny app ----
shinyApp(ui = ui, server = server)

