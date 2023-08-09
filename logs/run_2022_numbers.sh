#!/bin/bash

touch starttime
# -rw-rw-r--  1 wrf wrf           0 Jun 22 15:38 starttime
tar -zxpf NCBI_SRA_Metadata_Full_20220117.tar.gz -C Full_20220117/
touch endtime
# -rw-rw-r--  1 wrf wrf           0 Jun 23 15:13 endtime


#/dev/sdb1      961302540 461856164 450591916  51% /mnt/data
#/dev/sdb1      961302540 611146900 301301180  67% /mnt/data


~/git/taxonomy_database/parse_long_sra_metadata.py Full_20220117/ > NCBI_SRA_Metadata_Full_20220117.sample_w_exp.tab 2> NCBI_SRA_Metadata_Full_20220117.sample_w_exp.log

~/git/taxonomy_database/parse_long_sra_metadata.py Full_20220117/ > NCBI_SRA_Metadata_Full_20220117.sample_w_exp.short.tab

~/git/taxonomy_database/parse_ncbi_taxonomy.py -i NCBI_SRA_Metadata_Full_20220117.sample_w_exp.tab -n ~/db/taxonomy_20220628/names.dmp -o ~/db/taxonomy_20220628/nodes.dmp --numbers --samples --header > NCBI_SRA_Metadata_Full_20220117.sample_kingdom.tab

Rscript ~/git/taxonomy_database/taxon_barplot.R NCBI_SRA_Metadata_Full_20220117.sample_kingdom.tab

~/git/taxonomy_database/parse_ncbi_taxonomy.py -i NCBI_SRA_Metadata_Full_20220117.sample_w_exp.tab -n ~/db/taxonomy_20220628/names.dmp -o ~/db/taxonomy_20220628/nodes.dmp --numbers --samples --header --unique > NCBI_SRA_Metadata_Full_20220117.sample_kingdom_unique.tab

Rscript ~/git/taxonomy_database/taxon_barplot.R NCBI_SRA_Metadata_Full_20220117.sample_kingdom_unique.tab

~/git/taxonomy_database/parse_ncbi_taxonomy.py -i NCBI_SRA_Metadata_Full_20220117.sample_w_exp.tab -n ~/db/taxonomy_20220628/names.dmp -o ~/db/taxonomy_20220628/nodes.dmp --numbers --samples --metagenomes-only > NCBI_SRA_Metadata_Full_20220117.metagenomes.tab

Rscript ~/git/taxonomy_database/metagenomes_barplot.R NCBI_SRA_Metadata_Full_20220117.metagenomes.tab

~/git/taxonomy_database/polish_metagenome_table.py -i NCBI_SRA_Metadata_Full_20220117.metagenomes.tab > NCBI_SRA_Metadata_Full_20220117.metagenomes_latlon-fixed.tab














