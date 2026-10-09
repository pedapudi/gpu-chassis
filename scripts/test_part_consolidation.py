"""Regression checks for rotation-only manufacturing part equivalence."""
import unittest

import cadquery as cq

from consolidate_part_steps import ROTATIONS, difference, equivalent, normalize, rigid_transform


class PartEquivalenceTests(unittest.TestCase):
    def setUp(self):
        # Unequal legs and an offset hole distinguish handed formed parts.
        base=cq.Solid.makeBox(12,50,1.5).fuse(cq.Solid.makeBox(1.5,50,38))
        self.part=base.cut(cq.Solid.makeCylinder(2,4,cq.Vector(-1,20,9),cq.Vector(1,0,0)))

    def test_translation_reconstructs_installed_position(self):
        original=self.part.translate((426.5,123.2,171.5))
        local,placement=normalize(original,ROTATIONS[0])
        self.assertLess(difference(original,rigid_transform(local,placement)),1e-6)

    def test_opposite_orientation_can_share_a_file(self):
        reference,_=normalize(self.part,ROTATIONS[0])
        rotated=self.part.rotate((0,0,0),(0,0,1),180).translate((440,150,240))
        self.assertTrue(any(equivalent(reference,normalize(rotated,r)[0]) for r in ROTATIONS))

    def test_handed_parts_remain_distinct(self):
        reference,_=normalize(self.part,ROTATIONS[0])
        mirrored=self.part.mirror('YZ')
        self.assertFalse(any(equivalent(reference,normalize(mirrored,r)[0]) for r in ROTATIONS))

    def test_equal_volume_does_not_establish_equal_geometry(self):
        a=cq.Solid.makeBox(20,30,2).cut(cq.Solid.makeCylinder(2,3,cq.Vector(5,7,0)))
        b=cq.Solid.makeBox(20,30,2).cut(cq.Solid.makeCylinder(2,3,cq.Vector(6,7,0)))
        self.assertAlmostEqual(a.Volume(),b.Volume())
        self.assertFalse(equivalent(a,b))

    def test_tessellation_does_not_change_geometry_comparison(self):
        a=cq.Solid.makeBox(20,30,2).cut(cq.Solid.makeCylinder(2,3,cq.Vector(5,7,0)))
        b=a.copy()
        a.tessellate(.05,.1)
        self.assertTrue(equivalent(a,b))


if __name__=='__main__':
    unittest.main()
