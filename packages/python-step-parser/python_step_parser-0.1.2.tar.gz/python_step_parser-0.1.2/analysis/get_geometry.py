from step_types.advanced_brep_shape_representation import AdvancedBrepShapeRepresentation
from step_types.manifold_solid_brep import ManifoldSolidBrep
from step_types.closed_shell import ClosedShell
from step_types.axis2_placement3d import Axis2Placement3d
from step_types.cartesian_point import CartesianPoint
from step_types.direction import Direction

import json

def get_component_geometry(shape: AdvancedBrepShapeRepresentation):
    print(f'Loading geometry for {shape.context.context_type} {shape.context.context_identifier}')

    part_geoms = []
    for part in shape.items:
        print(part.type_name)
        p: ManifoldSolidBrep = part
        s: ClosedShell = p.outer
        face_geometries = []
        for f in s.faces:
            face_geometries.append(f.get_geometry())
        part_geoms.append(face_geometries)

    print('Compiled geometries')

    with open(f'./out/{shape.type_name}_{shape.key}.json', 'w') as f:
        f.writelines(json.dumps({
            'name': shape.context.context_identifier,
            'type': shape.context.context_type,
            'parts': part_geoms
        }, indent=2))

    print('Rendered geometries')