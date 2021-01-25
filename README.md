Установка
===================================

# Python 3.6+
# Установить пакеты: tesseract (tesseract-ocr), tesseract ru (tesseract-ocr-rus), libjpeg (libjpeg9), libpng (libpng16-16), zlib (zlib1g), opencv python3 bindings (python3-opencv), pip3 (python3-pip)
# Установить от имени root зависимости через pip3: pip3 install -r pip.req
# Установить Firefox последней версии
# Скачать Firefox драйвер последней версии для selenium - https://github.com/mozilla/geckodriver/releases/
# Распаковать Firefox драйвер. Переместить бинарный файл geckodriver в /usr/bin или другое место из PATH. Дать права на исполенение

Запуск парсера номеров телефонов
===================================

`
python3 ./parser/main_phone.py -c local.json tulskaya_oblast odezhda_obuv_aksessuary --workers 2 --chunk_size 10 --link_tmp /tmp/links
`

При такой конфигурации (2 воркера, чанки по 10 ссылок) выжирает максимум 2 гб оперативки