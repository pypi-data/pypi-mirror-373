from src.python_step_parser.step_types import *
import time

from typing import List, Tuple

from src.python_step_parser import step_types
from src.python_step_parser.step_types.transient import child_type_register as transient_register
from src.python_step_parser.step_types.shape_representation import child_type_register as shape_representation_register
from src.python_step_parser.step_types.solid_model import child_type_register as solid_model_regsiter
from src.python_step_parser.step_types.solid_model import child_type_register as solid_model_register

from src.python_step_parser import StepParser

import analysis

def get_components(parser) -> List[Tuple[RepresentationContext, int]]:
    geometric_contexts = []
    
    reps = parser.get_representation_contexts()
    for component_id in reps:
        val = step_types.RepresentationContext(parser, component_id)
        solids = []

        parents = parser.get_parents(val.key)
        for pid in parents:
            parent: step_types.ShapeRepresentation = shape_representation_register.try_parse(parser, pid)
            if parent is None:
                continue
            for rid in parent.items:
                solid = solid_model_regsiter.try_parse(parser, rid)
                if solid is not None:
                    # print(pid, parent.type_name, rid, step_types.helpers.get_entity_type(conn, rid))
                    solids.append(rid)

        if len(solids) > 0:
            geometric_contexts.append((
                val,
                solids[0]
            ))

    return geometric_contexts

if __name__ == '__main__':
    file_name = "GlassDoor_BanksideYards.step"
    parser = StepParser(file_name)
    parser.parse()

    print('loading cache')
    t = time.time()
    parser.load_cache()
    print(f'loaded cache in {round((time.time() - t) * 1000, 0)}')

    components = get_components(parser)
    print(components)

    # reps = parser.get_representation_contexts()
    # print(reps)

    # pre_t = time.time()

    # geometric_contexts = []
    
    # for component_id in reps:
    #     t = time.time()

    #     val = RepresentationContext(parser, component_id)
    #     solids = []

    #     parents = parser.get_parents(val.key)
    #     for pid in parents:
    #         parent: ShapeRepresentation = shape_representation_type_register.try_parse(parser, pid)
    #         if parent is None:
    #             continue
    #         for rid in parent.items:
    #             solid = solid_model_type_register.try_parse(parser, rid)
    #             if solid is not None:
    #                 # print(pid, parent.type_name, rid, step_types.helpers.get_entity_type(conn, rid))
    #                 solids.append(rid)

    #     if len(solids) > 0:
    #         geometric_contexts.append([
    #             val,
    #             solids
    #         ])
    #     # print(solids)
    #     # print(val)
    #     # print(f'resolved shape in {int(round((time.time() - t) * 1000, 0))}ms')

    # print('got', len(geometric_contexts), 'geometric contexts, out of', len(reps))
    # print(f'got all in {int(round((time.time() - pre_t) * 1000, 0))}ms')


"""
   196 ADVANCED_BREP_SHAPE_REPRESENTATION
 15557 ADVANCED_FACE
     1 APPLICATION_CONTEXT
     1 APPLICATION_PROTOCOL_DEFINITION
 28722 AXIS2_PLACEMENT_3D
  4671 B_SPLINE_CURVE_WITH_KNOTS
   660 B_SPLINE_SURFACE_WITH_KNOTS
125556 CARTESIAN_POINT
  9686 CIRCLE
   199 CLOSED_SHELL
    14 COLOUR_RGB
   132 CONICAL_SURFACE
   880 CONTEXT_DEPENDENT_SHAPE_REPRESENTATION
  7492 CYLINDRICAL_SURFACE
    13 DEGENERATE_TOROIDAL_SURFACE
 81981 DIRECTION
     2 DRAUGHTING_PRE_DEFINED_COLOUR
 43435 EDGE_CURVE
 18994 EDGE_LOOP
  3258 ELLIPSE
 19026 FACE_BOUND
   729 FILL_AREA_STYLE
   729 FILL_AREA_STYLE_COLOUR
   880 ITEM_DEFINED_TRANSFORMATION
 24537 LINE
   199 MANIFOLD_SOLID_BREP
     1 MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION
   880 NEXT_ASSEMBLY_USAGE_OCCURRENCE
 86870 ORIENTED_EDGE
  7214 PLANE
   729 PRESENTATION_STYLE_ASSIGNMENT
   233 PRODUCT
   233 PRODUCT_CATEGORY
   233 PRODUCT_CONTEXT
   233 PRODUCT_DEFINITION
   233 PRODUCT_DEFINITION_CONTEXT
   233 PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE
  1113 PRODUCT_DEFINITION_SHAPE
   233 PRODUCT_RELATED_PRODUCT_CATEGORY
   233 SHAPE_DEFINITION_REPRESENTATION
   233 SHAPE_REPRESENTATION
   196 SHAPE_REPRESENTATION_RELATIONSHIP
    26 SPHERICAL_SURFACE
   729 STYLED_ITEM
   729 SURFACE_SIDE_STYLE
   729 SURFACE_STYLE_FILL_AREA
     4 SURFACE_STYLE_RENDERING_WITH_PROPERTIES
     4 SURFACE_STYLE_TRANSPARENT
   729 SURFACE_STYLE_USAGE
    20 TOROIDAL_SURFACE
   233 UNCERTAINTY_MEASURE_WITH_UNIT
 24537 VECTOR
    32 VERTEX_LOOP
 29257 VERTEX_POINT
"""