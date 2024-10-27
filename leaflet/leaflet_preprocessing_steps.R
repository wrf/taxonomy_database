# leaflet_preprocessing_steps.R
# pre processing of the datafile for the interactive map of SRA metagenomic samples
# read flatfile as table and convert to Rds
# created by WRF 2024-10-26

# flatfile, compressed or not
inputfilename = "~/git/taxonomy_database/data/NCBI_SRA_Metadata_Full_20220117.metagenomes_latlon-fixed.tab.gz"
mgd_colunm_headers = c("sra_study_id", "sample_alias", "sra_sample_acc", "ncbi_id", "ncbi_category","latitude","longitude",
                       "year","month","day", "isolation_source", "location", 
                       "seq_type", "seq_source", "seq_selection", "category")
mgd_column_classes = c("character", "character", "character", "character", "character", "numeric", "numeric", 
                       "integer", "integer", "integer", "character", "character",
                       "character", "character", "character", "character" )
# read as table
metagenomedata = read.table(inputfilename, header=FALSE, sep="\t", stringsAsFactors=FALSE, 
                            col.names=mgd_colunm_headers, colClasses = mgd_column_classes )
# write as Rds for loading in app.R
saveRDS(metagenomedata, file = "~/git/taxonomy_database/data/NCBI_SRA_Metadata_Full_20220117.metagenomes_latlon-fixed.Rds")



#