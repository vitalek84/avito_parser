#!/bin/bash

rm -f "/opt/avito-parser/completed.txt"
folds="transport nedvigimost rabota uslugi lichnue_veshi dlya_doma_i_dachi bytovaya_elektronika hobbi_i_otdyh"
for f in ${folds}; do
	rm  -rf "/opt/avito-parser/$f/"
	mkdir "/opt/avito-parser/$f/"
done


touch "/opt/avito-parser/completed.txt"
regions="moskva moskovskaya_oblast sankt-peterburg leningradskaya_oblast adygeya altayskiy_kray amurskaya_oblast arhangelskaya_oblast astrahanskaya_oblast bashkortostan belgorodskaya_oblast bryanskaya_oblast buryatiya vladimirskaya_oblast volgogradskaya_oblast vologodskaya_oblast voronezhskaya_oblast dagestan evreyskaya_ao zabaykalskiy_kray ivanovskaya_oblast irkutskaya_oblast kabardino-balkariya kaliningradskaya_oblast kalmykiya kaluzhskaya_oblast kamchatskiy_kray karachaevo-cherkesiya kareliya kemerovskaya_oblast kirovskaya_oblast komi kostromskaya_oblast krasnodarskiy_kray krasnoyarskiy_kray respublika_krym kurganskaya_oblast kurskaya_oblast lipetskaya_oblast magadanskaya_oblast mariy_el murmanskaya_oblast nenetskiy_ao nizhegorodskaya_oblast novgorodskaya_oblast novosibirskaya_oblast omskaya_oblast orenburgskaya_oblast orlovskaya_oblast penzenskaya_oblast permskiy_kray primorskiy_kray pskovskaya_oblast respublika_altay rostovskaya_oblast ryazanskaya_oblast samarskaya_oblast saratovskaya_oblast sahalinskaya_oblast saha_yakutiya sverdlovskaya_oblast smolenskaya_oblast stavropolskiy_kray tambovskaya_oblast tatarstan tverskaya_oblast tomskaya_oblast tulskaya_oblast tyva tyumenskaya_oblast udmurtiya ulyanovskaya_oblast habarovskiy_kray hakasiya hanty-mansiyskiy_ao chelyabinskaya_oblast chechenskaya_respublika chuvashiya chukotskiy_ao yamalo-nenetskiy_ao yaroslavskaya_oblast"

for region in ${regions}; do
	rm -rf find "$region*"
	echo "$region"
	. run_phone_by_region.sh ${region}
done