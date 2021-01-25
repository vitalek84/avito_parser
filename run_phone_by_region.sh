#!/bin/bash

# Transport
python3 ./parser/main_phone.py -c default.json $1 avtomobili --workers 2 --chunk_size 10 --link_tmp /tmp/links
python3 ./csv_phone_create.py -data_folder_name "$1-avtomobili"
python3 ./parser/main_phone.py -c default.json $1 mototsikly_i_mototehnika --workers 2 --chunk_size 10 --link_tmp /tmp/links
python3 ./csv_phone_create.py -data_folder_name "$1-mototsikly_i_mototehnika"
python3 ./parser/main_phone.py -c default.json $1 gruzoviki_i_spetstehnika --workers 2 --chunk_size 10 --link_tmp /tmp/links
python3 ./csv_phone_create.py -data_folder_name "$1-gruzoviki_i_spetstehnika"
python3 ./parser/main_phone.py -c default.json $1 vodnyy_transport --workers 2 --chunk_size 10 --link_tmp /tmp/links
python3 ./csv_phone_create.py -data_folder_name "$1-vodnyy_transport"
python3 ./parser/main_phone.py -c default.json $1 zapchasti_i_aksessuary --workers 2 --chunk_size 10 --link_tmp /tmp/links
python3 ./csv_phone_create.py -data_folder_name "$1-zapchasti_i_aksessuary"

dd="$1-avtomobili $1-mototsikly_i_mototehnika $1-gruzoviki_i_spetstehnika $1-vodnyy_transport $1-zapchasti_i_aksessuary"
for d in ${dd}; do
	echo "copy $d"
	cp "/opt/avito-parser/$d/data.csv" "/opt/avito-parser/transport/$d-data.csv"
	echo $d >> "/opt/avito-parser/completed.txt"
done

# # Nedvigimost
# python3 ./parser/main_phone.py -c default.json $1 kvartiry --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-kvartiry"
# python3 ./parser/main_phone.py -c default.json $1 komnaty --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-komnaty"
# python3 ./parser/main_phone.py -c default.json $1 doma_dachi_kottedzhi --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-doma_dachi_kottedzhi"
# python3 ./parser/main_phone.py -c default.json $1 zemelnye_uchastki --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-zemelnye_uchastki"
# python3 ./parser/main_phone.py -c default.json $1 garazhi_i_mashinomesta --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-garazhi_i_mashinomesta"
# python3 ./parser/main_phone.py -c default.json $1 kommercheskaya_nedvizhimost --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-kommercheskaya_nedvizhimost"
# python3 ./parser/main_phone.py -c default.json $1 nedvizhimost_za_rubezhom --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-nedvizhimost_za_rubezhom"

# dd="$1-kvartiry $1-komnaty $1-doma_dachi_kottedzhi $1-zemelnye_uchastki $1-garazhi_i_mashinomesta $1-kommercheskaya_nedvizhimost $1-nedvizhimost_za_rubezhom"
# for d in ${dd}; do
# 	echo "copy $d"
# 	cp "/opt/avito-parser/$d/data.csv" "/opt/avito-parser/nedvigimost/$d-data.csv"
# 	echo $d >> "/opt/avito-parser/completed.txt"
# done

