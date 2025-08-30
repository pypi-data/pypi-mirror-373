'''
Created on 7 sept. 2017

@author: Jarrige_Pi

Determines where and which Picwin32 or Ganessa_SIM dll to use

17.12.12: added optional _ck suffix, added PICCOLO_DIR envt variable
18.08.27: added Program Files for x64 environment
20.02.04: use add_dll_directory with python 3.8+ instead of path
08.07.20: replace '.' with os.getcwd()
16.06.21: add %localappdata% and remove D: if not available
17.06.21: uses Piccolo_(lang) for Safege/Suez and Piccolo6_(lang) for Gfi/Inetum
05.07.21: fix %localappdata% on C: not found when D: partition mounted
19.08.21: test/manage call from embedding exe
15.04.22: add .activefield to AddDllDirectory
15.04.22: add .dll, .pyd, .embedded to AddDllDirectory; remove gandir and f return args from _getdllinfo
31.08.22: added 2022 and 2021 lookup of Picwin32.dll
16.06.24: added 2023 lookup of Picwin32.dll
10.03.25: added 2025 lookup of Picwin32.dll
27.03.25: added 2025 lookup of Picwin32.dll for Picalor/Frigolo
22.04.25: added SIM suffix as an alternative for language (target Ganessa_SIM)
24.08.25: added "Suez" as legacy folder for Piccolo6 in Program Files (x86)

'''
from typing import AnyStr

from importlib import import_module
from itertools import product, chain
from sys import modules as sys_modules
from sys import version_info
import builtins

USE_ADD_DLL = version_info[0:2] >= (3, 8)
from os import environ, getcwd
import os.path as OP
if USE_ADD_DLL:
    from os import add_dll_directory
# ganessa_emb_ is defined by embedding python
try:
    from ganessa_emb_ import full_path
except ImportError:
    full_path = False

debuglevel = 0

# def tostr(input_str: AnyStr) -> str:
#     '''converts to unicode'''
#     if isinstance(input_str, builtins.str):
#         return input_str
#     elif isinstance(input_str, builtins.bytes):
#         for codec in ('cp1252', 'utf-8', 'cp850', 'iso-8859-1'):
#             try:
#                 return str(input_str, codec)
#             except UnicodeError:
#                 continue
#     else:
#         return str(input_str)

class AddDllDirectory:
    '''Context manager class with a close() method'''
    def __init__(self, ndir, dll=""):
        ''' inserts ndir into the windows search path
        required even with add_dll_directory because of activation lib
        dll is not directly used here but serves as persistance of dll name for caller
        '''
        ndir = getcwd() if ndir == '.' else ndir
        self.dir = ndir
        self.dll = dll
        self.pyd = ""
        self.embedded = False
        self.path_modified = False
        self.add_dll_dir = None
        self.open()
        self.active = True

    def open(self):
        '''reopen'''
        self.path_modified = self.dir.lower() not in unistr(environ['path']).lower().split(';')
        self.add_dll_dir = add_dll_directory(self.dir) if USE_ADD_DLL and self.dir else None
        self.active = True
        if self.path_modified:
            if debuglevel > 2:
                print(environ['path'])
            environ['path'] += ';' + ws(self.dir)
            if debuglevel:
                print(ws(f'\tFolder "{self.dir}" added to PATH environment variable'))

    def close(self):
        '''remove last path'''
        self.active = False
        if self.add_dll_dir is not None:
            self.add_dll_dir.close()
            self.add_dll_dir = None
        if self.path_modified:
            chunks = environ['path'].split(';' + ws(self.dir))
            environ['path'] = "".join(chunks)
            assert len(chunks) > 1
            if debuglevel:
                print(ws(f'\tFolder "{self.dir}" removed from PATH environment variable'))
            self.path_modified = False

    def get_api(self):
        '''Imports and returns the pyd sub module'''
        if self.pyd:
            return import_module('.' + self.pyd, package='ganessa')
        raise ImportError

    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()
        return True

from ganessa.util import unistr, ws, X64

class EnvSearchError(Exception):
    '''Custom exception'''
    pass


