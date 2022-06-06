# What is in the large sequence databases? #
Large sequence archives like [NCBI SRA](https://trace.ncbi.nlm.nih.gov/Traces/sra/) can be unruly for beginners. They tend not not provide much overview of what is there, or how to contextualize those data (where/when).

Scripts are written for Python and R. Below, I detail how I made:

* plot of the most common species in the [NCBI trace assembly archive](https://www.ncbi.nlm.nih.gov/Traces/wgs/?page=1&view=tsa) (dominated by the insect transcriptome project)
* [plot](https://github.com/wrf/taxonomy_database#for-all-of-ncbi-sra) of the most common samples in [NCBI SRA](https://www.ncbi.nlm.nih.gov/sra) (human and mouse samples dominate)
* plot of species diversity, by taxonomic rank (bacteria dominate)
* [plot](https://github.com/wrf/taxonomy_database#metagenomic-samples) of most common sources of metagenomes (human and gut samples dominate, then soil, then water)
* [map](https://github.com/wrf/taxonomy_database#map-of-metagenomes) of global distribution of metagenomic samples (can be modified to show any category)
* [interactive map app](https://github.com/wrf/taxonomy_database#shinyapp-of-metagenomes) of the distribution of metagenomic samples, using [RShiny](https://shiny.rstudio.com/tutorial/) and [leaflet](https://rstudio.github.io/leaflet/)

## NCBI transcriptome assemblies ##
The master list of the transcriptome shotgun archive can be found below, though the embedded links only download a GenBank format file:

`ftp://ftp.ddbj.nig.ac.jp/ddbj_database/tsa/TSA_ORGANISM_LIST.html`

Gzipped FASTA-format files can also be downloaded at the [NCBI Trace archive](https://www.ncbi.nlm.nih.gov/Traces/wgs/), by species name (e.g. *Hormiphora californensis*) or the 4-letter accessions (like GGLO01).

This currently contains transcriptomes of:

![wgs_selector_tsa_only_20220606.w_king.png](https://github.com/wrf/taxonomy_database/blob/master/images/wgs_selector_tsa_only_20220606.w_king.png)

## adding kingdom etc ##
To add kingdom, phylum and class ranks to this table, so it can be more easily searched. Copy the `organism` column to a text file (here this is named as `sra_trace_species_list_2018-04-05.txt`). Then run:

`parse_ncbi_taxonomy.py -n names.dmp -o nodes.dmp -i sra_trace_species_list_2018-04-05.txt > sra_trace_species_w_phyla_2018-04-05.txt`

NCBI Taxonomy files can be downloaded at from the `taxdump.tar.gz` file at:

`ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/`

The current, full link can be captured with:

`wget ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/new_taxdump/new_taxdump.tar.gz`

In the older method, the names had to be extracted with `cut`, using `grep` to remove the header line `organism_an`. Then use the names and the taxonomy files to regenerate the table including kingdom. 

```
cut -f 5 -d , wgs_selector_tsa_only_2018-08-23.csv | grep -v organism_an > wgs_selector_tsa_only_2018-08-23.names_only`
parse_ncbi_taxonomy.py -i wgs_selector_tsa_only_2018-08-23.names_only -n ~/db/taxonomy/names.dmp -o ~/db/taxonomy/nodes.dmp --header > wgs_selector_tsa_only_2018-08-23.w_kingdom.tab
Rscript taxon_barplot.R wgs_selector_tsa_only_2018-08-23.w_kingdom.tab
```

Thus, it is better to use the method below, which can read directly from the NCBI TSA csv file.

## using CSV from NCBI WGS ##
On the [trace archive](https://www.ncbi.nlm.nih.gov/Traces/wgs/?page=1&view=tsa), select only the `TSA` projects, and download the file `wgs_selector.csv` (renaming as desired).

`parse_ncbi_taxonomy.py -n ~/db/taxonomy_20210518/names.dmp -o ~/db/taxonomy_20210518/nodes.dmp --csv -i wgs_selector_tsa_only_20220606.csv --numbers > wgs_selector_tsa_only_20220606.w_king.tsv`

Then generate the summary barplot:

`Rscript taxon_barplot.R wgs_selector_tsa_only_20220606.w_king.tsv`

## rapid downloading and renaming ##
Assemblies can be downloaded directly from the NCBI FTP using `wget`, which can be called through the script `download_ncbi_tsa.py`. The only input requirement (`-i`) is a file of the accession numbers.

`download_ncbi_tsa.py -i download_codes.txt`

The download codes are the 4-letter accessions, with one accession per line. Only the first 4 characters are used, so the names can be directly copied out of the table, and pasted into a text file like:

```
GAUS.gz
GAUU.gz
GAVC.gz
```

With each download, the FASTA headers are changed and written into a new file, in the format of `Genus_species_XXXX01.renamed.fasta`, where `XXXX` is the accession number. For example, from `GFGY01.1.fsa_nt.gz`, a new file would be made named `Paramacrobiotus_richtersi_GFGY01.renamed.fasta`, and the FASTA header of first sequence:

```
$ gzip -dc GFGY01.1.fsa_nt.gz | head
>GFGY01000001.1 TSA: Paramacrobiotus richtersi comp116965_c2 transcribed RNA sequence
```

would be changed to:

```
$ head Paramacrobiotus_richtersi_GFGY01.renamed.fasta
>Paramacrobiotus_richtersi_comp116965_c2
```

to preserve the information from Trinity components and allow better downstream identification of splice variants (perhaps from BLAST hits). This works for the vast majority of transcriptomes, which are assembled with Trinity, though it may be necessary to confirm for each sample.

## for all of NCBI SRA ##
At the time of writing (May 2021) [NCBI SRA](https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi) contains over 10M entries, accounting for [22 petabases](https://trace.ncbi.nlm.nih.gov/Traces/sra/sra_stat.cgi) (quadruple increase from 6 petabases at the end of 2017). Chordates (mostly human samples, or mouse) account for over 3.8 million of those, and "uncategorized" samples (probably environmental metagenomic samples) account for over 2.6 million.

![NCBI_SRA_Metadata_Full_20210104.w_kingdom.png](https://github.com/wrf/taxonomy_database/blob/master/images/NCBI_SRA_Metadata_Full_20210104.w_kingdom.png)

The entire [metadata library of SRA can be downloaded](https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=mirroring), and then parsed directly from the `.tar.gz` file (which is several Gb). In general, the folder structure can be viewed from the tarball with:

`tar -tzf NCBI_SRA_Metadata_Full_20180402.tar.gz | more`

Reading from the archive took a long time (rather slowly over several days with 1 CPU). As the file became rapidly larger over the years, and I was extracting more data from the archive, the run time approached a month yet still demanded around 20Gb of memory. Thus, a new version using glob on the unzipped archive was implemented. This trades time and memory for harddive space, as the zipped archive (April 2021) is 4.8Gb, while the unzipped archive is 169Gb (97% compression). It should be noted that `gzip -l` will not give accurate measures of compression rate for files this size.

This [first version](https://github.com/wrf/taxonomy_database/blob/master/parse_sra_metadata.py) generated a 4-column table containing: sample name, the SRA number, the NCBI Taxonomy number, the scientific name (species or environment). It is now preferable for other operations to use [another script to produce a longer table](https://github.com/wrf/taxonomy_database/blob/master/parse_long_sra_metadata.py) of 12 columns for downstream analyses. Based on the xml files present, a large number of folders do not have a `sample.xml` file, which creates a long list of warnings in the script. An example STDERR is shown for the command below.

`./parse_long_sra_metadata.py NCBI_SRA_Metadata_Full_20210104.tar.gz > NCBI_SRA_Metadata_Full_20210104.samples_ext.tab 2> NCBI_SRA_Metadata_Full_20210104.samples.log`

```
# parsing metadata from NCBI_SRA_Metadata_Full_20190914.tar.gz  Wed Dec 11 12:24:59 2019
# 100 WARNINGS, WILL NOT DISPLAY MORE  Wed Dec 11 12:42:42 2019
# 100000 folders  Thu Dec 12 20:32:08 2019
# 200000 folders  Sat Dec 14 02:31:20 2019
# 300000 folders  Sun Dec 15 06:28:39 2019
# 400000 folders  Mon Dec 16 08:23:30 2019
# 500000 folders  Tue Dec 17 08:14:53 2019
# 600000 folders  Wed Dec 18 05:59:39 2019
# 700000 folders  Thu Dec 19 02:02:55 2019
# 800000 folders  Thu Dec 19 19:42:26 2019
# 900000 folders  Fri Dec 20 11:20:12 2019
# 1000000 folders  Sat Dec 21 00:52:02 2019
# 1100000 folders  Sat Dec 21 12:21:58 2019
# 1200000 folders  Sat Dec 21 21:50:16 2019
# 1300000 folders  Sun Dec 22 05:14:40 2019
# Last folder was 1391232, ERA542143/ERA542143.sample.xml  Sun Dec 22 10:09:16 2019
# Process completed in 15704.3 minutes
# Found 1391232 folders, and 6298073 samples
# Found 4222631 members not in folders
# Could not find samples for 182338 folders
```

The long table (from `parse_long_sra_metadata.py`) is then processed with the taxonomy database to make a 4-column table, of species name, kingdom, phylum and class. This can be added to any existing spreadsheet or processed into the barplot. Here, the numbers are used as input by adding the option `--numbers` to `parse_ncbi_taxonomy.py`. This requires the NCBI Taxonomy data ([see above](https://github.com/wrf/taxonomy_database#adding-kingdom-etc))

`./parse_ncbi_taxonomy.py -i NCBI_SRA_Metadata_Full_20210104.samples_ext.tab -n ~/db/taxonomy-2021-04-22/names.dmp -o ~/db/taxonomy-2021-04-22/nodes.dmp --numbers --samples --header > NCBI_SRA_Metadata_Full_20210104.w_kingdom.tab`

`Rscript taxon_barplot.R NCBI_SRA_Metadata_Full_20210104.w_kingdom.tab`

As the above command had counted each sample separately, species can instead be combined to give a sense of the species diversity. This is done by adding the `--unique` option to the `parse_ncbi_taxonomy.py` script.

`./parse_ncbi_taxonomy.py -i NCBI_SRA_Metadata_Full_20210104.samples_ext.tab -n ~/db/taxonomy-2021-04-22/names.dmp -o ~/db/taxonomy-2021-04-22/nodes.dmp --numbers --samples --header --unique > NCBI_SRA_Metadata_Full_20210104.w_kingdom_unique.tab`

The Rscript then creates the graph, displaying a similar pattern to the number of samples.

`Rscript taxon_barplot.R NCBI_SRA_Metadata_Full_20210104.w_kingdom_unique.tab`

![NCBI_SRA_Metadata_Full_20210104.w_kingdom_unique.png](https://github.com/wrf/taxonomy_database/blob/master/images/NCBI_SRA_Metadata_Full_20210104.w_kingdom_unique.png)

### Metagenomic samples ###

Almost a quarter of the samples are metagenomic, i.e. those in the "None" category for kingdom, etc. These can be parsed out of the samples file, as the `names.dmp` contains specific numbers for a number of environmental or biological categories. The option `--metagenomes-only` restricts the analysis to the 333 current metagenomic numbers.

`./parse_ncbi_taxonomy.py -i NCBI_SRA_Metadata_Full_20210104.samples_ext.tab -n ~/db/taxonomy-2021-04-22/names.dmp -o ~/db/taxonomy-2021-04-22/nodes.dmp --numbers --samples --metagenomes-only > NCBI_SRA_Metadata_Full_20210104.metagenomes.tab`

This is again used as input for the Rscript, to generate another barplot. Obviously, human samples account for a major part, though apparently `soil` has taken the lead from 2018 to 2019, but was overtaken again in 2020.

`Rscript metagenomes_barplot.R NCBI_SRA_Metadata_Full_20210104.metagenomes.tab`

![NCBI_SRA_Metadata_Full_20210104.metagenomes.png](https://github.com/wrf/taxonomy_database/blob/master/images/NCBI_SRA_Metadata_Full_20210104.metagenomes.png)

### Map of metagenomes ###

![NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-sponge_water.png](https://github.com/wrf/taxonomy_database/blob/master/images/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-sponge_water.png)

The 12-column table (from `parse_long_sra_metadata.py`) includes scientific name, lat-lon, date, source, and location (as best given).

`./parse_long_sra_metadata.py NCBI_SRA_Metadata_Full_20210104.tar.gz > NCBI_SRA_Metadata_Full_20210104.samples_ext.tab 2> NCBI_SRA_Metadata_Full_20210104.samples.log`

This is converted into the organized 13-column table including the category as a final column:

`./parse_ncbi_taxonomy.py -i NCBI_SRA_Metadata_Full_20210104.samples_ext.tab -n ~/db/taxonomy-2021-04-22/names.dmp -o ~/db/taxonomy-2021-04-22/nodes.dmp --numbers --samples --metagenomes-only > NCBI_SRA_Metadata_Full_20210104.metagenomes.tab`

The latlon information contains a lot of errors due to different versions or missing data. This must be fixed. The same goes for the dates, which were supposed to be in one of a few formats, but can also be missing or contain errors.

`./polish_metagenome_table.py -i NCBI_SRA_Metadata_Full_20210104.metagenomes.tab > NCBI_SRA_Metadata_Full_20210104.metagenomes_latlon-fixed.tab`

```
# Reading NCBI_SRA_Metadata_Full_20210104.metagenomes.tab
# Counted 2487285 entries, wrote 1179990 entries
# 818175 entries had 'VOID' as lat-lon from previous steps, removed
# 483825 entries did not include lat-lon (missing, not collected, etc.), removed
# 106 entries had other values as lat-lon, removed
# 5189 entries had an unknown format of lat-lon, removed
# 50 entries had lat-lon as deg-min-sec format, fixed
# 15 entries had lat-lon as a range, fixed
# 2461 entries had unusual formats, fixed
# 1084214 entries had acceptable date format, 95776 were missing date
# 455 entries had improbable sample dates (before 1990)
```

The output is an extended 16-column tabular file, where latlon has been split to 2 columns, and the date has been split into 3 (year month day). This makes it much easier to sort in R using the location or year.

The v1 filtered tabular data can be downloaded [here](https://bitbucket.org/wrf/datasets/downloads/NCBI_SRA_Metadata_Full_20210404.metagenomes_latlon-fixed.tab.gz). This may be updated later to include approximate locations when the location tag is given (for cities, parks, rock formations, et cetera).

This is used within the R script [metagenomes_map.R](https://github.com/wrf/taxonomy_database/blob/master/metagenomes_map.R). Due to the large number of points, it is better to use interactively, with the version below.

### Shinyapp of metagenomes ###
I had attempted two versions of an interactive app, one with the base [shiny](https://github.com/wrf/taxonomy_database/blob/master/Rshiny/app.R) package, and the other using the fancier [leaflet](https://github.com/wrf/taxonomy_database/blob/master/leaflet/app.R). The `leaflet` one is far better, with easy scrolling, sample popups, satellite view, and most of the transparency is handled by the app. However, it lacks the `brushedPoints()` feature of the base plotting, so the sample table just shows all samples within the current view, which might be a lot.

This is a merged screenshot of the `leaflet` version:

![metagenomes_leaflet_screenshot.jpg](https://github.com/wrf/taxonomy_database/blob/master/images/metagenomes_leaflet_screenshot.jpg)

With so many packages, there are often compatibility issues, so here is the `sessionInfo()`:

```
R version 3.6.3 (2020-02-29)
Platform: x86_64-pc-linux-gnu (64-bit)
Running under: Ubuntu 16.04.7 LTS

Matrix products: default
BLAS:   /usr/lib/libblas/libblas.so.3.6.0
LAPACK: /usr/lib/lapack/liblapack.so.3.6.0

locale:
 [1] LC_CTYPE=en_US.UTF-8       LC_NUMERIC=C               LC_TIME=en_US.UTF-8       
 [4] LC_COLLATE=en_US.UTF-8     LC_MONETARY=en_US.UTF-8    LC_MESSAGES=en_US.UTF-8   
 [7] LC_PAPER=en_US.UTF-8       LC_NAME=C                  LC_ADDRESS=C              
[10] LC_TELEPHONE=C             LC_MEASUREMENT=en_US.UTF-8 LC_IDENTIFICATION=C       

attached base packages:
[1] stats     graphics  grDevices utils     datasets  methods   base     

other attached packages:
[1] DT_0.17         dplyr_1.0.5     leaflet_2.0.4.1 shiny_1.6.0    

loaded via a namespace (and not attached):
 [1] Rcpp_1.0.6              pillar_1.5.1            compiler_3.6.3         
 [4] bslib_0.2.4             later_1.1.0.1           jquerylib_0.1.3        
 [7] tools_3.6.3             digest_0.6.27           jsonlite_1.7.2         
[10] lifecycle_1.0.0         tibble_3.1.0            pkgconfig_2.0.3        
[13] rlang_0.4.10            rstudioapi_0.13         cli_2.3.1              
[16] DBI_1.1.1               crosstalk_1.1.1         yaml_2.2.1             
[19] fastmap_1.1.0           withr_2.4.1             leaflet.providers_1.9.0
[22] generics_0.1.0          vctrs_0.3.6             htmlwidgets_1.5.3      
[25] sass_0.3.1              tidyselect_1.1.0        glue_1.4.2             
[28] R6_2.5.0                fansi_0.4.2             purrr_0.3.4            
[31] magrittr_2.0.1          promises_1.2.0.1        ellipsis_0.3.1         
[34] htmltools_0.5.1.1       assertthat_0.2.1        mime_0.10              
[37] xtable_1.8-4            httpuv_1.5.5            utf8_1.2.1             
[40] cachem_1.0.4            crayon_1.4.1          
```

### Gallery of errors ###
Among the most common user-entered errors is swapping NS or EW. Longitude 0 would be in London, so most of Europe/Asia is E, meaning +X, while the Americas would be W, meaning -X. Here are a few samples that should be E and are given longitude W.

![lat-lon_e-w_mirror_image_error.jpg](https://github.com/wrf/taxonomy_database/blob/master/images/lat-lon_e-w_mirror_image_error.jpg)

Another obvious error is the presence of these stripes of samples, almost looking like oceanic transects. Each sample has an increasing latitude of the one before by exactly 1 unit, likely due to a drag-copy incrementing introduced by Excel. Probably, the submitters intended to copy some of the metadata fields in the spreadsheet before submitting to NCBI, not realizing that it would copy the text but try to increment numbers wherever it could.

![excel_drag_copy_error_screenshot.jpg](https://github.com/wrf/taxonomy_database/blob/master/images/excel_drag_copy_error_screenshot.jpg)

