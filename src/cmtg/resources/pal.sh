#!/bin/sh

setpal() {
	printf "\e]P%s%s" "${1}" "${2#\#}"
}

if [ "$TERM" = "linux" ]; then
    #setfont Tamsym8x16r
	setpal 0 "#000000"
	setpal 1 "#800000"
	setpal 2 "#008000"
	setpal 3 "#808000"
	setpal 4 "#000080"
	setpal 5 "#800080"
	setpal 6 "#008080"
	setpal 7 "#c0c0c0"
	setpal 8 "#808080"
	setpal 9 "#ff0000"
	setpal A "#00ff00"
	setpal B "#ffff00"
	setpal C "#0000ff"
	setpal D "#ff00ff"
	setpal E "#00ffff"
	setpal F "#ffffff"
	clear
fi
