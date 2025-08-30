"""Projection mapping for French area
Utility fuction for guessing projection from (median) X and Y coords
Utility function for retrieving CRS from model
Utility for building a transformer from from and to projs"""
import os.path as OP
import re

#****g* ganessa.proj/functions_proj
#****
#****g* ganessa.proj/Classes_proj
#****

#****o* Classes_proj/FrenchProjMapping
# PURPOSE
#   Provides and maintains a bijective dict of symbolic -> EPSG usual French CRS.
# SYNTAX
#   projs = FrenchProjMapping()
# METHODS
#   * dict methods: keys(), values(), items(), __getitem__, __setitem__
#   * item.epsg2symb(epsg: str, default="autre"): returns the symbolic name
#     associated with the given EPSG. Inserts it if not yet present, with the
#     symbolic name given as default.
#   * __setitem__ maintains the bijectivity of the dict and remove any
#     other key with the same value.
# REMARK
#   Initial dict values are available as FrenchProjMapping().
#   They include wgs84, various lambert systems for French Metropolitan,
#   utm20n (Martinique and Guadeloupe), rgaf09 (Martinique), utm40s (la Reunion),
#   utm22n (Guyanne), and macao
# HISTORY
#   * new in 2.3.1 (220802)
#   * 2.3.2 (220802) this doc has been added
#   * 2.3.6 (230217) added Tananarive Laborde grid approx for Madagascar
#   * 2.4.1 (240412) added Milano
#   * 2.5.1 (250401) simplify as a dict subclass
#****
_VOID, _VOID_EPSG = "", ""
class FrenchProjMapping(dict):
    """Mapping symbolic name to / EPSG:xxxx"""

    def __init__(self) -> None:
        self.update({
            _VOID: _VOID_EPSG,
            "wgs84": "EPSG:4326",  # geoCRS 2D
            "lamb93": "EPSG:2154",  # RGF93 / Lambert93 (projCRS)
            "rgf93": "EPSG:4171",  # RGF93 2D
            "lambN": "EPSG:27561",
            "lambC": "EPSG:27562",
            "lambS": "EPSG:27563",
            "lambCorse": "EPSG:27564",
            "ntf": "EPSG:4275",
            "ntfparis": "EPSG:4807",
            "lamb1": "EPSG:27571",
            "lamb2": "EPSG:27572",
            "lamb3": "EPSG:27573",
            "tananariveLaborde": "EPSG:29702", # Madagascar Laborde Grid Approximation
            "utm20n": "EPSG:4559",  # Martinique - Guadeloupe
            "rgaf09": "EPSG:5490",  # Martinique RGAF09 (EPSG5490).
            "utm40s": "EPSG:2975",  # Réunion
            "utm22n": "EPSG:2972",  # Guyanne
            # 'autre': "EPSG:0000",
            "MonteMario": "EPSG:3003", # Milan
            "macao": "EPSG:8433",
            # 'macau': b'+ellps=intl +proj=tmerc +lat_0=22.212222 +lon_0=113.536389 +k=1.000000 +x_0=20000.0 +y_0=20000.0 +units=m'
            "macau": "+ellps=intl +proj=tmerc +lat_0=22.212222 +lon_0=113.536389 +k=1.000000 +x_0=19685.0 +y_0=20115.0 +units=m",
        })
        self.inv_map = {v: k for k, v in self.items()}
        for lat in range(42, 51):
            self["rgf93-cc" + str(lat)] = f"EPSG:{3900+lat:4d}"

    # def __getitem__(self, symb: str, owner=None) -> str:
    #     """epsg getter"""
    #     return self[symb]

    def __setitem__(self, symb: str, value: str) -> None:
        """epsg setter - remove duplicates"""
        if symb and value:
            value = value.upper()
            if symb in self:
                del self.inv_map[value]
            if value in self.inv_map:
                del self[symb]
            super().__setitem__(symb, value)
            self.inv_map[value] = symb

    # def keys(self):
    #     """Returns symbolic CRS as keys"""
    #     return self.keys()

    # def values(self):
    #     """Returns CRS as values"""
    #     return self.values()

    # def items(self):
    #     """Returns key, CRS items"""
    #     return self.items()

    def epsg2symb(self, epsg: str, default=_VOID) -> str:
        """Returns symb associated to epsg if present; or 'autre'"""
        if not epsg or epsg == _VOID_EPSG:
            return _VOID
        epsg = epsg.upper()
        if epsg not in self.inv_map and default:
            # self.__setitem__(default, epsg)
            self[default] = epsg
        return self.inv_map[epsg]


