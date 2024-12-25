import bpy
from bpy.types import Object, Panel, Operator
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


class OBJECT_PT_MatrixParentInverse(Panel):
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


class OBJECT_OT_make_links_parent(Operator):
    """Replace assigned parent"""
    bl_idname = "object.make_links_parent"
    bl_label = "Link Parents"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        obj_src = context.active_object
        if not obj_src:
            self.report({"ERROR"}, "No active object")
            return {"CANCELLED"}
        for obj in context.selected_objects:
            if obj == obj_src:
                continue
            if obj == obj_src.parent:
                continue
            obj.parent = obj_src.parent
            obj.parent_type = obj_src.parent_type
            if obj_src.parent_type == "BONE":
                obj.parent_bone = obj_src.parent_bone
            elif obj_src.parent_type in ["VERTEX", "VERTEX_3"]:
                obj.parent_vertices = obj_src.parent_vertices
            obj.matrix_parent_inverse = obj_src.matrix_parent_inverse
        return {"FINISHED"}


def add_to_transfer_menu(self: Operator, context):
    layout = self.layout
    layout.separator()
    layout.operator(OBJECT_OT_make_links_parent.bl_idname)


def register():
    bpy.types.Object.parent_inverse_location = bpy.props.FloatVectorProperty(
        name="Location",
        subtype="TRANSLATION",
        description="Parent inverse location",
        get=get_parent_inverse_location,
        set=set_parent_inverse_location,
    )
    bpy.types.Object.parent_inverse_rotation = bpy.props.FloatVectorProperty(
        name="Rotation",
        subtype="EULER",
        description="Parent inverse rotation (Euler, XYZ)",
        get=get_parent_inverse_rotation,
        set=set_parent_inverse_rotation,
    )
    bpy.types.Object.parent_inverse_scale = bpy.props.FloatVectorProperty(
        name="Scale",
        subtype="XYZ",
        description="Parent inverse scale",
        get=get_parent_inverse_scale,
        set=set_parent_inverse_scale,
        default=(1, 1, 1),
    )
    bpy.utils.register_class(OBJECT_PT_MatrixParentInverse)
    bpy.utils.register_class(OBJECT_OT_make_links_parent)
    bpy.types.VIEW3D_MT_make_links.append(add_to_transfer_menu)


def unregister():
    bpy.types.VIEW3D_MT_make_links.remove(add_to_transfer_menu)
    bpy.utils.unregister_class(OBJECT_OT_make_links_parent)
    bpy.utils.unregister_class(OBJECT_PT_MatrixParentInverse)
    del bpy.types.Object.parent_inverse_location
    del bpy.types.Object.parent_inverse_rotation
    del bpy.types.Object.parent_inverse_scale


if __name__ == "__main__":
    register()
