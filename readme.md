# This tiny Blender addon helps with parenting objects and bones.

### 1. LINK PARENT
You can now __Link Parents__ in the "_Link/Transfer Data_" menu (Ctrl+L or Viewport > Object > Link/Transfer Data). It allow you to copy the active object's parent and it's transformation matrix. It supports object, bone and vertex parenting.

![Link Parents Operator](/presentation/Link_parents_operator.png)

### 2. SHOW PARENT
This addon also finally exposes the obscure __Matrix Parent Inverse__ under the Object's "_Relations_" property panel. This property is now editable through comprehensive transformation properties. Thanks to [Pullusb](https://github.com/Pullusb), you can now also copy/paste the matrix between objects. This also works between objects in different blend files.

![Matrix Parent Inverse Panel](/presentation/Matrix_parent_inverse_panel.png)

### 3. BONE CONSTRAINT
Finally, it allows you to copy-paste "Child of" bone constraint's inverse matrix from one bone to another. Thanks to [Pullusb](https://github.com/Pullusb).

![Matrix Parent Inverse Constraint](/presentation/Matrix_parent_inverse_constraint.png)


You can report any bug or file a feature request here: https://github.com/Trukasss/LinkParents/issues

Happy Blending!
