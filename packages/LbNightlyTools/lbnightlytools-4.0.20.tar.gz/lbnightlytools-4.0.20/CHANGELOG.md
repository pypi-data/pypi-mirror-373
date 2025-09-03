# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed
 - Drop support for legacy configuration formats #49

### Added
 - Add semantics checks for nightly slots configurations #50

## [3.0.26] - 2021-02-24

### Changed
- Drop support for `getpack` (!338)

### Added
- Add support for new software stack definitions from https://gitlab.cern.ch/lhcb-core/lhcbstacks/ (!335)
- Add support for project metadata in lhcbproject.yml (!333, !334)

### Fixed
- Fix from parallel execution of tests (!337)
- Match correctly dev and deprecation warnings in CMake output (!336)
- Fix checkout of data packages when the method was explicitly set to `git` (#82)

## [3.0.25] - 2021-01-05

### Fixed
 - Do not ignore --jobs option in CMT and old-style CMake tests (!332)

## [3.0.24] - 2020-12-08

### Added
 - Add lbn-install --jobs option (!331)

## [3.0.23] - 2020-12-08

### Added
 - Use XRootD also for listing in lbn-install (!330)

## [3.0.22] - 2020-12-01

### Added
 - Use XRootD if possible and process files in parallel (!298)

## [3.0.21] - 2020-11-03

### Fixed
- Add support for LCG nightly builds for projects with the new cmake configuration (!327)

## [3.0.20] - 2020-10-15

### Fixed
- Fix disabling of projects with ci-test (!325)
- Fix regex matching in LHCbPR test schedule definitions (!326)

## [3.0.19] - 2020-09-29

### Fixed
- Fixes and improvements in /ci-test hook script (!323)
- Use lb-dirac instead of lb-run LHCbDirac while sending LHCbPR test results (!324)

## [3.0.18] - 2020-09-16

### Added
- Set `<project>_INSTALL_VERSION` in CMake cache for all projects (!322)

## [3.0.17] - 2020-09-14

### Fixed
- Fix Python 3 compatibility in lbn-get-new-refs (!321)

## [3.0.16] - 2020-09-04

### Added
- Send build ready notification to lbtaskweb (!320)

## [3.0.15] - 2020-07-21

### Fixed
 - Make clean_slot_dict function also delete ci_test trigger info (!318)
 - Add SSL variables to conda environment (!319)

## [3.0.14] - 2020-07-16

### Added
- Add ci-test trigger source to ref_slot (!317)

## [3.0.13] - 2020-07-14

### Added
 - Add "trigger" information to a test_slot created from a Gitlab MR (!316)

## [3.0.12] - 2020-07-08

### Added
 - Allow compiler extension in platform strings (like gcc9+py3) (!315)

## [3.0.11] - 2020-06-26

### Fixed
 - Never trust output to be UTF8, always ignore errors !314

## [3.0.10] - 2020-06-17

### Added
 - Added artifacts repository !306
 - Allow regex for slot/platform in periodic test definition !310
 - Show exception before fallback to legacy configuration !311
 - Added support for data packages in ci-test #59
 - Support mixing commits and MRs in ci-test !313
 - Added tests for the most common cases in ci-test !313

### Changed
 - Prefer lhcb-nightlies.web.cern.ch over lhcb-nightlies.cern.ch !312

### Fixed
 - Fixed support for multiple MRs per project in ci-test #43
 - Do not ignore project target version in ci-test #68

### Removed
 - Removed wrapper script to run nosetests !313

## [3.0.9] - 2020-05-14

### Added
 - Added command line option to specify platform in lbn-get-new-refs #69

### Removed
 - Removed clone of lhcb-benchmark-scripts in lhcbpr throughput testing setup !307

### Fixed
 - Fixed Python 3 str/bytes issues !304

## [3.0.8] - 2020-04-22

### Changed
 - Do not create symlinks for ".cvmfscatalog" in DataProjects checkouts !300

### Fixed
 - Fixed test after LbEnv 2.0.0 05de0767

## [3.0.7] - 2020-03-18

### Added
 - Add changelog !297

### Changed
 - Use vtune 2019 for throughput testing #65

## [3.0.6] - 2020-03-02

### Added
 - Add identifiers for slot and projects !290
 - Add "-legacy" aliases for lbn-{checkout,build,test} !295
 - Converted all Python scripts to setuptools entry-points !296

### Changed
 - Better way to update LHCbPR2HD !287
 - Improve slot caching of lhcb-master-ref slots !289

### Fixed
 - Fix report of CMT test in summary pages #57
 - Fixed the bug causing the platforms string to get exploded in the slot creation #30
 - Fix feedback on MRs of nightly slots !285
 - Resolve "Avoid crashes when git submodules cannot be cloned" #60

## [3.0.5] - 2020-01-31

### Fixed
 - Fix failure of CMT test jobs (#53)

## [3.0.4] - 2020-01-29

### Fixed
 - /ci-test slot failures after gilab update (#52)
 - Fix override of slot build id to accept 0 (#51)

## [3.0.3] - 2020-01-18

### Fixed

 - Fixed typo in 3.0.2 (!278)

## [3.0.2] - 2020-01-17

### Fixed
 - Improve detection of old-style CMake projects (#48)
 - Hide CMake warning about missing project() call in release slots (#47)

## [3.0.1] - 2020-01-16

### Fixed
 - Build script fails when using new CMake project and no lcg-toolchains available (#45)

## [3.0.0] - 2020-01-14

### Added

 - Support new Gaudi CMake configuration (!274)

## [2.2.3] - 2019-12-20

### Changed
 - Add CouchDB view to list slots including a MR (#41)
 - Disable projects not relevant for ci-test builds (#32)
 - Trigger unchanged slots if last build is older than N days (#40)
 - Use master branch of handlers (#39)

## [2.2.2] - 2019-12-13

### Added
 - Record config commit id in slot metadata (!268)

### Fixed
 - Fixes to lbpr commands (!253, !259)
 - Properly add reference slot metadata in "mr" slots (#38)

## [2.2.1] - 2019-12-12

### Changed

 - Hide comparison of checkout with previous slot in /ci-test jobs (#21)

### Fixed

 - Do not run check-formatting for tags (#36)
 - Test conversion to JSON in lbn-check-config (#37)

## [2.2.0] - 2019-12-09

### Changed

 - Do not rerun nightly slots that did not change from the previous build #19
 - Apply LHCb formatting to Python code #26

### Added

 - Add metadata field to Slot class/configuration dict #24
 - Add date field to CouchDB document created by main Jenkins job #27

### Fixed

 - Fix LBCORE-1836: getNightlyRefs does not respect BINARY_TAG #34

## [2.1.4] - 2019-11-20

### Fixed

 - Modified lbn-install to understand recent changes in EOSWEB listing (#29)

## [2.1.3] - 2019-11-11

### Fixed

 - Retry connection to CouchDB in case of server error (!255)

## [2.1.2] - 2019-11-04

### Fixed

 - Do not try to get last commit for DataProjects or disabled projects (for ci tests) (!254)

## [2.1.1] - 2019-10-28

### Changed

 - Force git to update lhcb-benchmark-scripts repository on production machine (!250)

### Fixed

 - Fix failure in checkout from /ci-test when merge request comes from a fork (#17)
 - Fix misleading debug message (#11)

## [2.1.0] - 2019-10-24

### Changed

 - Refactor and improve the MR slots aka /ci-test (!246)
 - Remove contrib python packages (!245)
 - Updates for LHCbPR (!244)

### Fixed

 - Set env for throughput directly before executing the job (!248)
 - Improved debugging printout (!247)

## [2.0.4] - 2019-10-21

### Fixed

 - Fix bug introduced with !240 (!243)
 - Fix handling of arch extensions in BINARY_TAG (!242)

## [2.0.3] - 2019-10-21

### Added

 - Add support for new architectures (!240)

### Fixed

 - Ensure that restarted test jobs show up as running in the dashboard (!241)

## [2.0.2] - 2019-10-15

### Fixed

 - Do not override 'commit' option in resloveMRs (#13, !239)

## [2.0.1] - 2019-10-14

### Fixed

 - Fix regression intrduced with !236 (!238)
 - Fix use of pika (!237)

## [2.0.0] - 2019-10-13
Main changes in this release are the changes to the meaning of WIP and HEAD (LBCORE-1819), the support for pip install in Jenkins jobs, and the resolution of merge request aliases in the main Jenkins job.

### Changed

 - Resolve LBCORE-1820 "Cache slot config in main" (!230, !231, !232, !233)
 - Change meaning of meta version HEAD, see LBCORE-1819 (!229)
 - Run lb-project-init at build time instead of checkout time (!227)

### Added

 - Add options to resolve the MRs aliases in the main job, see LBCORE-1712 (!236)
 - Add propagation of Virtualenv override paramaters, see LBCORE-1772 (!228)
 - Code to parse gitlab hook for mrtests (!222)

### Fixed

 - Fix handling of unicode (!234, !235)
 - Fixes for zip (!226)

## [1.0.3] - 2019-09-23
We need a tag to deploy the change of archive format to zip (!220)

### Changed

 - Use .zip instead of .tar.bz2 archives (!220, !224)

### Fixed

 - Reverted temporary workaround (#7)

## [1.0.2] - 2019-07-12
I need a tag including !221 to prepare LHCbNightlyConf!159

### Fixed

 - Support for new LHCbNightlyConf layout (!221)

## [1.0.1] - 2019-07-09
Just because it's a month we do not make releases...

### Fixed

 - LBCORE-1703: Modify nightly checkout jobs so that there is no need for patching the sources (!213, !214, !215, !216)
 - LBCORE-1774: Allow skipping of ".git" directories in lbn-install (!218)
 - Avoid type error when reading from URL with python 3.7 (!219)
 - LBCORE-1773: Allow imperative/explicit declaration of slots (!217)

## [1.0.0] - 2019-05-20

### Changed

 - Modify nightly checkout jobs so that there is no need for patching the sources (!210)
 - Removed dependency to LBSCRIPTS and call to LbEnv (!209)

### Added

 - Small extensions to checkout configuration (!212)

## [0.4.2] - 2019-03-28

### Fixed

 - Updated LbRPMTools for latest SoftConfDb client (!208)

## [0.4.1] - 2019-03-28

### Fixed

 - Fixed interface for LbSoftConfDb (!207)

## [0.4.0] - 2019-03-27

### Changed

 - Updated to use LbSoftConfDb2Clients instead of LbSoftConfDB (!205)
 - Use LbEnv instead of LbLogin for build time environment in the nightlies (!200)

### Added

 - Dump git status output after build and test jobs (c439acba)

### Fixed

 - Prefer testing version of LbEnv, with an option to switch to others (7f71d48e)
 - Add support of gzip files inside zip files in extract.php (!204)
 - Clean up platform related artifacts before building (fd41c024)
 - Fix creation of DataProject shallow clone (af3bd807)
 - Adapt to new LbEnv flavour convention (71a13ffc)
 - Fix corner case in checkout log enhancement (!203)
 - Separate sending to Dirac from the handlers call (!202)
 - Make applyenv behaviour closer to sh (9cf208ce)
 - Prevent Vc from detecting a version of binutils too old on SLC6 (586c30f7)
 - Fix for the change in lbinstall!50 (49e2f0d5)
 - Use prod MYSITEROOT in CentOS7 gitlab-ci job (b0a62db0)
 - Correctly handle build_id aliases in lbn-install (!199)

## [0.3.0] - 2018-10-27

### Changed

 - Use eos cp instead of rsync (!198)
 - Different layout of artifacts directory (!197, !198)
 - Removed references to AFS (!175)

### Added

 - lb-get-nightly-refs (!196)
 - Add function to publish the list of configured slots to the nightlies frontend (!195)

## [0.2.0] - 2018-09-26
8e6c0f4c · "make clean" instead of removing build directory (!194)

## [0.1.1] - 2018-07-21
83247b30 · Fix host-"os" CMT tag

## [0.1.0] - 2018-05-22
bb65cb48 · Merge branch 'setuptools' into 'master'

## LbScripts-v8r6p8 - 2016-09-07
83bb10ef · fixed issue with unicode strings

## LbScripts-v8r6p4 - 2016-06-21
09ccb1ee · ensure we get into 'detached HEAD' also for git checkout of default branch

## LbScripts-v8r6p3 - 2016-06-20
version used in LbScripts v8r6p3
accd05c8 · Merge branch 'NoLHCbExternals' into 'master'

## old-style-dirac - 2016-04-06
15267618 · fixed problem with changes in git merge

[Unreleased]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.26...master
[3.0.26]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.25...3.0.26
[3.0.25]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.24...3.0.25
[3.0.24]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.23...3.0.24
[3.0.23]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.22...3.0.23
[3.0.22]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.21...3.0.22
[3.0.21]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.20...3.0.21
[3.0.20]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.19...3.0.20
[3.0.19]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.18...3.0.19
[3.0.18]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.17...3.0.18
[3.0.17]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.16...3.0.17
[3.0.16]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.15...3.0.16
[3.0.15]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.14...3.0.15
[3.0.14]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.13...3.0.14
[3.0.13]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.12...3.0.13
[3.0.12]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.11...3.0.12
[3.0.11]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.10...3.0.11
[3.0.10]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.9...3.0.10
[3.0.9]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.8...3.0.9
[3.0.8]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.7...3.0.8
[3.0.7]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.6...3.0.7
[3.0.6]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.5...3.0.6
[3.0.5]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.4...3.0.5
[3.0.4]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.3...3.0.4
[3.0.3]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.2...3.0.3
[3.0.2]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.1...3.0.2
[3.0.1]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/3.0.0...3.0.1
[3.0.0]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.2.3...3.0.0
[2.2.3]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.2.2...2.2.3
[2.2.2]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.2.1...2.2.2
[2.2.1]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.2.0...2.2.1
[2.2.0]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.1.4...2.2.0
[2.1.4]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.1.3...2.1.4
[2.1.3]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.1.2...2.1.3
[2.1.2]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.1.1...2.1.2
[2.1.1]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.1.0...2.1.1
[2.1.0]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.0.4...2.1.0
[2.0.4]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.0.3...2.0.4
[2.0.3]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.0.2...2.0.3
[2.0.2]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.0.1...2.0.2
[2.0.1]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/2.0.0...2.0.1
[2.0.0]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/1.0.3...2.0.0
[1.0.3]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/1.0.2...1.0.3
[1.0.2]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/1.0.1...1.0.2
[1.0.1]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/1.0.0...1.0.1
[1.0.0]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/0.4.2...1.0.0
[0.4.2]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/0.4.1...0.4.2
[0.4.1]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/0.4.0...0.4.1
[0.4.0]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/0.3.0...0.4.0
[0.3.0]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/0.2.0...0.3.0
[0.2.0]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/0.1.1...0.2.0
[0.1.1]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/0.1.0...0.1.1
[0.1.0]: https://gitlab.cern.ch/lhcb-core/LbNightlyTools/compare/LbScripts-v8r6p8...0.1.0
