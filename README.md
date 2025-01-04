# OUI-Visualization

- standardize to tkinter
  - use a theme: [list](https://www.reddit.com/r/Python/comments/lps11c/how_to_make_tkinter_look_modern_how_to_use_themes/)
- add Main Menu
- Pri izdelavi kode bodite prosim pozorni na glavni razlog, zakaj zlagamo vse skupaj v isto aplikacijo: želimo imeti kodo dovolj transparentno in pregledno, da jo lahko kasnejši študenti morda še nadgrajujejo.
- Program naj omogoča izris vseh spodnjih vizualizacij. V primeru, da katere ne morete prevesti mora za to obstajati tehten razlog.
- Dodatno/opcijsko: Shranjevanje in uporaba programov je zelo raznolika. Če vidite možnost za oblikovno poenotenje in poenotenje branja vhodov je to smiselno dodati.
- Dodatno/opcijsko: Nekateri algoritmi vsebujejo še logične napake. Če jih zaznate jih sporočite in odpravite.

# Original projects

- [x] Alpha Beta Pruning

  - uses tkinter
  - works

- [x] D-separation

  - uses tkinter
  - works
  - uses pygraphviz which "is notoriously difficult to install on a windows machine", has a windows version of the script without the dependency
  - outputs a lot of the information to the terminal

- [x] KNN

  - uses tkinter
  - works
  - clicking breaks after clicking outside the canvas
  - heavy preprocessing, before the UI even opens
  - does not exit after closing the window, requires a force quit

- [ ] AO

  - uses tkinter
  - works
  - uses a lot of global variables

- [ ] Nomogram

  - uses a **jupyter notebook**
  - works

- [ ] Razporejanje

  - uses tkinter
  - works
  - no example input

- [ ] Planiranje

  - uses **pygame**
  - works
  - throws error when moving blocks

- [ ] Rezanje
  - uses tkinter
  - **does not work**
  - made for cli, gui ("TODO: počasno")
  - horrible code quality
  - requires local graphviz installation
