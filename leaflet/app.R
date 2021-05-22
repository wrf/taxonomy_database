# sra/leaflet/app.R
# make interactive map of SRA metagenomic samples
# created by WRF 2021-04-11
# last updated 2021-05-17

library(shiny)
library(leaflet)
library(dplyr)
library(DT)

# current host of this file at:
# https://bitbucket.org/wrf/subsurface2017/downloads/
inputfilename = "~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20210404.metagenomes_latlon-fixed.h100k.tab"
#inputfilename = "~/git/taxonomy_database/NCBI_SRA_Metadata_Full_20210404.metagenomes_latlon-fixed.tab"

# v1 headers          1              2               3             4                 5              6           7
mgd_colunm_headers = c("sra_sample", "sample_alias", "accession", "ncbi_id", "ncbi_category","latitude","longitude",
                   "year","month","day", "isolation_source", "location", "category")
#                   8       9       10         11              12           13
# v2 headers
mgd_colunm_headers = c("sra_sample", "sample_alias", "accession", "ncbi_id", "ncbi_category","latitude","longitude",
                       "year","month","day", "isolation_source", "location", 
                       "seq_type", "seq_source", "seq_selection", "category")

print(paste("# Reading", inputfilename))
metagenomedata = read.table(inputfilename, header=FALSE, sep="\t", stringsAsFactors=FALSE, col.names=mgd_colunm_headers )
print(paste("# File contains", dim(metagenomedata)[1], "items with", dim(metagenomedata)[2], "columns"))

metagenome_type = metagenomedata[["category"]]

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

# determine colors for all points
print( "# Assigning colors to categories" )
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
#colorvec_trans = paste0(colorvec,"44") # transparency is handled by leaflet


# establish some values for downstream processing
all_categories = c(humancols, gutscols, miscbodycols, mar_animalcols, ter_animalcols, plantcols, algaecols, saltwatercols, watercols, earthcols, industcols, petrolcols, electriccols, citycols, aircols, microbecols, foodcols, plasticcols, synthcols, unclasscols)
metagenome_cat_table = table(metagenome_type)
not_found_categories = is.na( match( names(metagenome_cat_table), all_categories ) )
new_categories = names(metagenome_cat_table)[not_found_categories]
if (length(new_categories) > 0){new_categories}

# get number of items per category
all_categories_list = list(humancols, gutscols, miscbodycols, mar_animalcols, ter_animalcols, plantcols, algaecols, saltwatercols, watercols, earthcols, industcols, petrolcols, electriccols, citycols, aircols, microbecols, foodcols, plasticcols, synthcols, unclasscols)
items_per_cat = unlist(lapply(all_categories_list,length))
# assign numbers for each category to all metagenomes
all_cat_numerical_values = rep( seq(1,length(all_categories_list),1), items_per_cat)
#metagenome_type_code = all_cat_numerical_values[match(metagenome_type,all_categories)]

print( "# Building point popup labels" ) # unsure why this takes so long
# should end up looking like
# "<b><a href='https://www.ncbi.nlm.nih.gov/sra/SRS5092595'>SRS5092595</a></b>"
sra_expt_address_string = paste0("<b><a href='https://www.ncbi.nlm.nih.gov/sra/", 
                                 metagenomedata[["accession"]] ,"'>", 
                                 metagenomedata[["accession"]] , "</a></b>")
# should look like "2017-3-0"
sample_date_string = paste(metagenomedata[["year"]], metagenomedata[["month"]], 
                           metagenomedata[["day"]], sep="-")
sra_labels <- paste(sep = "<br/>",
                    sra_expt_address_string,
                    sample_date_string,
                    metagenomedata[["ncbi_category"]],
                    metagenomedata[["isolation_source"]],
                    metagenomedata[["location"]]
                    )

# add color vector and labels as columns
metagenomedata = cbind(metagenomedata, colorvec, sra_labels)

#
seq_lib_types = names(sort(table(taxondata_raw[,10]), decreasing=TRUE))
seq_lib_types_choices = c("All types", seq_lib_types )
#
seq_lib_sources = names(sort(table(taxondata_raw[,11]), decreasing=TRUE) )
seq_lib_sources_choices = c("All sources", seq_lib_sources )
#



