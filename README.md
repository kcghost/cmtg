# cmtg
`cmtg`(Color Matching Theme Generator) is a command line utility for generating matching color themes from templates.
It works by assigning colors from given palette(s) based on their [color difference](https://en.wikipedia.org/wiki/Color_difference).
It replaces colors of the form `#RRGGBB` in-place in the output.

## Install
Install from PyPI:
```
pip3 install cmtg
```

## Usage
```
usage: cmtg [-h] [--dist [{index,euclidean,redmean,cie1976,cie1994,cie2000,cmc}]] template palettes [palettes ...] out

Generate matching color theme given a template and palette

positional arguments:
  template              stdin, file, or builtins: ['simple.sublime-color-scheme', 'xterm.Xresources', 'pal.sh', 'pal.bash']
  palettes              stdin, file, xres, appres, or builtins: ['vga.clr', 'vscode.clr', 'ubuntu.clr', 'putty.clr', 'mirc.clr', 'powershell6.clr', 'eclipse.clr',
                        'xterm.clr', 'win10.clr', 'macos.clr', 'flat.clr', 'winxp.clr']
  out                   stdout or file

optional arguments:
  -h, --help            show this help message and exit
  --dist [{index,euclidean,redmean,cie1976,cie1994,cie2000,cmc}]
                        the color distance method (default: cie2000)
```

### Builtins
* `xres` grabs colors from `~/.Xresources` processed with `cpp` with `CMTG` macro defined
* `appres` grabs colors from `appres cmtg` output (which uses the currently loaded Xresources from xrdb)
* `simple.sublime-color-scheme`: My own Sublime Text color scheme loosely based on the `micro` editor's `simple` scheme
* `xterm.Xresources`: A typical set of colors
* `pal.bash/sh`: Scripts you can throw in a `.bashrc` that set the palette used in the [Linux console](https://en.wikipedia.org/wiki/ANSI_escape_code#OSC)
	* The default palette used in a Linux console (devoid of X) is `vga.clr`
	* Note that unlike xterm, separate foreground and background colors may not be used, you can only choose them from the 16 color palette
* `vga/winxp/powershell6/vscode/win10/macos/putty/mirc/xterm/ubuntu/eclipse.clr`: ANSI 16 color palettes used in popular terminals
	* ANSI colors consist of Black, Red, Green, Yellow, Blue, Magenta, Cyan, White and "bright" versions of each
* `flat.clr`: My own ANSI 16 color palette with low contrast
* `index` "color distance method" replaces colors in order of appearance rather than fancy algorithms

### Examples
```
cmtg pal.bash xres - >>~/.bashrc
cmtg simple.sublime-color-scheme flat.clr ~/.config/sublime-text-3/Packages/User/simple-flat.sublime-color-scheme
cmtg xterm.Xresources flat.clr ~/.Xresources
cmtg --dist index xterm.Xresources vscode.clr ~/.Xresources

cmtg vga.clr winxp.clr flat.clr /dev/null
cmtg vga.clr winxp.clr - | cmtg - flat.clr /dev/null

appres | cmtg pal.bash - >>~/.bashrc
appres | grep --color=never "color[0-9]" | sort -V | cmtg --dist index - vscode.clr -
```

### Tips
* When experimenting to get the right color assignment, use `/dev/null` output so it just prints the assignments to stderr.
* Try experimenting with different distance methods for different results
* Try chaining together palettes to work as intermediaries
	* Multiple palettes can be passed, or the results may be piped(`|`) through stdin/stdout if you need different distance methods in use
	* The `winxp.clr` palette is especially useful for ANSI colors, as its the most strictly mathematically defined
	* The builtin templates all use the `winxp.clr` pallete for this reason, they migrate to any other ANSI palette in one step
* ANSI and [base16](https://github.com/chriskempson/base16) palettes are defined differently, despite both consisting of 16 colors
	* While this utility is very generic and can be used in many contexts, the major focus is on ANSI colors
	* Support for `base16` colors and templates is a planned feature
