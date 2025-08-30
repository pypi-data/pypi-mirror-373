"""ganessa integration package for PicWin32/Ganessa_SIM/Ganessa_TH - see pyGanessa.html"""
# Version of the package
__version__ = "2.5.4"

#****g* ganessa.sim&th/About
# PURPOSE
#   The module ganessa.sim (resp. ganessa.th) provides a Python interface
#   to Picwin32.dll and Ganessa_SIM.dll (resp. Ganessa_TH.dll) kernel API.
#   It is provided as python wheels:
#   * all versions up to version 2.1.9 (april 2021) are compatible with python 2.7.
#   * from version 2, it is compatible with 32 and 64 bits versions of python 3.6/3.7.
#   * from version 2.1, it is compatible with python 3.7.6 and 3.8.
#   * from version 2.1.5, it is compatible with python 3.9.
#   * from version 2.1.8, it is compatible with python 3.10.
#   * up to version 2.1.9, it is compatible with python 2.7.
#   * from version 2.3.3, it is compatible with python 3.11.
#   * from version 2.3.10, it is compatible with python 3.12.
#   * from version 2.4.2, it is compatible with python 3.13.
#
#   The module name ganessa.sim&th is used for items available both
#   in .sim and .th environments
#
# INSTALLATION
#   |html <pre> python -m pip install [--trusted-host pypi.org] ganessa </pre>
#
#   The package expects the simulation kernel .dll to be found either
#   in the folders given by %GANESSA_DIR% environment variable (for Ganessa_xx.dll)
#   or %PICCOLO_DIR% (for Picwin32.dll),
#   or in the %PATH% environment variable (either name),
#   or in %LOCALAPPDATA%/Programs folders:
#   * Safege/Ganessa_<lang>/Ganessa_SIM.dll (or Suez/...)
#   * Safege/Piccolo_<lang>/Picwin32.dll    (or Suez/...)
#   * Inetum/Piccolo6_<lang>/Picwin32.dll   (starting with version 2.2.3)
#   * Gfi Progiciels/Piccolo6_<lang>/Picwin32.dll
#   or in one of the "Program Files (x86)"" sub folders (Picalor6 replaces Piccolo6 if needed):
#   * "Safege/Ganessa_<lang>/Ganessa_xx" (or Suez/...) (xx = SIM or TH) or
#   * "Inetum/Piccolo6_<lang>[_ck | _cl]/Picwin32.dll" or
#   * "Gfi Progiciels/Piccolo6_<lang>[_ck | _cl]/Picwin32.dll" or
#   * "Adelior/Piccolo5_<lang>/Picwin32.dll"
#   in either drive C: or D:
# USE
#   Syntax:
#       import ganessa.sim as pic   (or ganessa.th for Picalor)
#       pic.cmdfile("my file.dat")
#   Or:
#       from ganessa.sim import *
#       cmdfile("my file.dat")
#
#   the import will perform the following initialisation tasks:
#   * determines if it runs in python embedded - cf. is_embedded()
#   * locate Ganessa_xx.dll or Picwin32.dll kernel
#   * initialise it (if not run in embedded python)
#   * locate result.bin in a working subdirectory
#   * bind termination to ctrl+Z
# CONTENT
#   The package provides the following content:
#   * constants for calling API functions
#   * iterators for browsing objects, selections and tables
#   * functions for loading .bin file
#   * functions for executing command files / command strings / running simulations
#   * functions and exceptions for catching simulation errors and retrieving unstable items
#   * exceptions: GanessaError, SimulationError, IsolatedNodeSimulationError
#   * functions for retrieving individual objects attributes
#   * functions for retrieving table entries and object count
#   * functions for retrieving result or measurements time series
#   * functions for retrieving min / max / avg values for all objects
#
# REMARKS
#   * Most of the functions are getter. A few direct setter functions are provided
#     (setlinkattr, setdensity, defcalind, *SHL functions). The general purpose
#     gencmd(w), addcmd(w), cmd, execute and cmdfile can be used to build / commit
#     any other settings with command language (see the Piccolo Reference Manual).
#   * Commands (passed to cmd, execute, cmdfile) should be built in the language
#     (idiom) of the current version. getkeyword, modulekeyword, attrkeyword allow
#     to retrieve a given keyword in the current idiom; gencmd(w) allow to build a
#     command line in the current idiom from symbolic keywords.
#   * 'setlang' command allow to retrieve the current idiom and switch to another.
#   * A command file may be written in any of English, French or Spanish, the current
#     command language interpreter will switch to the xxx language from "_LANG_ xxx"
#     command until the end of the file, then switch back to the current language.
#   * Only recent Ganessa_SIM.dll versions can be used with this package, if not recent enough
#     import will fail and (try to) use any available PicWin32.dll.
#   * Any suggestion for extending / improving can be mailed to: piccolo@safege.fr
#
# HISTORY
#   The history of the package is:
#   * 1.0.0: (140211) creation of the package for python 2.7
#   * 1.0.3: (140410) plotmesx png takes care of measurement type
#   * 1.0.4: (140702) added demand getter for a demand code or for all
#   * 1.0.5: (140908) added Windows 7 paths 'program files (x86)';
#            added option to get TS by measurement step 'tsvalbymts';
#            added 'refdate' : retireval of REFDATE
#   * 1.0.6: (140908) correction to the grid adjustment in plotmes (util)
#   * 1.0.7: (140916) getMinMax can be called with a selection name
#   * 1.0.8: (140925) save function
#   * 1.0.9: (141006)SimulationError exception catching + save(identical to MMI);
#            requires numpy 1.8.1
#   * 1.1.0: (141006) same as 1.0.9 but requires only numpy 1.7.1
#   * 1.1.1: (141016) minor change to codewinfile=winstr
#   * 1.1.2: (141020) added 'execute' for multiple commands as strings (\n managed as a separator)
#   * 1.1.3: (141104) disable useoffset for Y axes in 'util.plotmes'
#   * 1.1.4: (141118) handling Picwin32.dll provided by GFI after 18-11-2014 (best 03-12-2014)
#   * 1.1.5: (141205) handling ts < ms in tsvalbymts
#   * 1.1.6: (150127) nodexyz added + bugfix in attrs documentation
#   * 1.1.7: (150309) minor grammatical changes
#   * 1.2.0: (150507) change in folder search order (ws7 priority) + language - OK with Picwin32 151203
#   * 1.2.1: (150527) Picalor enabled  as ganessa.th + density and SHL management;
#            (150603) added 'meanattr';
#            (150610) added 'addSHLtype'
#   * 1.2.2: (150709) bug fix calls select* from Selected
#   * 1.2.3: (150812) bug fix: return value of browseWQ; getall
#   * 1.2.4: (150910) constants added (WQ, Inverse Pb) + demandcodes
#   * 1.2.5: (150922) utils: tuning of plotmes subtitle fontsize for large titles
#                      + constants (MOD, NOD ...) + 'areas' function
#   * 1.2.6: (151128) added tsdemand and tsdemandlen, tsdevice and tsdevicelen;
#                     added tables (material, area etc.) access;
#                     utils: added list2file
#   * 1.3.0: (151202) added support for compatibility with Picwin32 12/2014, 12/2015 and Ganessa;
#            (151206) addl constants (BRA, DYN, RSV);
#            (151218) reviewed compatibility with Picwin32 (2015+ -> Piccolo6), (2014 -> Piccolo5)
#   * 1.3.1: (160108) header, footer and suffix optional args for utils.list2file;
#            (160113) added memory allocation error exception (inverse module)
#   * 1.3.2: (160118) added retrieval of problematic devices;
#            (160126) added 'H' tank attribute in util.plotmes(x)
#   * 1.3.3: (160226) added getindex, tankattrs, linkattr and linkattrs
#   * 1.3.4: (160301) added constants for inverse pb;
#            (160309) added inverse simulation summary;
#            (160318) added added nxxxxattr and nxxxxatrs function for getting attributes by index;
#            (160325) added file quote as needed in save function;
#            (160329) corrected doc (selectlen/select);
#            (160405) corrected doc, added linkXYZV;
#            (160408) utils: strloc, strf3loc
#   * 1.3.5: (160410) added init(folder)
#   * 1.3.6: (160511) added 'symmetric_node' (Ganessa_TH);
#            (160531) reviewed compatibility with dll versions since 2014.
#   * 1.3.7: (160622) added OpenFileMMI classes: SelectModel, SelectFile, ExecStatus;
#            (160706) added 'dist2link'; added 'util.dist_to_poly' as pure python backup;
#                     OpenFileMMI uses simulation interface from caller, or None;
#                     changed all classes to new style;
#                     added 'len' method to 'Selected' and 'Elements'; added 'Graph'
#   * 1.4.0: (160715) setup changed to build whl from source files;
#            (160719) minor bug fix in util.plotmes - reuse same fig in non interactive mode
#   * 1.4.1: (160820) OpenFileMMI SelectFile with null extension; load error handling
#   * 1.4.2: (160830) added AUTO and QUAL storestep constants; minor fix in gencmd;
#                     added include_depth optional attribute to 'linkxyzv';
#            (160915) added version_2016b in the Picwin32 lookup table;
#            (160919) added SelectFolder in OpenFileMMI;
#            (160922) added setlinkattr as a synonym of setbranchattr;
#            (160927) intermediate API for Piccolo6 2016 B (dec-2016)
#   * 1.5.0: (161010) added 'getkeyword';
#            (161019) minor change in util.plotmes: 160719 patch reviewed for better output;
#            (161124) added 'stat_quantiles', 'stat_duration', and 'Dynamic_Stats'
#   * 1.5.1  (161212) bug fix on ts* functions without result file;
#                     added 'retry' optional argument to full_solveH
#   * 1.5.2  (170105) added folder=option in util.list2file
#            (170110) build with numpy 1.11.0 - compatible with
#   * 1.7.0  (170119) build with BIND(C) instead of DEC$ATTRIBUTE C, REFERENCE;
#                     required with ganessa_SIM > 170117 (renamed API functions);
#            (170125) added fixed_interval to tsdevice, now return float values
#   * 1.7.1  (170221) minor changes in util.Inifile (default encoding utf-8);
#                     switch to unicode_literals in sim&th, util and prot;
#            (170223) added compiled util.dist, util.dist_p_seg, util.dist_to_poly
#   * 1.7.2  (170228) added OpenFileMMI.setlanguage function (FR/US or UK);
#            (170304) fix getMinMax/getallminmax break in 1.7.0
#   * 1.7.3  (170313) added WQ, MOD and LNK constants; added DICT.END;
#                     added modulekeyword and attrkeyword;
#            (170331) added shearstr; match Piccolo 2017 --> NO !
#   * 1.7.4  (170407) added silent option to init;
#            (170424) added default '@safege.com' domain to util.envoi_msg
#   * 1.7.5  (170426) improved util.plotmes(x) for horizon > 24h;
#            (170512) added module 'multithread';
#            (170515) fix parent.inidir error in OpenFileMMI; added solveH
#   * 1.7.6  (170613) added constants (STATIC, QUA.VISUSTEP) and util.group;
#                     minor bug fix in Selected, GetMinMax and Dynamic_Stats;
#            (170618) added title to OpenFileMMI.SelectFile and SelectFolder;
#                     added util.pageplot;
#            (170620) replaced litteral symbols with attrkeyword();
#            (170627) match Piccolo 2017 (apr 2017);
#   * 1.7.7  (170705) added cwfold;
#            (170707) optional arg for sim&th.close(arg) and prot.close(arg);
#                     added C1 in util.plotmes for chlorine plots;
#   * 1.7.8pr1 (170808) doc update; upload to pypi
#   * 1.7.8  (170817) replaced IniFile with json/xml version
#   * 1.7.9pr1 (170824) prepared for Piccolo 2017b;
#              (170830) added getunitcoef
#   * 1.8.0 (170907) sim.py split into core, core_sim, core_th; changed/fixed path lookup;
#           (170918) added resfile, raw_getcmdw, raw_stat_duration, raw_stat_quantiles
#   * 1.8.1 (171004) added util.update_package
#   * 1.8.2 (171016) added util.str2uni (tries utf8 the cp1252 - reverse from unistr);
#           (171018) minor bug fix for util.update_package;
#           (171103) added sort.HeapSort class and Graph.dtree
#   * 1.8.3 (171109) added error msg when OpenFileMMI is imported before sim or th;
#           (171110) fix _pyganutl import broken in 1.8.0 (util.dist, util.dist_to_poly);
#           (171114) added multithread.MultiProc class
#   * 1.8.4 (171120) bug fix / changed multithread.MultiProc.run return values as 3 lists
#   * 1.8.5 (171120) added util.plot_close to avoid Fatal Python error at exit;
#           (171128) added linkbbox and util.gbool
#   * 1.8.6 (171201) added progress keyword to parallel.Multiproc; full_version;
#                    added util.send_report
#   * 1.8.7 (171208) fix update_package not succeeding in update 'ganessa'
#   * 1.8.8 (171212) improved update_package proxy configuration using .json files;
#                    added Picwin32.dll lookup into PICCOLO_DIR environment variable;
#                    and '_ck' optional folder suffix
#   * 1.8.9 (171220) updated full_version; added UPN lookup in send_report;
#           (180126) added importEpanet and exportEpanet
#   * 1.9.0 (180227) added con2uni for converting console output to unicode (cp850)
#           (180305) fixes related to 2to3: _getdll: environ; util: winstr and utf,
#                    Inifile encoding, cmp_version, added version_as_tuple;
#           (180328) send_report timeout to 2 seconds, added util.is_text;
#                    2 and 3 compatibility changes for unistr, str2uni, utf2uni, ascii.
#   * 1.9.1 (180418) added a reduce function to parallel.MultiProc; fix seq run
#           (180502) update_package looks for package in current folder
#   * 1.9.2 (180514) fix python3 issue in parallel submodule; minor OpenFileMMI fixes;
#           (180518) fix update_package compatibility with parallel
#   * 1.9.3 (180525) added epanet2 API and dll (py27 only); fix epanet2.getlinknodes;
#           (180530) added util.ws
#   * 1.9.4 (180531) fix utf-8 decoding for Inifile1L;
#           (180604) fix getindex; added exists
#   * 1.9.5 (180607) added epanet2 API and dll (compiled from epanettools 0.4.2);
#           (180608) added an example in README;
#           (180613) plot funcs moved from ganessa.util to ganessa.plot
#   * 1.9.6 (180615) fix sim.init handling non-ascii chars in folder name (uploaded 180621)
#   * 1.9.7 (180705) fix util.IniFile handling non-ascii chars in file name;
#           (180718) fix OpenFileMMI issue with inidir;
#           (180813) added support for Piccolo 2018 (released 2018-07-25) and uploaded
#   * 1.9.8 (180814) 64-bits version for Ganessa_SIM (python 3.6);
#                    minor OpenFileMMI changes (clear_exe, bt_exe_state);
#           (180815) upload wheels for python 3.7 (32 and 64 bits).
#   * 2.0.0 (180816) util.group fix (python 3.7); added verbose param in util.update_package;
#           (180820) added 'wqtracevectsize' for returning the max size of WQ;
#                    concentration vector usable for tracing origin of water;
#           (180823) added geojsonfile for writing to geojson; fix minor midfile issue;
#           (180829) added C:/Program Files lookup in x64 env; geojson reader;
#           (180831) release and upload
#   * 2.0.1 (180910) util.list2file minor fix; doc fix; minor Elements changes;
#           (180919) fix ganessa.th break in 2.0.0;
#           (180924) added orient keyword in ganessa.plot functions; slight behavior change
#   * 2.0.2 (181003) added util.strf2loc; doc update;
#           (181011) minor change in sim.seleclen; added util.call_until_false;
#           (181025) minor fix in ganessa.prot;
#           (181030) release and upload
#   * 2.0.3 (181105) added plot.pageplotx; (13) added '.' at head of prot lookup folders;
#           (181119) changed geojson and midfile to conform to shapefile 2.0;
#           (181203) added '_cl' suffix option to the Piccolo lookup folder;
#                    len for Selected, Elements and derived iterators;
#           (181207) fix util.Inifile1L.save with python 3.x;
#           (181209) doc updated; release and upload
#   * 2.0.4 (181218) debug mode for unicode control; util.Inifile.get returns ustr;
#           (181220) OpenFileMMI.ExecStatus.clear: remove 'all' kwarg;
#                    added len to GetMinMax and DynamicStats iterators
#   * 2.0.5 (181229) added util.perfs;
#           (190107) handle OpenFileMMI.SelectModel(usedef=False);
#           (190109) changes in update_package permission lookup;
#           (190131) release and (190211) upload
#   * 2.0.6 (190411) minor fix in parallel.required_cpu;
#           (190416) minor evolution to parallel.Multiproc: alternate erfun call on Exception;
#           (190423) release and upload
#   * 2.0.7 (190617) added 'extra_data' keyword to sim.savemodel;
#           (190715) added DYNSTOP SimulationError; minor doc fix;
#           (190819) improved simulation error check in full_solveH, solveH, solveTH;
#           (190821) added util.get_python_exe;
#           (191007) minor fix in OpenFileMMI.SelectFile;
#           (191008) release and upload
#   * 2.0.8 (191015) fix README.rst;
#           (200106) added upstream and downstream methods to sim.Graph;
#           (200204) fix new python 3.8 dll directory search;
#                    release and upload (2.7-32 / 3.7 / 3.8 only)
#   * 2.0.9 (200205) fix prot with python 3.8 dll directory search + minor changes;
#                    release and upload (2.7-32 / 3.7 / 3.8 only)
#   * 2.1.0 (200214) fix urllib3 requiring proxy scheme in get_proxy;
#           (200220) Piccolo versions 2017+ required for python 3.x+;
#                    fix to dll directory search, related to FlexLM; fix Example.py;
#                    release and upload (2.7-32 / 3.7 / 3.8 only)
#   * 2.1.1 (200306) new sim.WQsources() iterator;
#           (200313) fix util.scaladjust for range below 1;
#                    fix chlorine (C1) plot.plotmes(x);
#           (200314) add added util.is_wq and sim.wqtslen; fix sim.tsval for WQ TS;
#           (200323) doc fixes; add module constant KW (MOD kw, QUA, INV);
#                    add optional return_type=True kw to sim.Selected;
#           (200324) fix workdir & result file in virtualstore;
#                    release and upload (2.7-32 / 3.7 / 3.8 only)
#   * 2.1.2 (200506) add util.IniFile.remove;
#           (200511) release and upload (2.7-32 / 3.7 / 3.8 only)
#   * 2.1.3 (200603) plot.plotmes: single (static) measurement plotted as an horizontal line;
#           (200604) OpenFileMMI.SelectModel: chdir to model folder to allow relative inner read;
#           (200619) added en2emu sim-like minimal compatibility module;
#           (200622) added nbvertices() and fake get_labels();
#           (200629) release and upload (2.7-32 / 3.7 / 3.8 only)
#   * 2.1.4 (200708) dll lookup in '.';
#           (200819) minor fix on plot.pageplot;
#                    release and upload (2.7-32 / 3.7 / 3.8 only)
#   * 2.1.5 (200824) replace util.ascii with util.myascii;
#           (200915) plot.pageplot(x) allows multiple ts per graph; fix cmdfile;
#           (200922) added demand profile query by zone and code/zone (tsdemand);
#           (201109) added util.read_as_idpic;
#           (201119) release and upload (2.7-32 / 3.7 / 3.8 only)
#   * 2.1.6 (201221) fix prot error with null path chunks;
#           (201222) fix Ganessa_TH integration not working properly;
#           (210126) added util.split_poly_at; release and upload
#   * 2.1.7 (210301) plot.plotmes(x) plot tank bottom and top water level when prefixed with '=';
#           (210307) addl single value plot as horizontal line in plot.pageplot;
#           (210310) add util.utf8_bom_encoding(file);
#           (210324) fix util.split_poly_at ValueError: not enough values to unpack (expected 3, got 2);
#                    release and upload (2.7-32 / 3.7 / 3.8 only)
#   * 2.1.8 (210325) added Graph.pop and len(Graph); added SelectModel.update_info;
#                    fix missing .pyd components resulting in suboptimal use of the API;
#                    release and upload (2.7-32 / 3.7 / 3.8 / 3.9)
#   * 2.1.9 (210426) util.IniFile removes the -<maxvers><minvers> suffix on param save;
#           (210428) prot now seek extensive paths incl. ../SafProdLicMgr, C:/Logiciels etc.;
#           (210429) fix geojson writer (use Transformer, swap return coords);
#           (210430) release and upload (2.7-32 / 3.7 / 3.8 / 3.9) - last 2.7 release
#   * 2.2.0 (210506) fix pypi doc; change _fresult and _workdir lookup;
#           (210517) minor changes to util.strf3 and strf2
#           (210527) fix Ws10 using utf8 rather than cp1252 in util
#           (210531) release and upload (3.7 / 3.8)
#   * 2.2.1 (210609) util.send_report include OS version
#           (210610) OpenFileMMI.SelectFile: invisible contour & parent cascade for subframe
#           (210614) Add %localappdata%/Programs/Safege & Suez... to the search path
#           (210616) Add Inetum to the lookup folders for Piccolo
#           (210617) Add update_info(-1) to OpenFileMMI.SelectFile
#           (210618) release and upload (3.7 / 3.8); (210621) upload (3.9) - not passed
#   * 2.2.2 (210621) Add %localappdata%/Programs/Gfi Progiciels & Inetum to the search path
#           (210621) fix README.rst; release and upload (3.7 / 3.8 / 3.9);
#   * 2.2.3 (210623) Minor fix to OpenFileMMI.SelectModel.update_info(-1);
#           (210624) Added IsolatedNodeSimulationError exception;
#           (210701) lookup 'Inetum' folder before 'Gfi Progiciels'; addl TS for plot.plotmes
#           (210702) release and upload 32 (3.5 / 3.6 / 3.7 / 3.8) and 64 (3.7 / 3.8)
#   * 2.2.4 (210705) fix dll search path order with D: partition
#           (210723) OpenFileMMI.SelectModel silent read .dat by default
#           (210819) Handling of python embedding into dll caller (Piccolo.exe) - beta
#           (210823) add sim.is_embedded()
#           (210901) add sim.dll_version() from API = not requiring init(); release and upload (3.8 / 3.9)
#   * 2.2.5 (210913) adaptation to python 3.10;
#           (210914) plot changes (uses- axes and figures rather than default pyplot funcs);
#           (210927) fix util.get_proxy doc and return value;
#           (210929) fix getvar truncate output to 48 (now 256); add model_filename(); util.update_package exits in embedded mode.
#           (211004) OpenFileMMI.SelectModel kwarg show_emb=False hides dialog in embedded mode;
#           (211012) util.Inifile kwarg folder=None allows load/save to alternate location;
#           (211013) OpenFileMMI.SelectModel fix chdir error when filename has no dirname;
#           (211020) add OpenFileMMI.SelectFile.setfilename;
#           (211026) add fname property to OpenFileMMI.SelectFile, SelectModel, SelectFolder;
#           (211027) release and upload (3.8 / 3.9 / 3.10)
#   * 2.2.6 (211028) add OpenFileMMI.SelectFolder.add_extra_info; .fname setter;
#           (211106) add type hint to most functions;
#           (211109) fix _dll_version in embedded mode;
#           (211112) add emb_model_folder() function;
#           (211116) minors changes in OpenFileMMI; new util.piccolo_context function for color settings;
#           (211117) release and upload (3.8 / 3.9 / 3.10)
#   * 2.2.7 (211124) fix is_wq() for water hardness (TH or HD or DU); setlang accepts 1 or 2 letter arg;
#           (211126) OpenFileMMI.add_extra_model_info append to previous line if returned text starts with backspace \b;
#           (211216) refdate returns (unicode) str;
#           (211230) release and upload (3.8 / 3.9 / 3.10)
#   * 2.2.8 (220128) fix util compatibility with windows servers;
#           (220203) dll lookup on E: if it exists and D: does not;
#           (220203) release and upload (3.8 / 3.9 / 3.10) (should have done it yesterday !)
#   * 2.2.9 (220211) fix non ascii str passed to Selected must be bytes2;
#           (220214) fix util.update_package: replace -use-binary with -prefer-binary; -trusted-host pypi.org;
#           (220222) release and upload (3.8 / 3.9 / 3.10)
#   * 2.3.0 (220304) fix plot.pageplot[x] issue with python 3.9+ (ax.title); (220309) tune xscale for t < 1h;
#           (220318) fixed _getdll.AddDllDirectory to allow more than 1 call / close in any order;
#           (220324) WQSources return str;
#           (220419) allow multiple init / close (reloads the dll)
#           (220420) add Selectid(xxx) for Selected(xxx, return_type=False)
#           (220421) minor change to [E:| D:], C: lookup; release and upload (3.8 / 3.9 / 3.10)
#   * 2.3.1 (220428) added proj.FrenchProjMapping to handle symbolic / EPSG mapping
#           (220505) added proj.get_spatial_ref to get SPATIAL-REF from .dat
#           (220701) added SelectFile.set_rw_mode(x) allowing to change read/write mode
#           (220706) added SelectFile(allow_reset=False) creates a button calling .clearfilename()
#           (220719) added util.strf4
#           (220720) added TableValues iterator for getting values from tables
#           (220721) added implemented(func_or_iter_name) for checking availability
#           (220802) release and upload (3.8 / 3.9 / 3.10)
#   * 2.3.2 (220804) added linkattrv, tankattrv getters for array attributes
#           (220810) added util.FichInfo.sub_module: used in banner() and send_report
#           (220820) added Controls iterator (220821) extended with control entities
#           (220823) plot.plotmes savefig DPI doubled to 300; always write ID (name) on 2 lines if too long
#           (220824) ControlEntities iterator
#           (220829) modified Controls to return ControlId and ControlData; added command_logger
#           (220831) added 2021 and 2022 Picwin32.dll version lookup
#           (220831) release and upload (3.8 / 3.9 / 3.10)
#   * 2.3.3 (220902) added CommandLogger.logs to handle non unicode multi word in cmdfile
#           (220909) add 3rd optional arg to getcalind
#           (220920) minor fixes in OpenFileMMI.SelectFile; build wheel for 3.11-64
#           (220923) add inv_varcount, inv_variable, and IPSVariable iterator
#           (220927) release and upload (3.8 / 3.9 / 3.10 / 3.11)
#   * 2.3.4 (221010) plot.plotmes prefix title with file basename; add Graph.extended_segment; doc update
#           (221103) fix util.quotefilename causing an exeption when a null string is passed
#           (221110) add Graph.antennas and sort.HeapSort.modify
#           (221110) release and upload (3.8 / 3.9 / 3.10 / 3.11)
#   * 2.3.5 (221111) add SupplyNodes() iterator
#           (221129) add util.csv_with_tabs
#           (221213) util.gbool: added "ko" and "x" as False
#           (221221) release and upload (3.8 / 3.9 / 3.10 / 3.11)
#   * 2.3.6 (230206) tsvals: efficent retrieval of multiple TS
#           (230207) util.update_package: added --trusted-host files.pythonhosted.org and --use-feature=truststore
#           (230218) add proj.get_transformer and proj.get_transformer
#           (230220) add proj.to_epsg and proj.to_symbolic
#           (230221) release and upload (3.8 / 3.9 / 3.10 / 3.11)
#   * 2.3.7 (230224) add "null" FrenchProjMapping
#           (230311) add xkcd style handling in plot.plotmes(x) and plot.pageplot(x)
#           (230320) add pic.attrname and pic.attrindex (requires Ganessa_SIM >= 230320); add compatibility with recent but not last version of Ganessa_SIM
#           (230322) plot.plotmes handles non ascii chars (débit, réservoir, m³/h) but this help file does not ?!
#           (230327) minor changes to (Table and) TableValues returning demand coefs (requires Ganessa_SIM >= 230328)
#           (230330) Selectid/Selected returns empty iterator for blank selection
#           (230331) release and upload (3.8 / 3.9 / 3.10 / 3.11)
#   * 2.3.8 (230404) fix _getdll.AddDllDirectory use when path is empty (embedded case); fix Writer.field() 4th arg in midfile and geojsonfile
#           (230413) proj.guess_proj calls get_spatial_ref in module mode
#           (230419) add ganessa version in send_report
#           (230502) tsvals: change return order to allow building a dict from return value
#           (230511) plot.pageplot allow plotting more than 2 TS per plot
#           (230623) add compiled util.shearstress for direct shearstress calculation
#           (230626) fix epanet2.solveH() fail to use temp bin file; fix epanet2 computation of tank diameter
#           (230710) fix minor issues in util.roundval and util.scaladjust
#           (230712) added epanet22 API and dll (integration manually transposed from epanettools 0.4.2)
#           (230809) added owa_epanet22 providing epanettools compatibility for owa-epanet
#           (230817) release and upload (3.8 / 3.9 / 3.10 / 3.11)
#   * 2.3.9 (230908) add .get() alias to .getfilename() / .getfoldername() in OpenMMI classes
#           (230922) "default project" management in owa_epanet22, for multiprocessing purpose
#           (231002) updated en2emu and OpenFileMMI to basic handling of Epanet .inp File
#           (231004) updated sim.update_package to seek importlib.metadata.version
#           (231017) updated en2emu with extensions, doc; improved html doc
#           (231018) release and upload (3.8 / 3.9 / 3.10 / 3.11)
#   * 2.3.10
#           (231025) updated en2emu with WQ simulation and changes in epanet project
#           (231106) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12)
#   * 2.4.0
#           (231114) add Controls.__len__
#           (240112) handle en2emu error loading .inp model (non-ascii filename), catch it in OpenFileMMI.SelectModel
#           (240115) minor improvement in en2emu.ENmodel.save_as: keep comments after changed section header
#           (240116) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12)
#   * 2.4.1 (240307) add util.get_this_python_display_name
#           (240412) added MonteMario projection in proj.FrenchProjMapping
#           (240418) added util.profilise_folder and util.user_writeable, used by FichInfo and IniFile
#           (240503) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12)
#   * 2.4.2 (240611) review util.get_this_python_display_name lookup
#           (240613) added pygansim2023.pyd for use with 2023 and later Picwin32.dll
#           (240616) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13)
#   * 2.4.3 (240625) fix OpenFileMMI.SelectFile use when ganessa.sim not imported
#           (240702) send_report includes python exe name
#           (240702) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13)
#   * 2.4.4 (240702) fix path split in util.profilise_folder ("." case)
#           (240704) numpy < 2.0 required for ganessa < 2.4.4 or python < 3.12
#           (240715) util.user_writeable check uses a tempfile in case of parallel runs
#           (240717) added Pipes([*attrs]) iterator
#           (240718) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13)
#   * 2.4.5 (240724) util.send_report sender lookup
#           (240808) change dependancy numpy < 2.0 if python < 3.13;
#           (240808) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13)
#   * 2.4.6 (240809) plot.plotmes[x] labels keyword for ("simulation, "Reference")
#           (240810) add optional arg name[="autre"] to proj.to_symbolic
#           (241030) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13)
#   * 2.4.7 (241219) parallel.MultiProc.run_sequential calls term if defined
#           (250107) added linknodes function that returns 'from' and 'to' nodes
#           (250108) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13)
#   * 2.4.8 (250131) added script full path to util.send_report content
#           (250210) added Graph.antennas(strict=True) optional keyword
#           (250211) change profilise_folder to operate when folder not in users;
#                    user_writeable also force profilise when folder name starts with "program";
#                    PYTHON_FROZEN constant; update_package exits with unmatch and frozen/embedded python
#           (250213) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13)
#   * 2.5.0 (250220) fixed util.is_folder_writeable for parallel use
#           (250225) added util.hhmmssd: hour with fractional seconds; sim.all_ts: return all
#                    TS for the given attribute, exact results with Ganessa_SIM >= 250225;
#                    hresults_block and hresults_block_xtra.
#           (250226) vectorise util.tsadd and add shape parameter ("constant, "linear")
#           (250127) add demand_pressure: demand/pressure related parameters
#                    and code_pressure: activation of demand pressure for a code.
#                    (ganessa_sim API only)
#           (250303) doc fixes.
#           (250303) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13)
#   * 2.5.1 (250306) Extend sort.HeapSort with key_index option; rename HeapSortRank; move
#                    key option to HeapSortFunc; add Graph.wtree and Graph.path; fix Graph.dtree.
#           (250310) include '_pygansim2025' in dll lookup (demand_pressure and code_pressure);
#                    fix proj with MonteMario vs rgf-ccxx recognition; minor improvements in
#                    OpenFileMMI (parent.v1 and parent.finalise optional, new get_info method).
#           (250325) fix issues in midfile and geojsonfile (Readers); compliance with shapefile.
#           (250327) build '_pygan_th2025.pyd' and include it in dll lookup.
#           (250401) proj.FrenchProjMapping simplified as dict subclass.
#           (250403) en2emu.is_embedded and .resfile required when no Picwin32/ganessa_Sim.dll.
#           (250403) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13)
#   * 2.5.2 (250407) fix getcalind: _dll_api.dll_version() undefined with dll jan-2022.
#           (250410) fix en2emu reset / loadbin issues.
#           (250416) fix core_th: Callable typo (250402) disabling its use in 2.5.1.
#           (250422) added SIM suffix as an alternative for language (dll lookup)
#           (250422) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13)
#   * 2.5.3 (250424) Graph is a subclass of (link) dict; pop is replaced with pop_link.
#           (250506) allow use of non compiled side modules with non-Windows platforms
#           (250619) fix _getdll missing weird configuration handling; added result_filename;
#                    OpenFileMMI.SelectModel(ext="bin") use result_filename in embedded mode.
#           (250626) added OpenFileMMI.ask_for_single_input; OpenFileMMI.SelectFile use
#                    model_filename + any exts in embedded mode, if file exists.
#           (250630) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13)
#   * 2.5.4 (250709) fix tsval and tsvals with WQ attribute; fix tsvals typing;
#                    allow tsvals to be called with a list of ids or a list of indices.
#           (250814) fix init and setlang clear IsolatedNodeError in embedded mode
#           (250824) added "Suez" as legacy folder for Piccolo6 in Program Files (x86)
#           (250830) release and upload (3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13)
#   * 2.5.5 (2509xx) to be continued
#****
