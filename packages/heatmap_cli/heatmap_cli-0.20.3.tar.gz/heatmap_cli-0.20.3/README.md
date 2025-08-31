# heatmap_cli

A console program that generates yearly calendar heatmap.

## Installation

Stable version From PyPI using `pipx`:

```console
uv tool install heatmap_cli
```

Stable version From PyPI using `pip`:

```console
uv tool upgrade heatmap_cli
```

## Usage

```console
heatmap -h -v
```

<!--help !-->

```console
usage: heatmap_cli [--demo [NUMBER_OF_COLORMAP]] [-y YEAR] [-w WEEK]
                   [-e END_DATE] [-O OUTPUT_DIR] [-o] [-p] [-v] [-t TITLE]
                   [-u AUTHOR] [-f IMAGE_FORMAT] [-c COLORMAP]
                   [-i COLORMAP_MIN_VALUE] [-x COLORMAP_MAX_VALUE] [-b]
                   [-a | --annotate | --no-annotate] [-q] [-Y] [-d] [-E] [-V]
                   [-h]
                   [CSV_FILENAME]

A console program that generates a yearly calendar heatmap.

website: https://github.com/kianmeng/heatmap_cli
changelog: https://github.com/kianmeng/heatmap_cli/blob/master/CHANGELOG.md
issues: https://github.com/kianmeng/heatmap_cli/issues

positional arguments:
  CSV_FILENAME
      CSV filename (required unless --demo is used)

options:
  --demo [NUMBER_OF_COLORMAP]
      generate number of heatmaps by colormaps (default: '192')
  -y, --year YEAR
      filter by year from the CSV file (default: '2025')
  -w, --week WEEK
      filter until week of the year from the CSV file (default: '28')
  -e, --end-date END_DATE
      filter until the date of the year from the CSV file and this will overwrite -y and -w option (default: None)
  -O, --output-dir OUTPUT_DIR
      set default output folder (default: 'output')
  -o, --open
      open the generated heatmap using the default program (default: False)
  -p, --purge
      remove all leftover artifacts set by --output-dir folder (default: False)
  -v, --verbose
      show verbosity of debugging log. Use -vv, -vvv for more details
  -t, --title TITLE
      set title for the heatmap (default: None)
  -u, --author AUTHOR
      set author for the heatmap (default: kianmeng.org)
  -f, --format IMAGE_FORMAT
      set the default image format (default: 'png')
  -c, --cmap COLORMAP
      Set default colormap. (default: 'RdYlGn_r')

      Available colormaps:
        Accent, Accent_r, afmhot, afmhot_r, autumn, autumn_r
        berlin, berlin_r, binary, binary_r, Blues, Blues_r
        bone, bone_r, BrBG, BrBG_r, brg, brg_r
        BuGn, BuGn_r, BuPu, BuPu_r, bwr, bwr_r
        cividis, cividis_r, CMRmap, CMRmap_r, cool, cool_r
        coolwarm, coolwarm_r, copper, copper_r, crest, crest_r
        cubehelix, cubehelix_r, Dark2, Dark2_r, flag, flag_r
        flare, flare_r, gist_earth, gist_earth_r, gist_gray, gist_gray_r
        gist_grey, gist_grey_r, gist_heat, gist_heat_r, gist_ncar, gist_ncar_r
        gist_rainbow, gist_rainbow_r, gist_stern, gist_stern_r, gist_yarg, gist_yarg_r
        gist_yerg, gist_yerg_r, GnBu, GnBu_r, gnuplot, gnuplot2
        gnuplot2_r, gnuplot_r, gray, gray_r, Grays, Grays_r
        Greens, Greens_r, grey, grey_r, Greys, Greys_r
        hot, hot_r, hsv, hsv_r, icefire, icefire_r
        inferno, inferno_r, jet, jet_r, magma, magma_r
        mako, mako_r, managua, managua_r, nipy_spectral, nipy_spectral_r
        ocean, ocean_r, Oranges, Oranges_r, OrRd, OrRd_r
        Paired, Paired_r, Pastel1, Pastel1_r, Pastel2, Pastel2_r
        pink, pink_r, PiYG, PiYG_r, plasma, plasma_r
        PRGn, PRGn_r, prism, prism_r, PuBu, PuBu_r
        PuBuGn, PuBuGn_r, PuOr, PuOr_r, PuRd, PuRd_r
        Purples, Purples_r, rainbow, rainbow_r, RdBu, RdBu_r
        RdGy, RdGy_r, RdPu, RdPu_r, RdYlBu, RdYlBu_r
        RdYlGn, RdYlGn_r, Reds, Reds_r, rocket, rocket_r
        seismic, seismic_r, Set1, Set1_r, Set2, Set2_r
        Set3, Set3_r, Spectral, Spectral_r, spring, spring_r
        summer, summer_r, tab10, tab10_r, tab20, tab20_r
        tab20b, tab20b_r, tab20c, tab20c_r, terrain, terrain_r
        turbo, turbo_r, twilight, twilight_r, twilight_shifted, twilight_shifted_r
        vanimo, vanimo_r, viridis, viridis_r, vlag, vlag_r
        winter, winter_r, Wistia, Wistia_r, YlGn, YlGn_r
        YlGnBu, YlGnBu_r, YlOrBr, YlOrBr_r, YlOrRd, YlOrRd_r
  -i, --cmap-min COLORMAP_MIN_VALUE
      Set the minimum value of the colormap range (default: None)
  -x, --cmap-max COLORMAP_MAX_VALUE
      Set the maximum value of the colormap range (default: None)
  -b, --cbar
      show colorbar (default: False)
  -a, --annotate, --no-annotate
      add count to each heatmap region
  -q, --quiet
      suppress all logging
  -Y, --yes
      yes to prompt
  -d, --debug
      show debugging log and stack trace
  -E, --env
      print environment information for bug reporting
  -V, --version
      show program's version number and exit
  -h, --help
      show this help message and exit.
```

<!--help !-->

## Copyright and License

Copyright (C) 2023,2024 Kian-Meng Ang

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along
with this program. If not, see <https://www.gnu.org/licenses/>.

The fish logo used in the documentation generated by Sphinx is a public domain
drawing of male freshwater phase [Steelhead (Oncorhynchus
mykiss)](https://en.wikipedia.org/w/index.php?oldid=1147106962) from
<https://commons.wikimedia.org/entity/M2787008>.
