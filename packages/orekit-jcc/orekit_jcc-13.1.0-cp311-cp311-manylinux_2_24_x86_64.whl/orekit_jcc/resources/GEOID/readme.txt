egm96.grd / egm96.grd.hdr sont les fichiers utilisés sur l'otb

vu la taille de la grille (resolution de 0.25 degrés), ca semble correspondre au même fichier que fourni sous
earth-info.nga.mil/GandG/wgs84/gravitymod/egm96/binary.readme.txt
comme référencé par Enrico Cadau dans IPF-523 sous Jira

Par contre la grille n'a pas la taille prévue dans [GPP-DEM]


=================================
Pour générer le MNT_GLOBE, j'ai utilisé egm96_15.gtx, fourni par proj4. Attention, il faut utiliser une récente version de proj4, parceque les premiers fichiers avait une erreur de géoréférencement (un demi-pixel comme d'hab!)