# # USLUGI
# python3 ./parser/main_phone.py -c default.json $1 it_internet_telekom --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-it_internet_telekom"
# python3 ./parser/main_phone.py -c default.json $1 bytovye_uslugi --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-bytovye_uslugi"
# python3 ./parser/main_phone.py -c default.json $1 delovye_uslugi --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-delovye_uslugi"
# python3 ./parser/main_phone.py -c default.json $1 iskusstvo --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-iskusstvo"
# python3 ./parser/main_phone.py -c default.json $1 kurerskie_uslugi --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-kurerskie_uslugi"
# python3 ./parser/main_phone.py -c default.json $1 krasota_zdorove --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-krasota_zdorove"
# python3 ./parser/main_phone.py -c default.json $1 master_na_chas --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-master_na_chas"
# python3 ./parser/main_phone.py -c default.json $1 nyani_sidelki --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-nyani_sidelki"
# python3 ./parser/main_phone.py -c default.json $1 oborudovanie_proizvodstvo --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-oborudovanie_proizvodstvo"
# python3 ./parser/main_phone.py -c default.json $1 obuchenie_kursy --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-obuchenie_kursy"
# python3 ./parser/main_phone.py -c default.json $1 ohrana_bezopasnost --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-ohrana_bezopasnost"
# python3 ./parser/main_phone.py -c default.json $1 pitanie_keytering --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-pitanie_keytering"
# python3 ./parser/main_phone.py -c default.json $1 prazdniki_meropriyatiya --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-prazdniki_meropriyatiya"
# python3 ./parser/main_phone.py -c default.json $1 reklama_poligrafiya --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-reklama_poligrafiya"
# python3 ./parser/main_phone.py -c default.json $1 remont_i_obsluzhivanie_tehniki --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-remont_i_obsluzhivanie_tehniki"
# python3 ./parser/main_phone.py -c default.json $1 remont_stroitelstvo --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-remont_stroitelstvo"
# python3 ./parser/main_phone.py -c default.json $1 sad_blagoustroystvo --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-sad_blagoustroystvo"
# python3 ./parser/main_phone.py -c default.json $1 transport_perevozki --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-transport_perevozki"
# python3 ./parser/main_phone.py -c default.json $1 uborka_klining --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-uborka_klining"
# python3 ./parser/main_phone.py -c default.json $1 ustanovka_tehniki --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-ustanovka_tehniki"
# python3 ./parser/main_phone.py -c default.json $1 uhod_za_zhivotnymi --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-uhod_za_zhivotnymi"
# python3 ./parser/main_phone.py -c default.json $1 foto-_i_videosemka --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-foto-_i_videosemka"
# python3 ./parser/main_phone.py -c default.json $1 drugoe --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-drugoe"


# dd="$1-it_internet_telekom $1-bytovye_uslugi $1-delovye_uslugi $1-iskusstvo $1-kurerskie_uslugi $1-krasota_zdorove $1-master_na_chas $1-nyani_sidelki $1-oborudovanie_proizvodstvo $1-obuchenie_kursy $1-ohrana_bezopasnost $1-pitanie_keytering $1-prazdniki_meropriyatiya $1-reklama_poligrafiya $1-remont_i_obsluzhivanie_tehniki $1-remont_stroitelstvo $1-sad_blagoustroystvo $1-transport_perevozki $1-uborka_klining $1-ustanovka_tehniki $1-uhod_za_zhivotnymi $1-foto-_i_videosemka $1-drugoe" 
# for d in ${dd}; do
# 	echo "copy $d"
# 	cp "/opt/avito-parser/$d/data.csv" "/opt/avito-parser/uslugi/$d-data.csv"
# 	echo $d >> "/opt/avito-parser/completed.txt"
# done


# # Lichnue veshi
# python3 ./parser/main_phone.py -c default.json $1 odezhda_obuv_aksessuary --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-odezhda_obuv_aksessuary"
# python3 ./parser/main_phone.py -c default.json $1 detskaya_odezhda_i_obuv --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-detskaya_odezhda_i_obuv"
# python3 ./parser/main_phone.py -c default.json $1 tovary_dlya_detey_i_igrushki --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-tovary_dlya_detey_i_igrushki"
# python3 ./parser/main_phone.py -c default.json $1 chasy_i_ukrasheniya --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-chasy_i_ukrasheniya"
# python3 ./parser/main_phone.py -c default.json $1 krasota_i_zdorove --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-krasota_i_zdorove"

# dd="$1-odezhda_obuv_aksessuary $1-detskaya_odezhda_i_obuv $1-tovary_dlya_detey_i_igrushki $1-chasy_i_ukrasheniya $1-krasota_i_zdorove" 
# for d in ${dd}; do
# 	echo "copy $d"
# 	cp "/opt/avito-parser/$d/data.csv" "/opt/avito-parser/lichnue_veshi/$d-data.csv"
# 	echo $d >> "/opt/avito-parser/completed.txt"
# done