print( "# Starting user interface" )
# begin actual shiny code
ui <- fluidPage(

  titlePanel("NCBI SRA Metagenomic Samples"),
  
  # Sidebar layout with input and output definitions ----
  verticalLayout(
    fluidRow(
      column(4,
             radioButtons("tileset", h3("Map Tile Set"),
                          choices = list("Esri.WorldTopoMap (topography)" = "esritopo",
                                         "Esri.WorldImagery (satellite)" = "esrisatellite",
                                         "Esri.OceanBasemap" = "esriocean",
                                         "TonerLite (gray)" = "tonerlite")
                         ),
             h4("Overlay options for satellite view"),
             checkboxInput("lineoverlay", "Border overlay", value = FALSE),
             checkboxInput("nameoverlay", "Placename overlay", value = FALSE),
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
                                               "Aquatic animals" = 4, "Terrestrial animals" = 5, 
                                               "Plants" = 6,
                                               "Algae" = 7),
                                selected = 7
                                ),
             selectInput("libtype", "Library Type (Amplicon, WGS, etc.)", 
                         choices = seq_lib_types_choices
                        )
             ),
      column(2, 
             checkboxGroupInput("cats2", "",
                                choices = list("Ocean waters" = 8, "Fresh waters or ice" = 9, 
                                               "Earth (any)" = 10, "Industrial process" = 11, 
                                               "Oil and gas" = 12,
                                               "Electrical process" = 13)
                               ),
             selectInput("libsource", "Library Source (Metagenome, Metatxome, etc.)", 
                         choices = seq_lib_sources_choices
                        )
             ),
      column(2, 
             checkboxGroupInput("cats3", "",
                                choices = list("City environment" = 14, "Air" = 15,
                                               "Microbial process" = 16, "Food" = 17, 
                                               "Plastic" = 18, "Synthetic" = 19, 
                                               "Unclassified" = 20)
                               )
             )
    ),

    # Main panel for displaying outputs ----
    mainPanel(width=12,
      h3("Each point is a sample, click to display stats, Shift+click+drag to zoom"),
      leafletOutput(outputId = "worldMap", height=700),
      verbatimTextOutput(outputId = "debug"), 
      h3("Selected sub-categories:"),
      verbatimTextOutput(outputId = "catInfo"), 
      # verbatimTextOutput(outputId = "mapBounds"), 
      h3("Samples in current view, zoom to change or filter"),
      dataTableOutput("sampleInfo")
    #  
    ) # end mainPanel
    
  ) # end verticalLayout
) # end fluidPage

#
server <- function(input, output) {
  #output$debug <- renderText({ unlist(input$worldMap_bounds) })
  #output$debug <- renderText({  })
  
  get_tileset_choice = reactive({
    if (input$tileset == "tonerlite") {
      providers$Stamen.TonerLite }
    else if (input$tileset == "esriocean") {
      providers$Esri.OceanBasemap }
    else if (input$tileset == "esrisatellite") {
      providers$Esri.WorldImagery }
    else { providers$Esri.WorldTopoMap }
  })
  
  # reactive function to get category choices and filter dataset
  get_selected_samples = reactive({
    user_selected_values = c( input$cats1, input$cats2, input$cats3 )
    cat_is_selected = !is.na(match(all_cat_numerical_values,user_selected_values))
    selected_cats = all_categories[cat_is_selected]
    year_range = input$year[1]:input$year[2]
    if (input$libtype == "All types") {
      lib_type_selected = seq_lib_types
    } else {lib_type_selected = input$libtype}
    if (input$libsource == "All sources") {
      lib_source_selected = seq_lib_sources
    } else {lib_source_selected = input$libsource}
    selected_samples = dplyr::filter(metagenomedata, category %in% selected_cats &
                                       year %in% year_range &
                                       seq_type %in% lib_type_selected &
                                       seq_source %in% lib_source_selected )
  })
  
  # display table() of total samples per category
  output$catInfo <- renderPrint({ table(get_selected_samples()$category ) })
  
  # draw map
  output$worldMap <- renderLeaflet({
    leaflet( options=leafletOptions( minZoom=2, worldCopyJump=TRUE ) ) %>% 
      setView(lng=0, lat=35, zoom=4) %>% 
      addProviderTiles( get_tileset_choice() ) %>%
      addScaleBar("bottomright")
  })
  
  # observer for categories of points
  observe({
    selected_samples = get_selected_samples()
    leafletProxy("worldMap", data=selected_samples) %>%
      clearMarkers() %>%
      addCircleMarkers(lng=selected_samples$longitude , lat=selected_samples$latitude ,
                       stroke=FALSE, fillOpacity=0.25,
                       fillColor= selected_samples$colorvec ,
                       popup = selected_samples$sra_labels
                       )
  }) # end observe

  # observer for border and road overlay
  observe({
    if ( input$lineoverlay==TRUE ) {
      leafletProxy("worldMap", data=NULL) %>%
        removeTiles(layerId="overlaylines") %>%
        addProviderTiles(providers$Stamen.TonerLines, layerId="overlaylines",
                         options = providerTileOptions(opacity = 0.9) )
    } else {
      leafletProxy("worldMap", data=NULL) %>%
        removeTiles(layerId="overlaylines")
    }
  })
  # observer for place label overlay
  observe({
    if ( input$nameoverlay==TRUE ) {
      leafletProxy("worldMap", data=NULL) %>%
        removeTiles(layerId="overlaylabs") %>%
        addProviderTiles(providers$Stamen.TonerLabels, layerId="overlaylabs",
                         options = providerTileOptions(opacity = 0.5) )
    } else {
      leafletProxy("worldMap", data=NULL) %>%
        removeTiles(layerId="overlaylabs")
    }
  })

  # create DataTable of samples that are on screen
  output$sampleInfo <- renderDataTable({
    selected_samples = get_selected_samples() %>%
      dplyr::filter( input$worldMap_bounds$north >= latitude &
                       latitude >= input$worldMap_bounds$south &
                       input$worldMap_bounds$east >= longitude &
                       longitude >= input$worldMap_bounds$west ) %>%
      dplyr::select( sra_sample:accession,ncbi_category:seq_source )

    DT::datatable(selected_samples, options = list(lengthMenu = c(50,100,500), pageLength = 50))
  })
}

# Create Shiny app ----
shinyApp(ui = ui, server = server)

