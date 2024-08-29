Master

[unreleased]
- updated github actions

v0.70.0 - 2024-08-29
- fix error when no start time defined

v0.69.0 - 2024-08-29
- convert UTC to local time to prevent timezone issues

v0.68.0 - 2024-08-18
- use macos-13 on github runner

v0.67.0 - 2024-08-18
- use latest macos on github runner

v0.66.0 - 2024-08-18
- bump opensoar to 1.1.3: fix timezone correction

v0.65.0 - 2024-02-11
- bump opensoar to 1.1.2: now support empty callsign
- fix internal typo in settingsclass

v0.64.0 - 2023-08-25
- made export more robust when certain attributes not present
- update opensoar: fixes normal sectors

v0.63.0 - 2023-05-20
- updated python, dependencies and actions to latest
- update opensoar: fixes complex aat sectors

v0.62.0 - 2023-03-26
- update dependencies
- drop strepla support
- opensoar brings significant speedup
- automated ci

v0.61.0
- update dependencies
- opensoar newest version fixes soaringspot
- remove unused functions

v0.60.0
- use calculation thread to fix 'not-responding' in GUI
- update opensoar dependecy
- remove unused dependencies
- fix bug in skipped analyses
- add CI build and publish

v0.60.0-rc1
- use calculation thread to fix 'not-responding' in GUI
- update opensoar dependecy
- remove unused dependencies
- fix bug in skipped analyses
- add CI build and publish

v0.59.0
- check on version during startup
- bump opensoar to 0.1.4 to solve dev.soaringspot.com

v0.58.0
- use wxpython instead of tkinter for GUI

v0.57.2
- try, except around performance creation
- bump opensoar to v0.1.3

v0.57.1
- update opensoar to 0.1.2

v0.57.0
- Use opensoar and aerofiles functionalities (#100, #123)
- Do not skip HC contestants
- Skip contestant for which analysis fails
- several bugfixes

v0.56.3
- Fix aat with fixed sector orientation

v0.56.2
- Fix changes to soaringspot internal structure

v0.56
- Strepla support
