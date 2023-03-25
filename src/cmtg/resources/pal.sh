#!/bin/sh

setpal() {
	printf "\e]P%s%s" "${1}" "${2#\#}"
}

if [ "$TERM" = "linux" ]; then
    #setfont Tamsym8x16r
	setpal 0 "#000000"
	setpal 1 "#AA0000"
	setpal 2 "#00AA00"
	setpal 3 "#AA5500"
	setpal 4 "#0000AA"
	setpal 5 "#AA00AA"
	setpal 6 "#00AAAA"
	setpal 7 "#AAAAAA"
	setpal 8 "#555555"
	setpal 9 "#FF5555"
	setpal A "#55FF55"
	setpal B "#FFFF55"
	setpal C "#5555FF"
	setpal D "#FF55FF"
	setpal E "#55FFFF"
	setpal F "#FFFFFF"
	clear
fi
