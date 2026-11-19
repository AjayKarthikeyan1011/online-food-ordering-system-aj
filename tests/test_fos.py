"""Unit tests for validators, menu, customers, cart and orders."""
import unittest

from fos import cart as cart_module
from fos import customers, menu, orders, validators
from fos.database import connect
from fos.validators import ValidationError


class BaseCase(unittest.TestCase):
    def setUp(self):
        self.conn = connect(":memory:")
        self.burger = menu.add_item(self.conn, "Veg Burger", "Main Course", "120")
        self.coffee = menu.add_item(self.conn, "Cold Coffee", "Drinks", "80")
        self.biryani = menu.add_item(self.conn, "Veg Biryani", "Main Course", "220")
        self.customer = customers.register_customer(
            self.conn, "Meera Iyer", "meera@example.com", "9876543210")

    def tearDown(self):
        self.conn.close()

    def cart_with(self, *pairs):
        cart = cart_module.Cart()
        for item_id, qty in pairs:
            cart.add(self.conn, item_id, qty)
        return cart


class ValidatorTests(unittest.TestCase):
    def test_email_invalid(self):
        with self.assertRaises(ValidationError):
            validators.validate_email("bad-email")

    def test_email_valid_is_lowercased(self):
        self.assertEqual(validators.validate_email(" Asha@Example.COM "), "asha@example.com")

    def test_phone_must_be_10_digits(self):
        for bad in ("123", "98765abc10", "98765432101"):
            with self.assertRaises(ValidationError):
                validators.validate_phone(bad)

    def test_price_rejects_zero_negative_and_text(self):
        for bad in ("0", "-5", "abc", ""):
            with self.assertRaises(ValidationError):
                validators.validate_price(bad)

    def test_quantity_range(self):
        self.assertEqual(validators.validate_quantity("3"), 3)
        for bad in ("0", "11", "-1", "x"):
            with self.assertRaises(ValidationError):
                validators.validate_quantity(bad)

    def test_category_is_normalised(self):
        self.assertEqual(validators.validate_category("main course"), "Main Course")
        with self.assertRaises(ValidationError):
            validators.validate_category("Snacks")


class MenuTests(BaseCase):
    def test_add_and_list(self):
        self.assertEqual(len(menu.list_items(self.conn)), 3)

    def test_duplicate_name_rejected_case_insensitive(self):
        with self.assertRaises(ValidationError):
            menu.add_item(self.conn, "veg burger", "Main Course", "100")

    def test_search_is_case_insensitive(self):
        self.assertEqual([r["name"] for r in menu.search_items(self.conn, "BURGER")], ["Veg Burger"])

    def test_remove_unordered_item(self):
        menu.remove_item(self.conn, self.coffee)
        self.assertEqual(len(menu.list_items(self.conn)), 2)

    def test_cannot_remove_item_in_active_order(self):
        orders.place_order(self.conn, self.customer, self.cart_with((self.burger, 1)))
        with self.assertRaises(ValidationError):
            menu.remove_item(self.conn, self.burger)


class CustomerTests(BaseCase):
    def test_register_returns_id(self):
        self.assertEqual(self.customer, 1)

    def test_duplicate_email_rejected_case_insensitive(self):
        with self.assertRaises(ValidationError):
            customers.register_customer(self.conn, "Other", "MEERA@example.com", "9123456780")

    def test_unknown_customer(self):
        with self.assertRaises(ValidationError):
            customers.get_customer(self.conn, 99)


class CartTests(BaseCase):
    def test_totals_with_delivery_fee(self):
        t = self.cart_with((self.burger, 2), (self.coffee, 1)).totals(self.conn)
        self.assertEqual((t["subtotal"], t["tax"], t["delivery_fee"], t["total"]),
                         (320.0, 16.0, 40.0, 376.0))

    def test_free_delivery_at_500_or_more(self):
        t = self.cart_with((self.biryani, 3)).totals(self.conn)
        self.assertEqual((t["subtotal"], t["delivery_fee"], t["total"]), (660.0, 0.0, 693.0))

    def test_quantity_limit_per_item(self):
        cart = self.cart_with((self.burger, 8))
        with self.assertRaises(ValidationError):
            cart.add(self.conn, self.burger, 3)

    def test_unavailable_item_rejected(self):
        menu.set_availability(self.conn, self.coffee, False)
        with self.assertRaises(ValidationError):
            cart_module.Cart().add(self.conn, self.coffee, 1)

    def test_remove_from_cart(self):
        cart = self.cart_with((self.burger, 1))
        cart.remove(self.burger)
        self.assertTrue(cart.is_empty())
        with self.assertRaises(ValidationError):
            cart.remove(self.burger)


class OrderTests(BaseCase):
    def test_place_order_stores_totals_and_clears_cart(self):
        cart = self.cart_with((self.burger, 2), (self.coffee, 1))
        order_id = orders.place_order(self.conn, self.customer, cart)
        order = orders.get_order(self.conn, order_id)
        self.assertEqual((order["status"], order["total"]), ("Placed", 376.0))
        self.assertTrue(cart.is_empty())
        self.assertEqual(len(orders.order_lines(self.conn, order_id)), 2)

    def test_empty_cart_rejected(self):
        with self.assertRaises(ValidationError):
            orders.place_order(self.conn, self.customer, cart_module.Cart())

    def test_unknown_customer_rejected(self):
        with self.assertRaises(ValidationError):
            orders.place_order(self.conn, 99, self.cart_with((self.burger, 1)))

    def test_status_flow_to_delivered(self):
        order_id = orders.place_order(self.conn, self.customer, self.cart_with((self.burger, 1)))
        seen = [orders.update_status(self.conn, order_id)[1] for _ in range(3)]
        self.assertEqual(seen, ["Preparing", "Out for Delivery", "Delivered"])
        with self.assertRaises(ValidationError):
            orders.update_status(self.conn, order_id)

    def test_cancel_only_when_placed(self):
        first = orders.place_order(self.conn, self.customer, self.cart_with((self.burger, 1)))
        orders.cancel_order(self.conn, first)
        self.assertEqual(orders.get_order(self.conn, first)["status"], "Cancelled")
        second = orders.place_order(self.conn, self.customer, self.cart_with((self.coffee, 1)))
        orders.update_status(self.conn, second)
        with self.assertRaises(ValidationError):
            orders.cancel_order(self.conn, second)

    def test_cancelled_order_cannot_advance(self):
        order_id = orders.place_order(self.conn, self.customer, self.cart_with((self.burger, 1)))
        orders.cancel_order(self.conn, order_id)
        with self.assertRaises(ValidationError):
            orders.update_status(self.conn, order_id)

    def test_history_and_active_orders(self):
        a = orders.place_order(self.conn, self.customer, self.cart_with((self.burger, 1)))
        orders.place_order(self.conn, self.customer, self.cart_with((self.coffee, 1)))
        orders.cancel_order(self.conn, a)
        self.assertEqual(len(orders.order_history(self.conn, self.customer)), 2)
        self.assertEqual(len(orders.active_orders(self.conn)), 1)


if __name__ == "__main__":
    unittest.main()
