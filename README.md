# taxonomy database #
The master list of the transcriptome shotgun archive can be found below, though the embedded links only download a GenBank format file:

`ftp://ftp.ddbj.nig.ac.jp/ddbj_database/tsa/TSA_ORGANISM_LIST.html`

Gzipped FASTA-format files can also be downloaded at the [NCBI Trace archive](https://www.ncbi.nlm.nih.gov/Traces/wgs/), by species name (e.g. *Hormiphora californensis*) or the 4-letter accessions (like GGLO01).

This currently contains transcriptomes of:

![wgs_selector_tsa_only_2019-01-11.w_kingdom.png](https://github.com/wrf/taxonomy_database/blob/master/images/wgs_selector_tsa_only_2019-01-11.w_kingdom.png)

## adding kingdom etc ##
To add kingdom, phylum and class ranks to this table, so it can be more easily searched. Copy the `organism` column to a text file (here this is named as `sra_trace_species_list_2018-04-05.txt`). Then run:

`parse_ncbi_taxonomy.py -n names.dmp -o nodes.dmp -i sra_trace_species_list_2018-04-05.txt > sra_trace_species_w_phyla_2018-04-05.txt`

NCBI Taxonomy files can be downloaded at from the `taxdump.tar.gz` file at:

`ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/`

## using CSV from NCBI WGS ##
On the [trace archive](https://www.ncbi.nlm.nih.gov/Traces/wgs/?page=1&view=tsa), select only the `TSA` projects, and download the file `wgs_selector.csv` (renaming as desired).

Extract the names with `cut`, using `grep` to remove the header line `organism_an`:

`cut -f 5 -d , wgs_selector_tsa_only_2018-08-23.csv | grep -v organism_an > wgs_selector_tsa_only_2018-08-23.names_only`

Then use the names and the taxonomy files to regenerate the table including kingdom:

`parse_ncbi_taxonomy.py -i wgs_selector_tsa_only_2018-08-23.names_only -n ~/db/taxonomy/names.dmp -o ~/db/taxonomy/nodes.dmp --header > wgs_selector_tsa_only_2018-08-23.w_kingdom.tab`

Then generate the summary barplot:

`Rscript taxon_barplot.R wgs_selector_tsa_only_2018-08-23.w_kingdom.tab`

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
At the time of writing (Dec 2019) [NCBI SRA](https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi) contains over 6.2M entries, accounting for [13 petabases](https://trace.ncbi.nlm.nih.gov/Traces/sra/sra_stat.cgi) (doubling from 6 petabases at the end of 2017). Chordates (mostly human samples, or mouse) account for over 2.5 million of those, and "uncategorized" samples (probably environmental metagenomic samples) account for almost 1.6 million.

![NCBI_SRA_Metadata_Full_20191130.ncbi_ids_w_kingdom.png](https://github.com/wrf/taxonomy_database/blob/master/images/NCBI_SRA_Metadata_Full_20191130.ncbi_ids_w_kingdom.png)

The entire [metadata library of SRA can be downloaded](https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=mirroring), and then parsed directly from the `.tar.gz` file (which is 1.8Gb). In general, the folder structure can be viewed from the tarball with:

`tar -tzf NCBI_SRA_Metadata_Full_20180402.tar.gz | more`

Reading from the archive took a long time (rather slowly over several days with 1 CPU). This generates a 4-column table containing: sample name, the SRA number, the NCBI Taxonomy number, the scientific name (species or environment). Based on the xml files present, a large number of folders do not have a `sample.xml` file, which creates a long list of warnings in the script. The STDERR is shown for the command below.

`parse_sra_metadata.py NCBI_SRA_Metadata_Full_20190914.tar.gz > NCBI_SRA_Metadata_Full_20190914.samples.tab 2> NCBI_SRA_Metadata_Full_20190914.samples.log`

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

This produces a table that would look like:

```
PNUSAE012016	SRS3075518	562	Escherichia coli
2672F-sc-2013-07-18T13:25:16Z-1668979	ERS327577	1773	Mycobacterium tuberculosis
PRJEB19319	ERS1543308	182710	Oceanobacillus iheyensis
```

Because the NCBI taxonomy numbers are also given, rather than just samples, those can be used instead to index the nodes in the taxonomy tree. The NCBI IDs (numbers) are extracted with the shell command `cut`, taking the third column:

`cut -f 3 NCBI_SRA_Metadata_Full_20180402.samples.tab > NCBI_SRA_Metadata_Full_20180402.ncbi_ids.txt`

This is then processed as above from the taxonomy database to make a 4-column table, of species name, kingdom, phylum and class. This can be added to any existing spreadsheet or processed into the barplot. Here, the numbers are used as input by adding the option `--numbers` to `parse_ncbi_taxonomy.py`. This requires the NCBI Taxonomy data ([see above](https://github.com/wrf/taxonomy_database#adding-kingdom-etc))

`parse_ncbi_taxonomy.py -i NCBI_SRA_Metadata_Full_20180402.ncbi_ids.txt -n ~/db/taxonomy/names.dmp -o ~/db/taxonomy/nodes.dmp --numbers --header > NCBI_SRA_Metadata_Full_20180402.ncbi_ids_w_kingdom.tab`

`Rscript taxon_barplot.R NCBI_SRA_Metadata_Full_20180402.ncbi_ids_w_kingdom.tab`

As the above command had counted each sample separately, species can instead be combined to give a sense of the species diversity. This is done by adding the `--unique` option to the `parse_ncbi_taxonomy.py` script.

`parse_ncbi_taxonomy.py -i NCBI_SRA_Metadata_Full_20180402.ncbi_ids.txt -n ~/db/taxonomy/names.dmp -o ~/db/taxonomy/nodes.dmp ~/db/taxonomy/merged.dmp --numbers --header --unique > NCBI_SRA_Metadata_Full_20180402.unique_ncbi_ids_w_king.tab`

The Rscript then creates the graph, displaying a similar pattern to the number of samples.

`Rscript taxon_barplot.R NCBI_SRA_Metadata_Full_20180402.unique_ncbi_ids_w_king.tab`

![NCBI_SRA_Metadata_Full_20191130.unique_ncbi_ids_w_king.png](https://github.com/wrf/taxonomy_database/blob/master/images/NCBI_SRA_Metadata_Full_20191130.unique_ncbi_ids_w_king.png)

### Metagenomic samples ###

Almost a quarter of the samples are metagenomic, i.e. those in the "None" category for kingdom, etc. These can be parsed out of the samples file, as the `names.dmp` contains specific numbers for a number of environmental or biological categories. The option `--metagenomes-only` restricts the analysis to the 258 current metagenomic numbers.

`parse_ncbi_taxonomy.py -i NCBI_SRA_Metadata_Full_20181203.samples.tab -n ~/db/taxonomy/names.dmp -o ~/db/taxonomy/nodes.dmp --numbers --samples --metagenomes-only > NCBI_SRA_Metadata_Full_20181203.metagenomes.tab`

This is again used as input for the Rscript, to generate another barplot. Obviously, human samples account for a major part, though apparently `soil` has taken the lead from 2018 to 2019.

`Rscript metagenomes_barplot.R NCBI_SRA_Metadata_Full_20181203.metagenomes.tab`

![NCBI_SRA_Metadata_Full_20191130.metagenomes.png](https://github.com/wrf/taxonomy_database/blob/master/images/NCBI_SRA_Metadata_Full_20191130.metagenomes.png)

### Map of metagenomes ###

![NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-sponge_water.png](https://github.com/wrf/taxonomy_database/blob/master/images/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-sponge_water.png)

To instead extract a longer table including location and latitude/longitude of each sample, use the alternate script. This produces a 9-column table, the same 4 as above, with scientific name, lat-lon, date, source, and location (as best given).

`parse_long_sra_metadata.py NCBI_SRA_Metadata_Full_20191130.tar.gz > NCBI_SRA_Metadata_Full_20191130.sample_ext.tab`

This is converted into the organized table including the category as a final column:

`./parse_ncbi_taxonomy.py -n ~/db/taxonomy-20191211/names.dmp -o ~/db/taxonomy-20191211/nodes.dmp -i NCBI_SRA_Metadata_Full_20191130.sample_ext.tab --metagenomes-only --numbers --samples > NCBI_SRA_Metadata_Full_20191130.metagenomes_ext.tab`

The latlon information contains a lot of errors due to different versions or missing data. This must be fixed.

`polish_metagenome_table.py NCBI_SRA_Metadata_Full_20191130.metagenomes_ext.tab > NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon-fixed.tab`

```
# Reading NCBI_SRA_Metadata_Full_20191130.metagenomes_w_member.tab
# Counted 1131076 entries, wrote 686747 entries
# 443173 entries did not include lat-lon (missing, not collected, etc.), removed
# 106 entries had other values as lat-lon, removed
# 1050 entries had an unknown format of lat-lon, removed
# 50 entries had lat-lon as deg-min-sec format, fixed
# 15 entries had lat-lon as a range, fixed
# 1465 entries had unusual formats, fixed
```

The v1 filtered tabular data can be downloaded [here](https://bitbucket.org/wrf/subsurface2017/downloads/NCBI_SRA_Metadata_Full_20191130.metagenomes_latlon_v1.tab.gz). This may be updated later to include approximate locations when the location tag is given (for cities, parks, rock formations, et cetera).

This is used within the R script [metagenomes_map.R](https://github.com/wrf/taxonomy_database/blob/master/metagenomes_map.R). Due to the large number of points, it is better to use interactively.


