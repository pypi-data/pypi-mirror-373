'''
Created on 22 aug 2018

@author: Jarrige_Pi

 18.08.22 (0.9.0) - creation - based on shapefile
 18.11.07 (0.9.1) - added target and shapeType Write keyword
                    added close Write method (shapefile 2.0)
 29.04.21 (0.9.2) - remove +init= in pyproj inits; use pyproj.Tranformer; swap wgs coords
 25.03.25 (1.0.0) - remove python 2 residues; uses proj.FrenchProjMapping; fix Reader
'''

import os.path as OP
import json
from numbers import Number

from ganessa.util import ws
from ganessa.proj import FrenchProjMapping

__version__ = "1.0.0"

POINT = 1
POLYLINE = 3
POLYGON = 5

def swapper(fun):
    '''returns a function that swaps return values'''
    def swapped_res(x, y):
        xr, yr = fun(x, y)
        return yr, xr
    return swapped_res

class Writer:
    '''Class wrapper for write functions to geojson'''
    def __init__(self, target=None, shapeType=POLYLINE):
        self.gtype = shapeType
        self.nfields = []
        self.sfields = []
        self.gobjects = []
        self.records = []
        self.proj = 'wgs84'
        self.target = target

    def point(self, x, y):
        self.gobjects.append((POINT, (x, y)))

    def line(self, parts=None, shapeType=POLYLINE):
        self.gobjects.append((shapeType, [] if parts is None else parts))

    def poly(self, parts=None, shapeType=POLYGON):
        self.gobjects.append((shapeType, [] if parts is None else parts))

#   def field(self, name, fieldType="C", size="50", decimal=0)
    def field(self, name, fieldType="N", size="50", decimal=0):
        self.nfields.append(name)
        self.sfields.append(size if fieldType.upper() == "C" else 0)

    def record(self, *args):
        self.records.append(args)

    def projection(self, proj):
        self.proj = proj

    def save(self, target=None):
        fname = self.target if target is None else target
        fname = OP.splitext(fname)[0]
        if self.proj == 'wgs84':
            convert = lambda x, y: (x, y)
        else:
            import pyproj
            wgs84 = pyproj.Proj(ws("EPSG:4326"))      # doit etre explicitement definie
            dicproj = FrenchProjMapping().mapping

            try:
                prj = dicproj[self.proj]
            except KeyError:
                prj = self.proj
                # if prj.upper().startswith('EPSG:'):
                #     prj = '+init=' + prj.upper()
            fmprj = pyproj.Proj(ws(prj))
            try:
                convert = pyproj.Transformer.from_proj(fmprj, wgs84).transform
            except AttributeError:
                class myTransformer:
                    '''Transformer emulator for older pyproj'''
                    @staticmethod
                    def transform(x, y):
                        return pyproj.transform(prj, wgs84, x, y)
                convert = myTransformer().transform
            convert = swapper(convert)

        items = []
        for (gtype, gdata), data in zip(self.gobjects, self.records):
            if gtype == POINT:
                stype = 'Point'
                wdata = convert(*gdata)
            else:
                if len(gdata) == 1:
                    stype = 'LineString'
                    wdata = [convert(*x) for x in gdata[0]]
                else:
                    stype = 'MultiLineString'
                    wdata = [[convert(*x) for x in part] for part in gdata]
            geom = dict(type=stype,
                        coordinates=wdata)
            pdata = [round(float(x), 4 if abs(x) > 1 else 6)
                     if isinstance(x, Number) else x for x in data]
            props = dict(zip(self.nfields, pdata))
            items.append(dict(type='Feature',
                              geometry=geom,
                              properties=props))
        with open(fname + '.geojson', 'w', encoding='utf-8') as f:
            item_to_dump = dict(type='FeatureCollection', features=items)
            json.dump(item_to_dump, f, indent=2)

    close = save

class _Shape:
    def __init__(self, typ, points=None):
        self.shapeType = typ
        self.points = points or []

class _ShapeRecord:
    """A shape object of any type."""
    def __init__(self, shape=None, record=None):
        self.shape = shape
        self.record = record

class Reader:
    """Class wrapper for read functions from geojson"""
    def __init__(self, fname, encoding=None):
        # fields to keep order, set for efficiency
        self.fields = []
        self.fieldset = set()
        self.data = []
        self.name = OP.splitext(fname)[0]
        self.count = 0
        for ext in ('.json', '.geojson'):
            if  OP.exists(self.name  + ext):
                self.name += ext
                break
        else:
            return
        # Lecture du fichier
        with open(self.name, 'r', encoding='utf-8') as f:
            item_to_filter = json.load(f)
        if item_to_filter['type'] != 'FeatureCollection':
            return
        for item in item_to_filter['features']:
            if item['type'] != 'Feature':
                continue
            geom = item['geometry']
            props = item.get('properties', {})
            gtype = geom['type']
            gdata = geom['coordinates']
            if gtype == 'Point':
                self.data.append((POINT, [tuple(gdata)], props))
            elif gtype == 'LineString':
                self.data.append((POLYLINE,
                                  [tuple(pt) for pt in gdata], props))
            else:
                continue
            # update fields list
            for p in props.keys():
                if p not in self.fieldset:
                    self.fields.append(p)
                    self.fieldset.add(p)
        return

    def shape(self, pos=0):
        """Returns the object at pos as a shape"""
        # return self.data[pos][0:2]
        typ, geom, *_ = self.data[pos]
        return _Shape(typ, geom)

    def iterShapes(self):
        """Iterator over objects, return shape"""
        for typ, geom, _ in self.data:
            # yield obj[0:2]
            yield _Shape(typ, geom)

    def _allfields(self, rec):
        '''Explode object props according to the field order'''
        return [rec.get(field, "") for field in self.fields]

    def record(self, pos=0):
        """Returns attributes"""
        return self._allfields(self.data[pos][2])

    def iterRecords(self):
        """Iterator over records"""
        for obj in self.data:
            yield self._allfields(obj[2])

    def shapeRecord(self, pos=0):
        """Returns """
        typ, geom, rec = self.data[pos]
        return _ShapeRecord(_Shape(typ, geom), rec)

    def iterShapeRecords(self):
        """Iterator over shape + record at once"""
        for typ, geom, rec in self.data:
            yield _ShapeRecord(_Shape(typ, geom), rec)

    def __len__(self):
        return len(self.data)

# for symmetry with shapefile
class ShapefileException(Exception):
    pass

if __name__ == "__main__":
    sig = Reader('D:/Temp/tmp-N.geojson')
    print('Read count:', len(sig))
    print('Fields:', sig.fields)
    for item in sig.iterShapes():
        pass
    for item in sig.iterRecords():
        pass
    print('Termine')
