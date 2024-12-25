import bpy
from bpy.types import Context, Object
from mathutils import Matrix, Vector, Euler


def get_parent_inverse_location(self):
    obj = bpy.context.object
    matrix: Matrix = obj.matrix_parent_inverse
    return matrix.to_translation()


def get_parent_inverse_rotation(self):
    obj = bpy.context.object
    matrix: Matrix = obj.matrix_parent_inverse
    return matrix.to_euler()


def get_parent_inverse_scale(self):
    obj = bpy.context.object
    matrix: Matrix = obj.matrix_parent_inverse
    return matrix.to_scale()


def set_parent_inverse_matrix(obj: Object, loc: Vector, rot: Euler, scale: Vector):
    obj.matrix_parent_inverse = (
        Matrix.Translation(loc)
        @ rot.to_matrix().to_4x4()
        @ Matrix.Diagonal(scale).to_4x4()
    )


def set_parent_inverse_location(self, value):
    obj = bpy.context.object
    matrix: Matrix = obj.matrix_parent_inverse
    set_parent_inverse_matrix(
        obj=obj, 
        loc=Vector(value), 
        rot=matrix.to_euler(), 
        scale=matrix.to_scale()
    )


def set_parent_inverse_rotation(self, value):
    obj = bpy.context.object
    matrix: Matrix = obj.matrix_parent_inverse
    set_parent_inverse_matrix(
        obj=obj,
        loc=matrix.to_translation(),
        rot=Euler(value),
        scale=matrix.to_scale(),
    )


def set_parent_inverse_scale(self, value):
    obj = bpy.context.object
    matrix: Matrix = obj.matrix_parent_inverse
    set_parent_inverse_matrix(
        obj=obj,
        loc=matrix.to_translation(),
        rot=matrix.to_euler(),
        scale=Vector(value),
    )


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


def register():
    bpy.utils.register_class(OBJECT_PT_MatrixParentInverse)
    bpy.types.Object.parent_inverse_location = bpy.props.FloatVectorProperty(
        name="Location",
        subtype="TRANSLATION",
        description="Location  from matrix_parent_inverse",
        get=get_parent_inverse_location,
        set=set_parent_inverse_location,
    )  # type: ignore
    bpy.types.Object.parent_inverse_rotation = bpy.props.FloatVectorProperty(
        name="Rotation",
        subtype="EULER",
        description="Rotation (Euler) from matrix_parent_inverse",
        get=get_parent_inverse_rotation,
        set=set_parent_inverse_rotation,
    )  # type: ignore
    bpy.types.Object.parent_inverse_scale = bpy.props.FloatVectorProperty(
        name="Scale",
        subtype="XYZ",
        description="Scale from matrix_parent_inverse",
        get=get_parent_inverse_scale,
        set=set_parent_inverse_scale,
        default=(1, 1, 1),
    )  # type: ignore


def unregister():
    bpy.utils.unregister_class(OBJECT_PT_MatrixParentInverse)
    del bpy.types.Object.parent_inverse_location
    del bpy.types.Object.parent_inverse_rotation
    del bpy.types.Object.parent_inverse_scale


if __name__ == "__main__":
    register()