def _import_ganessa(f, bth, dlls, test=True):
    '''Search for the most recent version of ganessa compatible dll: 
    Ganessa_SIM.dll or Picwin32.dll'''
    # utility function for testing API in turn
    def check_dlls(pydlls, pkg='ganessa'):
        for pydll in pydlls:
            try:
                mod = import_module('.' + pydll, package=pkg)
                if debuglevel > 2:
                    print(f, 'FIT', pydll)
                break               # found -> stop iteration
            except ImportError:
                if debuglevel > 2:
                    print(f, 'do not fit', pydll, '; mode=', 'test' if test else 'activation')
                continue
        else:
            # sequence exhausted w/o finding a suitable dll
            raise ImportError
        return mod, pydll

    try:
        if debuglevel > 1:
            print("Checking family:", f)
        if f == dlls[1]:
            # look for Picwin32 - no specific 2019 and 2024 API
            pydlls = ('_pygan_th2025', '_pygan_th2021', '_pygan_th2018',
                      '_pygan_th2017', '_pygan_th2016', '_pygan_th2015',
                ) if bth else (
                      '_pygansim2025', '_pygansim2023', '_pygansim2022',
                      '_pygansim2021', '_pygansim2020', '_pygansim2018b',
                      '_pygansim2018', '_pygansim2017b', '_pygansim2017',
                      '_pygansim2016b', '_pygansim2016a', '_pygansim2016',
                      '_pygansim2015', '_pygansim2014')
            mod, pydll = check_dlls(pydlls)
        elif f == dlls[0]:
            # look for Ganessa_xxx
            pydlls = ('_pygan_th',) if bth else ('_pygansim', '_pygansim_alt')
            mod, pydll = check_dlls(pydlls)
        else:
            print("Unexpected dll mismatch", f, "#", " ".join(dlls))
            return False if test else (None, "")
    except ImportError:
        if debuglevel > 0:
            print('\t', f, 'error; mode=', 'test' if test else 'activation')
        return False if test else (None, "")
    else:
        if debuglevel > 0:
            print(f, 'is OK for use with', pydll, '; mode=', 'test' if test else 'activation')
        if test:
            del mod
            return True
        print('  --->  using interface <', pydll, '> for ', f, sep="")
        return mod, pydll

