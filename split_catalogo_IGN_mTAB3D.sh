### Línea para crear una lista con las rutas de los terremotos que hay en cada carpeta quakes_*

#ls -d /media/jlsanchezroldan/Maxtor/terremotos_adra_9495/reserieadra/reloc_adra9394_UCM_postcorreccion/loc/ADRA9394.*.grid0.loc.hyp > lista_quakes.txt 

### Script para sacar las fases de cada terremoto por separado y colocarlas en una carpeta según un intervalo temporal.

mkdir -p datos_ims
rm /datos_ims/*

sed '/^FASES/d' almería_julio_2025.txt | sed '/^ (#PRIME)/d'  > almería_julio_2025_NO_CABECERA.txt

csplit -z almería_julio_2025_NO_CABECERA.txt /"DATA_TYPE"/ '{*}'

for file_quake in xx*
do 

	sed -i -r '/^\s*$/d' $file_quake
	mv $file_quake /home/jlsanchezroldan/Nextcloud/almería_julio_2025/test_ims2nllobs/datos_ims/$file_quake.ims

done

ls -d $PWD/datos_ims/*.ims | sort -g  > lista_quakes.txt