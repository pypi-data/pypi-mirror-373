# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.shopfloor_reception.tests.common import CommonCase


# pylint: disable=W8110
class TestSetPackDimension(CommonCase):
    @classmethod
    def setUpClassBaseData(cls):
        super().setUpClassBaseData()
        # Activate the option to use the module
        cls.menu.sudo().set_packaging_dimension = True
        cls.picking = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10), (cls.product_c, 10)]
        )
        cls.default_packaging_level = cls.env[
            "product.packaging"
        ].default_packaging_level_id()
        cls.default_packaging_level.sudo().write(
            {
                "shopfloor_collect_length": True,
                "shopfloor_collect_width": True,
                "shopfloor_collect_height": True,
                "shopfloor_collect_weight": True,
            }
        )
        # Picking has 3 products
        # Product A with one packaging
        # Product B with no packaging
        cls.product_b.packaging_ids = [(5, 0, 0)]
        # Product C with 2 packaging
        cls.product_c_packaging_2 = (
            cls.env["product.packaging"]
            .sudo()
            .create(
                {
                    "name": "Big Box",
                    "product_id": cls.product_c.id,
                    "barcode": "ProductCBigBox",
                    "qty": 6,
                }
            )
        )

        cls.line_with_packaging = cls.picking.move_line_ids[0]
        cls.line_without_packaging = cls.picking.move_line_ids[1]

    def _assert_response_set_dimension(
        self, response, picking, line, packaging, message=None
    ):
        data = {
            "picking": self.data.picking(picking),
            "selected_move_line": self.data.move_line(line),
            "packaging": self.data_detail.packaging_detail(packaging),
        }
        self.assert_response(
            response,
            next_state="set_packaging_dimension",
            data=data,
            message=message,
        )

    def test_scan_product_ask_for_dimension(self):
        self.product_a.tracking = "none"
        # self._add_package(self.picking)
        self.assertTrue(self.product_a.packaging_ids)
        response = self.service.dispatch(
            "scan_line",
            params={
                "picking_id": self.picking.id,
                "barcode": self.product_a.barcode,
            },
        )
        self.data.picking(self.picking)
        selected_move_line = self.picking.move_line_ids.filtered(
            lambda li: li.product_id == self.product_a
        )
        self._assert_response_set_dimension(
            response, self.picking, selected_move_line, self.product_a_packaging
        )

    def test_scan_product_dimension_already_defined(self):
        self.product_a.tracking = "none"
        self.product_a_packaging.write(
            {
                "packaging_length": 10.0,
                "width": 5.0,
                "height": 2.0,
                "weight": 1.5,
            }
        )
        response = self.service.dispatch(
            "scan_line",
            params={
                "picking_id": self.picking.id,
                "barcode": self.product_a.barcode,
            },
        )
        selected_move_line = self.picking.move_line_ids.filtered(
            lambda li: li.product_id == self.product_a
        )
        self.assert_response(
            response,
            next_state="set_quantity",
            data={
                "confirmation_required": None,
                "picking": self.data.picking(self.picking),
                "selected_move_line": [self.data.move_line(selected_move_line)],
            },
        )

    def test_scan_product_dimension_not_needed(self):
        self.product_a.tracking = "none"
        self.default_packaging_level.sudo().write(
            {
                "shopfloor_collect_length": False,
                "shopfloor_collect_width": False,
                "shopfloor_collect_height": False,
                "shopfloor_collect_weight": False,
            }
        )
        response = self.service.dispatch(
            "scan_line",
            params={
                "picking_id": self.picking.id,
                "barcode": self.product_a.barcode,
            },
        )
        selected_move_line = self.picking.move_line_ids.filtered(
            lambda li: li.product_id == self.product_a
        )
        self.assert_response(
            response,
            next_state="set_quantity",
            data={
                "confirmation_required": None,
                "picking": self.data.picking(self.picking),
                "selected_move_line": [self.data.move_line(selected_move_line)],
            },
        )

    def test_scan_lot_ask_for_dimension(self):
        self.product_a.tracking = "none"
        selected_move_line = self.picking.move_line_ids.filtered(
            lambda li: li.product_id == self.product_a
        )
        self.assertTrue(self.product_a.packaging_ids)
        response = self.service.dispatch(
            "set_lot_confirm_action",
            params={
                "picking_id": self.picking.id,
                "selected_line_id": selected_move_line.id,
            },
        )
        self.data.picking(self.picking)
        selected_move_line = self.picking.move_line_ids.filtered(
            lambda li: li.product_id == self.product_a
        )
        self._assert_response_set_dimension(
            response, self.picking, selected_move_line, self.product_a_packaging
        )

    def test_set_packaging_dimension(self):
        selected_move_line = self.picking.move_line_ids.filtered(
            lambda li: li.product_id == self.product_a
        )
        self.service.dispatch(
            "set_packaging_dimension",
            params={
                "picking_id": self.picking.id,
                "selected_line_id": selected_move_line.id,
                "packaging_id": self.product_a_packaging.id,
                "height": 55,
                "qty": 34,
                "barcode": "barcode",
            },
        )
        self.assertEqual(self.product_a_packaging.height, 55)
        self.assertEqual(self.product_a_packaging.barcode, "barcode")
        self.assertEqual(self.product_a_packaging.qty, 34)

    def test_set_multiple_packaging_dimension(self):
        line = self.picking.move_line_ids.filtered(
            lambda li: li.product_id == self.product_c
        )
        # Set the weight but other dimension are required
        self.product_c_packaging_2.weight = 200
        response = self.service.dispatch(
            "set_packaging_dimension",
            params={
                "picking_id": self.picking.id,
                "selected_line_id": line.id,
                "packaging_id": self.product_c_packaging.id,
                "height": 55,
                "length": 233,
            },
        )
        self.assertEqual(self.product_c_packaging.height, 55)
        self.assertEqual(self.product_c_packaging.packaging_length, 233)
        self._assert_response_set_dimension(
            response,
            self.picking,
            line,
            self.product_c_packaging_2,
            message=self.msg_store.packaging_dimension_updated(
                self.product_c_packaging
            ),
        )
        response = self.service.dispatch(
            "set_packaging_dimension",
            params={
                "picking_id": self.picking.id,
                "selected_line_id": line.id,
                "packaging_id": self.product_c_packaging_2.id,
                "height": 200,
                "weight": 1000,
            },
        )
        self.assertEqual(self.product_c_packaging_2.height, 200)
        self.assertEqual(self.product_c_packaging_2.weight, 1000)
        self.assert_response(
            response,
            next_state="set_quantity",
            data={
                "picking": self.data.picking(self.picking),
                "selected_move_line": self.data.move_lines(line),
                "confirmation_required": None,
            },
            message=self.msg_store.packaging_dimension_updated(
                self.product_c_packaging_2
            ),
        )
