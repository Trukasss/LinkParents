bl_info = {
    "name": "Link Parents",
    "description": "Link objects parents & edit Parent Inverse Matrix in UI",
    "author": "Lukas Sabaliauskas <lukas_sabaliauskas@hotmail.com>",
    "version": (1, 2, 0),
    "blender": (4, 0, 0),
    "location": "Object Properties > Relations > Matrix Parent Inverse",
    "warning": "",
    "doc_url": "https://extensions.blender.org/add-ons/link-parents/",
    "tracker_url": "https://github.com/Trukasss/LinkParents",
    "category": "3D View",
}

import bpy
import json

from bpy.types import Object, Panel, Operator, PropertyGroup
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

class TransformParentInverse(PropertyGroup):
    location: bpy.props.FloatVectorProperty(
        name="Location",
        subtype="TRANSLATION",
        description="Parent inverse location",
        get=get_parent_inverse_location,
        set=set_parent_inverse_location,
    ) # type: ignore
    rotation: bpy.props.FloatVectorProperty(
        name="Rotation",
        subtype="EULER",
        description="Parent inverse rotation (Euler, XYZ)",
        get=get_parent_inverse_rotation,
        set=set_parent_inverse_rotation,
    ) # type: ignore
    scale: bpy.props.FloatVectorProperty(
        name="Scale",
        subtype="XYZ",
        description="Parent inverse scale",
        get=get_parent_inverse_scale,
        set=set_parent_inverse_scale,
        default=(1, 1, 1),
    ) # type: ignore


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

    def draw_header_preset(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator('object.copy_matrix_parent_inverse', text="", icon="COPYDOWN")
        row.operator('object.paste_matrix_parent_inverse', text="", icon="PASTEDOWN")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        obj = context.object
        col.prop(obj.transform_parent_inverse, "location")
        col.prop(obj.transform_parent_inverse, "rotation")
        col.prop(obj.transform_parent_inverse, "scale")


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


class OBJECT_OT_copy_matrix_parent_inverse(Operator):
    """Copy matrix parent inverse from active object to clipboard"""
    bl_idname = "object.copy_matrix_parent_inverse"
    bl_label = "Copy Matrix Parent Inverse"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        matrix_list = [v[:] for v in context.active_object.matrix_parent_inverse]
        matrix_clip = json.dumps(matrix_list)
        bpy.context.window_manager.clipboard = matrix_clip
        self.report({"INFO"}, "Matrix Parent Inverse copied to clipboard")
        return {"FINISHED"}

class OBJECT_OT_paste_matrix_parent_inverse(Operator):
    """Paste matrix parent inverse to active object from clipboard"""
    bl_idname = "object.paste_matrix_parent_inverse"
    bl_label = "Paste Matrix Parent Inverse"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        try:
            matrix_clip = json.loads(bpy.context.window_manager.clipboard)
            context.object.matrix_parent_inverse = Matrix(matrix_clip)
        except Exception as e:
            self.report({"ERROR"}, f"Invalid clipboard:\n{e}")
            return {"CANCELLED"}

        self.report({"INFO"}, "Matrix Parent Inverse pasted")
        return {"FINISHED"}


## --- Constraints inverse matrix copy/paste

class BONE_OT_copy_constraint_inverse_matrix(Operator):
    """Copy active constraint matrix inverse from active bone to clipboard"""
    bl_idname = "bone.copy_constraint_inverse_matrix"
    bl_label = "Copy Bone Constraint matrix inverse"
    bl_options = {"REGISTER", "INTERNAL"}

    constraint_index : bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_pose_bone

    def execute(self, context):
        target_constraint = None
        for i, constraint in enumerate(context.active_pose_bone.constraints):
            if i == self.constraint_index:
                target_constraint = constraint
                break
        if target_constraint is None:
            self.report({"ERROR"}, "No constraint found")
            return {"CANCELLED"}

        matrix_list = [v[:] for v in target_constraint.inverse_matrix]
        matrix_clip = json.dumps(matrix_list)
        bpy.context.window_manager.clipboard = matrix_clip
        self.report({"INFO"}, "Constraint matrix inverse copied to clipboard")
        return {"FINISHED"}

class BONE_OT_paste_constraint_inverse_matrix(Operator):
    """Paste active constraint matrix inverse to active bone from clipboard"""
    bl_idname = "bone.paste_constraint_inverse_matrix"
    bl_label = "Paste Bone Constraint matrix inverse"
    bl_options = {"REGISTER", "INTERNAL"}

    constraint_index : bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_pose_bone

    def execute(self, context):
        target_constraint = None
        for i, constraint in enumerate(context.active_pose_bone.constraints):
            if i == self.constraint_index:
                target_constraint = constraint
                break
        if target_constraint is None:
            self.report({"ERROR"}, "No constraint found")
            return {"CANCELLED"}

        try:
            matrix_clip = json.loads(bpy.context.window_manager.clipboard)
            target_constraint.inverse_matrix = Matrix(matrix_clip)
        except Exception as e:
            self.report({"ERROR"}, f"Invalid clipboard:\n{e}")
            return {"CANCELLED"}

        self.report({"INFO"}, "Constraint matrix inverse pasted")
        return {"FINISHED"}

class BONE_PT_ConstraintMatrixParentInverse(Panel):
    """Panel to copy/paste constraint's matrix_parent_inverse"""

    bl_label = "Child Of Matrix Parent Inverse"
    bl_idname = "OBJECT_PT_constraint_inverse_matrix"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "bone_constraint"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.active_pose_bone and any(constraint.type == 'CHILD_OF'
                        for constraint in context.active_pose_bone.constraints
        )

    def draw(self, context):
        if not context.active_pose_bone:
            return
        pose_bone = context.active_pose_bone
        layout = self.layout
        layout.use_property_split = True

        for i, constraint in enumerate(pose_bone.constraints):
            if constraint.type != 'CHILD_OF':
                continue
            row = layout.row()
            row.label(text=f"{constraint.name}", icon="CONSTRAINT")
            subrow = row.row(align=True)
            subrow.operator('bone.copy_constraint_inverse_matrix', text="", icon="COPYDOWN").constraint_index = i
            subrow.operator('bone.paste_constraint_inverse_matrix', text="", icon="PASTEDOWN").constraint_index = i


def add_to_transfer_menu(self: Operator, context):
    layout = self.layout
    layout.separator()
    layout.operator(OBJECT_OT_make_links_parent.bl_idname, icon="ORIENTATION_PARENT")


def register():
    bpy.utils.register_class(TransformParentInverse)
    bpy.types.Object.transform_parent_inverse = bpy.props.PointerProperty(type=TransformParentInverse)
    bpy.utils.register_class(OBJECT_OT_make_links_parent)
    bpy.utils.register_class(OBJECT_OT_copy_matrix_parent_inverse)
    bpy.utils.register_class(OBJECT_OT_paste_matrix_parent_inverse)
    bpy.utils.register_class(BONE_OT_copy_constraint_inverse_matrix)
    bpy.utils.register_class(BONE_OT_paste_constraint_inverse_matrix)
    bpy.utils.register_class(OBJECT_PT_MatrixParentInverse)
    bpy.utils.register_class(BONE_PT_ConstraintMatrixParentInverse)
    bpy.types.VIEW3D_MT_make_links.append(add_to_transfer_menu)


def unregister():
    bpy.types.VIEW3D_MT_make_links.remove(add_to_transfer_menu)
    bpy.utils.unregister_class(BONE_PT_ConstraintMatrixParentInverse)
    bpy.utils.unregister_class(OBJECT_PT_MatrixParentInverse)
    bpy.utils.unregister_class(OBJECT_OT_paste_matrix_parent_inverse)
    bpy.utils.unregister_class(OBJECT_OT_copy_matrix_parent_inverse)
    bpy.utils.unregister_class(BONE_OT_paste_constraint_inverse_matrix)
    bpy.utils.unregister_class(BONE_OT_copy_constraint_inverse_matrix)
    bpy.utils.unregister_class(OBJECT_OT_make_links_parent)
    del bpy.types.Object.transform_parent_inverse
    bpy.utils.unregister_class(TransformParentInverse)


if __name__ == "__main__":
    register()
