import bpy
from bpy.types import Context, Object
from mathutils import Matrix, Vector, Euler


class OBJECT_PT_MatrixParentInverse(bpy.types.Panel):
    """Panel to display matrix_parent_inverse as Location, Rotation, and Scale"""
    bl_label = "Matrix Parent Inverse"
    bl_idname = "OBJECT_PT_matrix_parent_inverse"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "OBJECT_PT_relations"
    bl_options = {"DEFAULT_CLOSED"}


    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        obj = context.object
        col.prop(obj, "parent_inverse_location")
        col.prop(obj, "parent_inverse_rotation")
        col.prop(obj, "parent_inverse_scale")


def update_matrix_parent_inverse_props(obj):
    matrix = obj.matrix_parent_inverse
    obj.parent_inverse_location = matrix.to_translation()
    obj.parent_inverse_rotation = matrix.to_euler()
    obj.parent_inverse_scale = matrix.to_scale()


def update_matrix_parent_inverse(self, context: Context):
    obj = context.object
    if not obj:
        return
    loc = Vector(obj.parent_inverse_location)
    rot = Euler(obj.parent_inverse_rotation)
    scale = Vector(obj.parent_inverse_scale)
    obj.matrix_parent_inverse = (
        Matrix.Translation(loc) @ rot.to_matrix().to_4x4() @ Matrix.Diagonal(scale).to_4x4()
    )

def register():
    bpy.utils.register_class(OBJECT_PT_MatrixParentInverse)
    bpy.types.Object.parent_inverse_location = bpy.props.FloatVectorProperty(
        name="Location",
        subtype='TRANSLATION',
        description="Location  from matrix_parent_inverse",
        update=update_matrix_parent_inverse,
    )
    bpy.types.Object.parent_inverse_rotation = bpy.props.FloatVectorProperty(
        name="Rotation",
        subtype='EULER',
        description="Rotation (Euler) from matrix_parent_inverse",
        update=update_matrix_parent_inverse,
    )
    bpy.types.Object.parent_inverse_scale = bpy.props.FloatVectorProperty(
        name="Scale",
        subtype='XYZ',
        description="Scale from matrix_parent_inverse",
        update=update_matrix_parent_inverse,
    )

    # # Initialize the properties for existing objects
    # for obj in bpy.data.objects:
    #     if hasattr(obj, "matrix_parent_inverse"):
    #         update_matrix_parent_inverse_props(obj)


def unregister():
    bpy.utils.unregister_class(OBJECT_PT_MatrixParentInverse)
    del bpy.types.Object.parent_inverse_location
    del bpy.types.Object.parent_inverse_rotation
    del bpy.types.Object.parent_inverse_scale


if __name__ == "__main__":
    register()
