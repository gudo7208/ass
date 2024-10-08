import json
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopoDS import topods
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAbs import (GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Sphere, GeomAbs_Cone, GeomAbs_Torus, GeomAbs_BezierSurface, GeomAbs_BSplineSurface, GeomAbs_SurfaceOfRevolution, GeomAbs_SurfaceOfExtrusion, GeomAbs_OffsetSurface, GeomAbs_OtherSurface)
from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop

def read_step_file(filename):
    """Read and parse STEP file, return shape object."""
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(filename)
    if status != 1:
        raise ValueError("Unable to read STEP file.")
    step_reader.TransferRoots()
    return step_reader.OneShape()

def get_surface_type_code(surf_type):
    surface_types = {
        GeomAbs_Plane: "PLN", GeomAbs_Cylinder: "CYL", GeomAbs_Sphere: "SPH",
        GeomAbs_Cone: "CON", GeomAbs_Torus: "TOR", GeomAbs_BezierSurface: "BEZ",
        GeomAbs_BSplineSurface: "BSP", GeomAbs_SurfaceOfRevolution: "REV",
        GeomAbs_SurfaceOfExtrusion: "EXT", GeomAbs_OffsetSurface: "OFS",
        GeomAbs_OtherSurface: "OTH"
    }
    return surface_types.get(surf_type, "UNK")

def extract_features(shape):
    """Extract high-level features from the shape."""
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    features = []
    index = 1
    
    while explorer.More():
        face = topods.Face(explorer.Current())
        explorer.Next()
        
        surface = BRepAdaptor_Surface(face)
        surf_type = surface.GetType()
        
        props = GProp_GProps()
        brepgprop.SurfaceProperties(face, props)
        center = props.CentreOfMass()
        area = props.Mass()
        
        feature = {
            "id": index,
            "st": get_surface_type_code(surf_type),
            "a": round(area, 3),
            "com": [round(center.X(), 3), round(center.Y(), 3), round(center.Z(), 3)]
        }
        
        if surf_type == GeomAbs_Cylinder:
            cylinder = surface.Cylinder()
            feature["r"] = round(cylinder.Radius(), 3)
            axis = cylinder.Axis()
            feature["ad"] = [round(axis.Direction().X(), 3), round(axis.Direction().Y(), 3), round(axis.Direction().Z(), 3)]
        elif surf_type == GeomAbs_Sphere:
            feature["r"] = round(surface.Sphere().Radius(), 3)
        elif surf_type == GeomAbs_Cone:
            cone = surface.Cone()
            feature["r"] = round(cone.RefRadius(), 3)
            feature["sa"] = round(cone.SemiAngle(), 3)
        
        features.append(feature)
        index += 1
    return features

def build_json(part_id="P001", part_name="SamplePart", material="Steel", features=[]):
    """Organize extracted features into JSON structure."""
    json_data = {
        "metadata": {
            "format_description": """Format Description:
Top-level fields:
- "id": Part ID.
- "name": Part name.
- "mat": Material.
- "fts": List of features.

Feature fields:
- "id": Feature ID, integer.
- "st": Surface type, using abbreviated codes:
  - "PLN": Plane
  - "CYL": Cylinder
  - "SPH": Sphere
  - "CON": Cone
  - "TOR": Torus
  - "BEZ": Bezier Surface
  - "BSP": BSpline Surface
  - "REV": Surface of Revolution
  - "EXT": Surface of Extrusion
  - "OFS": Offset Surface
  - "OTH": Other Surface
- "a": Area.
- "com": Center of mass coordinates, [x, y, z].

Additional fields for specific types:
- "r": Radius (applicable to cylinder, sphere, cone, etc.).
- "ad": Axis direction, [x, y, z] (applicable to cylinder).
- "sa": Semi-angle, in radians (applicable to cone)."""
        },
        "id": part_id,
        "name": part_name,
        "mat": material,
        "fts": features
    }
    return json_data

def main():
    step_filename = "/data6/guanyandong/0abfd208a8ede2492e36683498e8574c.STEP"
    shape = read_step_file(step_filename)
    features = extract_features(shape)
    json_output = build_json(part_id="P001", part_name="SamplePart", material="Steel", features=features)
    output_filename = "/data6/guanyandong/bearing_part_features_pythonOCC_en.json"
    with open(output_filename, "w", encoding="utf-8") as json_file:
        json.dump(json_output, json_file, ensure_ascii=False, indent=2, separators=(',', ':'))
    print(f"Feature extraction complete. JSON saved as '{output_filename}'.")

if __name__ == "__main__":
    main()