# # Dly_doma_i_Dachi
# python3 ./parser/main_phone.py -c default.json $1 bytovaya_tehnika --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-bytovaya_tehnika"
# python3 ./parser/main_phone.py -c default.json $1 mebel_i_interer --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-mebel_i_interer"
# python3 ./parser/main_phone.py -c default.json $1 posuda_i_tovary_dlya_kuhni --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-posuda_i_tovary_dlya_kuhni"
# python3 ./parser/main_phone.py -c default.json $1 produkty_pitaniya --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-produkty_pitaniya"
# python3 ./parser/main_phone.py -c default.json $1 remont_i_stroitelstvo --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-remont_i_stroitelstvo"
# python3 ./parser/main_phone.py -c default.json $1 rasteniya --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-rasteniya"


# dd="$1-bytovaya_tehnika $1-mebel_i_interer $1-posuda_i_tovary_dlya_kuhni $1-produkty_pitaniya $1-remont_i_stroitelstvo $1-rasteniya" 
# for d in ${dd}; do
# 	echo "copy $d"
# 	cp "/opt/avito-parser/$d/data.csv" "/opt/avito-parser/dlya_doma_i_dachi/$d-data.csv"
# 	echo $d >> "/opt/avito-parser/completed.txt"
# done


# # bytovaya_elektronika
# python3 ./parser/main_phone.py -c default.json $1 audio_i_video --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-audio_i_video"
# python3 ./parser/main_phone.py -c default.json $1 igry_pristavki_i_programmy --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-igry_pristavki_i_programmy"
# python3 ./parser/main_phone.py -c default.json $1 nastolnye_kompyutery --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-nastolnye_kompyutery"
# python3 ./parser/main_phone.py -c default.json $1 noutbuki --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-noutbuki"
# python3 ./parser/main_phone.py -c default.json $1 orgtehnika_i_rashodniki --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-orgtehnika_i_rashodniki"
# python3 ./parser/main_phone.py -c default.json $1 planshety_i_elektronnye_knigi --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-planshety_i_elektronnye_knigi"
# python3 ./parser/main_phone.py -c default.json $1 bytovaya_tehnika --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-bytovaya_tehnika"
# python3 ./parser/main_phone.py -c default.json $1 telefony --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-telefony"
# python3 ./parser/main_phone.py -c default.json $1 tovary_dlya_kompyutera --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-tovary_dlya_kompyutera"
# python3 ./parser/main_phone.py -c default.json $1 fototehnika --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-fototehnika"

# dd="$1-audio_i_video $1-igry_pristavki_i_programmy $1-nastolnye_kompyutery $1-noutbuki $1-orgtehnika_i_rashodniki $1-planshety_i_elektronnye_knigi $1-bytovaya_tehnika $1-telefony $1-tovary_dlya_kompyutera $1-fototehnika" 
# for d in ${dd}; do
# 	echo "copy $d"
# 	cp "/opt/avito-parser/$d/data.csv" "/opt/avito-parser/bytovaya_elektronika/$d-data.csv"
# 	echo $d >> "/opt/avito-parser/completed.txt"
# done

# # hobbi_i_otdyh
# python3 ./parser/main_phone.py -c default.json $1 bilety_i_puteshestviya --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-bilety_i_puteshestviya"
# python3 ./parser/main_phone.py -c default.json $1 velosipedy --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-velosipedy"
# python3 ./parser/main_phone.py -c default.json $1 knigi_i_zhurnaly --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-knigi_i_zhurnaly"
# python3 ./parser/main_phone.py -c default.json $1 kollektsionirovanie --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-kollektsionirovanie"
# python3 ./parser/main_phone.py -c default.json $1 muzykalnye_instrumenty --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-muzykalnye_instrumenty"
# python3 ./parser/main_phone.py -c default.json $1 ohota_i_rybalka --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-ohota_i_rybalka"
# python3 ./parser/main_phone.py -c default.json $1 sport_i_otdyh --workers 2 --chunk_size 10 --link_tmp /tmp/links
# python3 ./csv_phone_create.py -data_folder_name "$1-sport_i_otdyh"

# dd="$1-bilety_i_puteshestviya $1-velosipedy $1-knigi_i_zhurnaly $1-kollektsionirovanie $1-muzykalnye_instrumenty $1-ohota_i_rybalka $1-sport_i_otdyh" 
# for d in ${dd}; do
# 	echo "copy $d"
# 	cp "/opt/avito-parser/$d/data.csv" "/opt/avito-parser/hobbi_i_otdyh/$d-data.csv"
# 	echo $d >> "/opt/avito-parser/completed.txt"
# done