#****f* functions_proj/guess_proj, to_epsg, to_symbolic
# PURPOSE
#   Determines the CRS (projection) amongst usual French CRS
# SYNTAX
#   * name_or_epsg = guess_proj(point_or_module, as_epsg)
#   * epsg = to_epsg(name)
#   * name = to_symbolic(epsg)
# ARGUMENT
#   * Union[Tuple(float, float), module] point_or_module: either a x, y point or
#     ganessa.sim module. In the latter case, the median X and Y node coordinates are retrieved.
#   * bool as_epsg: if True, returns the EPSG CRS, otherwise returns the symbolic name
#   * str name: symbolic name
#   * str epsg: EPSG:xxxx
# RESULT
#   str name_or_epsg: EPSG:xxxx or symbolic name, depending on the value of as_epsg:
#   * if True, returns the guess of EPSG:xxxx CRS
#   * if False, returns one of "wgs84", "lambCorse", lambN", "lamb93", "rgf93-ccll"
#     where 42 <= ll <= 50, "utm20n", "utm22n", "utm40s", "tananariveLaborde" etc.
# EXAMPLE
#   guess_proj((646464.64, 6868686.8), True) should return EPSG:2154
# HISTORY
#   * new in 2.3.1 (220802)
#   * 2.3.2 (220802) this doc has been added
#   * 2.3.6 (230220) added to_epsg and to_symbolic
#   * 2.3.7 (230223) fix guess_proj w/o returning "autre" causing KeyError in as_epsg()
#   * 2.3.8 (230413) guess_proj calls get_spatial_ref in module mode
#   * 2.4.1 (240412) added MonteMario as alternative of rgf93-ccxx if defined
#   * 2.4.6 (240810) added optional arg name[="autre"] to to_symbolic
#   * 2.5.1 (250307) fix MonteMario / rgf-cc recognition
#****
_french_proj_mapping = FrenchProjMapping()

def guess_proj(point_or_module, as_epsg: bool = False) -> str:
    """Projection guess according to an x, y point or average model coords"""
    if isinstance(point_or_module, (tuple, list)):
        x, y, *_ = point_or_module
    else:
        # get median coords from the model
        pic = point_or_module
        if not pic.nbobjects(pic.NODE):
            return _VOID_EPSG if as_epsg else _VOID
        # Check if CRS defined and return it
        try:
            model = point_or_module.model_filename()
        except AttributeError:
            model = ""
        if (crs := get_spatial_ref(point_or_module, model)) and "#" not in crs:
            return crs if as_epsg else _french_proj_mapping.epsg2symb(crs, "autre")
        x = float(pic.getvar("Q50:NOEUD.X"))
        y = float(pic.getvar("Q50:NOEUD.Y"))

    if x < 1_200_000:
        if x < 180 and y < 85 or y < 180 and x < 85:
            theprj = "wgs84"
        elif y < 600_000:
            if x < 350_000:
                theprj = "lambCorse"
            else:
                theprj = "lambN"
        elif 1_556_576 < y < 1_589_155:
            theprj = "rgaf09"
        elif y < 2_707_000:
            theprj = "lamb2"
        else:
            theprj = "lamb93"
    else:
        # lambert CC42 a 50, ou MonteMario
        if (1_290_651 < x < 2_343_702) and (4_190_306 < y < 5_261_004) and (
            (mm := "MonteMario") in _french_proj_mapping):
            theprj = mm
        else:
            theprj = "rgf93-cc" + str(42 + (int(y) - 700_000) // 1_000_000)
    return _french_proj_mapping[theprj] if as_epsg else theprj

def to_epsg(theprj: str) -> str:
    """Returns the EPSG associated to a mnemonic"""
    return _french_proj_mapping[theprj]

def to_symbolic(epsg: str, name="autre") -> str:
    """Returns the EPSG associated to a mnemonic"""
    return _french_proj_mapping.epsg2symb(epsg, name)

#****f* functions_proj/get_spatial_ref
# PURPOSE
#   Query or retrieves the spatial ref from the (current) model
# SYNTAX
#   crs_name = get_spatial_ref(pic_module [, model_file])
# ARGUMENT
#   * module pic_module: ganessa.sim module
#   * str model_file: optional name of the model file
# RESULT
#   Name of the CRS as defined in the Piccolo models as "SPATIAL-REF" command
# REMARKS
#   * Before 2022-02-14 Piccolo and Ganessa_SIM API do not return SPATIAL-REF;
#     in this case SPATIAL-REF is searched in the file model_file with extension replaced with .dat or .pic
#   * Return value can be a blank str "" if SPATIAL-REF is not defined, or "#NAN#"
#     for old API or non-existing model_file or SPATIAL-REF not defined in the file.
# HISTORY
#   * new in 2.3.1 (220802)
#   * 2.3.2 (220802) this doc has been added
#****
def get_spatial_ref(pic_module, model_file: str = "") -> str:
    """Returns model CRS (spatial-ref)"""
    crs = pic_module.getvar("SPATIAL-REF")
    if crs and "#" not in crs:
        return crs
    # if getvar not implemented, try finding SPATIAL-REF in model file
    model_name, model_type = OP.splitext(model_file)
    if model_type.lower() == ".bin":
        for mtype in (".dat", ".pic"):
            if OP.exists(mfile := model_name + mtype):
                model_type, model_file = mtype, mfile
                break
    if model_type.lower() in (".dat", ".pic"):
        if not OP.exists(model_file):
            return crs
        with open(model_file, "r", encoding="cp1252") as fmod:
            for line in fmod:
                if m := re.search(r'SPATIAL-REF\s+"?(EPSG:\d+)', line, re.IGNORECASE):
                    print("CRS found for model file:", OP.basename(model_file))
                    return m[1].upper()
    return crs
