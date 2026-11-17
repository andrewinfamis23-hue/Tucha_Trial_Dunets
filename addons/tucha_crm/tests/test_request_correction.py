from datetime import datetime
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestRequestCorrection(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = new_test_user(
            cls.env, login="test_correction_manager",
            groups="tucha_crm.group_tucha_manager",
        )
        cls.candidate = new_test_user(
            cls.env, login="test_correction_candidate",
            groups="tucha_crm.group_tucha_candidate",
        )
        cls.customer = cls.env["res.partner"].create({"name": "Correction test"})

    def setUp(self):
        super().setUp()
        self.request = self.env["tucha.request"].create({
            "name": "TEST-CORRECTION",
            "customer_id": self.customer.id,
            "planned_from": "2026-01-01 10:00:00",
            "planned_to": "2026-01-01 11:00:00",
        }).with_user(self.manager)

    def test_full_cycle_reopens_with_fresh_date(self):
        old = datetime(2026, 1, 1, 10)
        fresh = datetime(2026, 1, 2, 10)
        with patch("odoo.fields.Datetime.now", return_value=old):
            self.request.action_request_correction()
            self.request.action_receive_correction()
            self.request.action_verify_correction()
        self.assertEqual(self.request.correction_state, "verified")
        self.assertEqual(self.request.correction_received_at, old)
        self.assertEqual(self.request.correction_verified_at, old)
        with patch("odoo.fields.Datetime.now", return_value=fresh):
            self.request.action_reopen_correction()
        self.assertEqual(self.request.correction_state, "requested")
        self.assertEqual(self.request.correction_requested_at, fresh)
        self.assertFalse(self.request.correction_received_at)
        self.assertFalse(self.request.correction_verified_at)

    def test_candidate_cannot_reopen(self):
        self.request.action_request_correction()
        self.request.action_receive_correction()
        with self.assertRaisesRegex(UserError, "только менеджер"):
            self.request.with_user(self.candidate).action_reopen_correction()
        self.assertEqual(self.request.correction_state, "received")
        self.assertTrue(self.request.correction_received_at)

    def test_manager_cannot_reopen_requested(self):
        self.request.action_request_correction()
        with self.assertRaisesRegex(UserError, "не находится на проверке"):
            self.request.action_reopen_correction()
        self.assertEqual(self.request.correction_state, "requested")

    def test_manager_can_reopen_received(self):
        self.request.action_request_correction()
        self.request.action_receive_correction()
        self.request.action_reopen_correction()
        self.assertEqual(self.request.correction_state, "requested")
        self.assertFalse(self.request.correction_received_at)
        self.assertFalse(self.request.correction_verified_at)