def _getdllinfo(bth):
    ''' Locates the simulation kernel - picwin32.dll or Ganessa_xx.dll
        in an expected folder and ensures that an appropriate .pyd
        interface exists (EnvSearchError)

        Folder are looked up in the following order:
        - GANESSA_DIR environment variable for Ganessa_xx.dll
        - folder list from PATH environment variable for either dll
        - default installation folders for Piccolo and Picalor
        - for FR, SIM, esp, eng and optionally _ck
    '''
    dlls = ('Ganessa_TH.dll' if bth else 'Ganessa_SIM.dll', 'Picwin32.dll')

    if full_path:
        emb_path = full_path()
        if debuglevel:
            print("Path is:", emb_path, " * length:", len(emb_path))
        gandir, f = OP.split(emb_path)
        if debuglevel:
            print('>> Using embedded:', gandir, f)
        to_close = AddDllDirectory(gandir, f)
        mod, pyd = _import_ganessa(f, bth, dlls, test=False)
        if mod:
            to_close.pyd = pyd
            to_close.embedded = True
            return mod, to_close
    else:
        if debuglevel:
            print('>> Embedding not found')

    # first examine GANESSA_DIR and PICCOLO_DIR
    for ganessa_dir, f in zip(('GANESSA_DIR', 'PICCOLO_DIR'), dlls):
        if ganessa_dir in environ:
            gandir = unistr(environ[ganessa_dir])
            if OP.exists(OP.join(gandir, f)):
                print(f, 'found in environment variable', ganessa_dir, end=' ')
                with AddDllDirectory(gandir):
                    if _import_ganessa(f, bth, dlls):
                        print(' :-)')
                        break
                    print(' but *NOT* responding !')
            else:
                print(f, ' ** NOT ** found in environment variable', ganessa_dir)
    else:
        # if none succeeds examine PATH variable
        for gandir, f in product(unistr(environ['path']).split(';'), dlls):
            if OP.exists(OP.join(gandir, f)):
                if debuglevel > 0:
                    print(ws(f + ' found in Path: ' + gandir))
                with AddDllDirectory(gandir):
                    if _import_ganessa(f, bth, dlls):
                        break
        # finally check default installation paths
        else:
            if debuglevel:
                print(' * no dll found in PATH environment variable folders')
            # then default installation folders:
            # (drive) (program folder) (editor name) (software_lang) (dll)
            PROG5 = '\\Program Files'
            PROG6_x64 = environ.get('ProgramW6432', '/Program Files')
            PROG6_x32 = environ.get('ProgramFiles(x86)', '/Program Files (x86)')
            PROG_USR = OP.join(environ['LOCALAPPDATA'], 'Programs')
            # Piccolo folder is Piccolo_lang for Safege and Piccolo6_lang for Gfi/Inetum
            picfldr = 'Picalor_' if bth else 'Piccolo_'
            dpesn = tuple((PROG_USR, saf, name, idx) for saf, (name, idx) in
                    product(("Safege", "Suez"), (('Ganessa_', 0), (picfldr, 1))))
            dpesn += tuple((PROG_USR, gfi, 'Piccolo6_', 1) for gfi in ('Inetum', 'Gfi Progiciels'))
            pesn = tuple((PROG6_x32, saf, 'Ganessa_', 0) for saf in ("Safege", "Suez"))
            if X64:
                pesn += tuple((PROG6_x64, saf, 'Ganessa_', 0) for saf in ("Safege", "Suez"))
            else:
                picfldr = 'Picalor6_' if bth else 'Piccolo6_'
                pesn += tuple((PROG6_x32, gfi, picfldr, 1) for gfi in ("Suez", 'Inetum', 'Gfi Progiciels'))
                if not bth:
                    pesn += ((PROG5, 'Adelior', 'Piccolo5_', 1),)
            if OP.exists('E:/'):
                partition = ('E:', 'C:')
            elif OP.exists('D:/'):
                partition = ('D:', 'C:')
            else:
                partition = ('C:',)

            ppesn = ((d + OP.splitdrive(p)[1], e, s, n)
                        for d, (p, e, s, n) in product(partition, pesn))
            # Main folder lookup loop
            for p, e, s, n in chain(dpesn, ppesn):
                folder = OP.join(p, e)
                if not OP.exists(folder):
                    if debuglevel > 1:
                        print('...skipping non-existent folder', folder)
                    continue
                # Suffix lookup loop
                for l, k in product(('FR', "SIM", 'esp', 'eng', 'UK'), ("", '_ck', '_cl')):
                    f = dlls[n]
                    gandir = OP.join(folder, s + l + k)
                    if debuglevel > 1:
                        print(' ... examining ' + gandir + '/' + f)
                    if not OP.exists(OP.join(gandir, f)):
                        continue
                    with AddDllDirectory(gandir):
                        if debuglevel > 0:
                            print(' ... testing ' + gandir + '/' + f)
                        if _import_ganessa(f, bth, dlls):
                            if debuglevel > 0:
                                print(f + ' responding from ' + gandir)
                            del p, e, s, l
                            break
                        print(ws(f + ' found in ' + gandir + ' but *NOT* responding'))
                else:
                    # Not found with suffixes -> continue main folder lookup
                    continue
                # Found with l & k suffix - break folder loop
                break
            else:
                # Not found
                raise ImportError('Unable to find an adequate '+ ' or '.join(dlls))

    # dll found and API OK: finalise the import
    # with AddDllDirectory(gandir):
    #     mod = _import_ganessa(f, bth, dlls, test=False)
    # context will be closed after call to init.
    to_close = AddDllDirectory(gandir, f)
    mod, pyd = _import_ganessa(f, bth, dlls, test=False)
    to_close.pyd = pyd
    return mod, to_close

class _LookupDomainModule:
    def __init__(self):
        for item in ('ganessa.sim', 'ganessa.th', 'ganessa.en2emu'):
            if item in sys_modules:
                self.name = item
                self.module = sys_modules[item]
                break
        else:
            self.name = ""
            self.module = None
            print(' ***\n *** CAUTION *** if used, ganessa.sim or .th should be imported',
                  ' before .OpenFileMMI- Please inform piccolo@safege.fr\n ***')

    def is_th(self):
        '''Returns True if called from ganessa.th'''
        return self.name.endswith('th')
