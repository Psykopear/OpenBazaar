import unittest
import mock

from orders import Orders


class TestOrdersClass(unittest.TestCase):
    """
    Tests for orders.py
    """

    def setUp(self):
        self.mock_transport = mock.Mock()
        self.mock_transport.add_callbacks.return_value = "mock"
        self.mock_db = mock.Mock()
        self.orders = Orders(transport=self.mock_transport, market_id='', db_connection=self.mock_db, gpg='')

    def test_init(self):
        """
        Test that everything is initialized well
        """
        self.assertEqual(self.orders.market_id, '')
        self.assertEqual(self.orders.gpg, '')
        self.assertEqual(self.mock_transport.add_callbacks.call_count, 1)

    def test_state_class(self):
        """
        Test the State class' variables
        """
        self.assertEqual(self.orders.State.SENT, 'Sent')
        self.assertEqual(self.orders.State.ACCEPTED, 'Accepted')
        self.assertEqual(self.orders.State.BID, 'Bid')
        self.assertEqual(self.orders.State.BUYER_PAID, 'Buyer Paid')
        self.assertEqual(self.orders.State.NEED_TO_PAY, 'Need to Pay')
        self.assertEqual(self.orders.State.WAITING_FOR_MERCHANT, 'Order Pending')
        self.assertEqual(self.orders.State.NEW, 'New')
        self.assertEqual(self.orders.State.NOTARIZED, 'Notarized')
        self.assertEqual(self.orders.State.PAID, 'Paid')
        self.assertEqual(self.orders.State.RECEIVED, 'Received')
        self.assertEqual(self.orders.State.SHIPPED, 'Shipped')
        self.assertEqual(self.orders.State.WAITING_FOR_PAYMENT, 'Waiting for Payment')
        self.assertEqual(self.orders.State.COMPLETED, 'Completed')

    def test_validate_on_order(self):
        """
        Test Order.validate_on_order()
        """
        self.assertTrue(self.orders.validate_on_order())

    @mock.patch('orders.Orders.new_order')
    def test_on_order_with_new_order(self, mocked_function):
        """
        Test Order.on_order() with new_order
        """
        msg = {'state': self.orders.State.NEW}
        self.orders.on_order(msg)
        self.assertEqual(mocked_function.call_count, 1)

    @mock.patch('orders.Orders.handle_bid_order')
    def test_on_order_with_bid_order(self, mocked_function):
        """
        Test Order.on_order() with handle_bid_order
        """
        msg = {'state': self.orders.State.BID}
        self.orders.on_order(msg)
        self.assertEqual(mocked_function.call_count, 1)

    @mock.patch('orders.Orders.handle_notarized_order')
    def test_on_order_with_notarized_order(self, mocked_function):
        """
        Test Order.on_order() with handle_notarized_order
        """
        msg = {'state': self.orders.State.NOTARIZED}
        self.orders.on_order(msg)
        self.assertEqual(mocked_function.call_count, 1)

    @mock.patch('orders.Orders.handle_accepted_order')
    def test_on_order_with_accepted_order(self, mocked_function):
        """
        Test Order.on_order() with handle_accepted_order
        """
        msg = {'state': self.orders.State.WAITING_FOR_PAYMENT}
        self.orders.on_order(msg)
        self.assertEqual(mocked_function.call_count, 1)

    @mock.patch('orders.Orders.handle_paid_order')
    def test_on_order_with_paid_order(self, mocked_function):
        """
        Test Order.on_order() with handle_paid_order
        """
        msg = {'state': self.orders.State.PAID}
        self.orders.on_order(msg)
        self.assertEqual(mocked_function.call_count, 1)

    @mock.patch('orders.Orders.handle_shipped_order')
    def test_on_order_with_shipped_order(self, mocked_function):
        """
        Test Order.on_order() with handle_shipped_order
        """
        msg = {'state': self.orders.State.SHIPPED}
        self.orders.on_order(msg)
        self.assertEqual(mocked_function.call_count, 1)

    def test_get_offer_json_with_order_sent(self):
        """
        Test Orders.get_offer_json() with order sent
        """
        state = Orders.State.SENT
        raw_contract = 'First line \n' \
                       'Second line \n' \
                       'Third line \n' \
                       'Fourth line \n' \
                       'Fifth line \n' \
                       '{"test": "test"}\n' \
                       '- -----BEGIN PGP SIGNATURE-----' \
                       'signature'
        self.assertEqual(self.orders.get_offer_json(raw_contract, state), {'test': 'test'})

    def test_get_offer_json_with_pending_order(self):
        """
        Test Orders.get_offer_json() with pending order
        """
        state = Orders.State.WAITING_FOR_PAYMENT
        raw_contract = 'First line \n' \
                       'Second line \n' \
                       'Third line \n' \
                       'Fourth line \n' \
                       'Fifth line \n' \
                       'Sixth line \n' \
                       'Eighth line \n' \
                       'Nineth line \n' \
                       '{"test": "test"} \n' \
                       '---------BEGIN PGP SIGNATURE-----\n' \
                       'Eighth line \n' \
                       'Nineth line'
        self.assertEqual(self.orders.get_offer_json(raw_contract, state), {'test': 'test'})

    def test_get_offer_json_with_completed_order(self):
        """
        Test Orders.get_offer_json() with completed order
        """
        state = Orders.State.COMPLETED
        raw_contract = '1st line \n' \
                       '2nd line \n' \
                       '3th line \n' \
                       '4th line \n' \
                       '5th line \n' \
                       '6th line \n' \
                       '7th line \n' \
                       '8th line \n' \
                       '9th line \n' \
                       '10th line \n' \
                       '"test": "test"} \n' \
                       '- - -----BEGIN PGP SIGNATURE-----'
        self.assertEqual(self.orders.get_offer_json(raw_contract, state), {'test': 'test'})

    def test_get_offer_json_with_shipped_order(self):
        """
        Test Orders.get_offer_json() with shipped order
        """
        state = Orders.State.SHIPPED
        raw_contract = 'First line \n' \
                       'Second line \n' \
                       'Third line \n' \
                       'Fourth line \n' \
                       'Fifth line \n' \
                       'Sixth line \n' \
                       'Eighth line \n' \
                       'Nineth line \n' \
                       '{"test": "test"} \n' \
                       '--- -----BEGIN PGP SIGNATURE-----\n' \
                       'Eighth line \n' \
                       'Nineth line'
        self.assertEqual(self.orders.get_offer_json(raw_contract, state), {'test': 'test'})

    def test_get_offer_json_with_notarized_order(self):
        """
        Test Orders.get_offer_json() with notarized order
        """
        state = Orders.State.RECEIVED
        raw_contract = 'First line \n' \
                       'Second line \n' \
                       'Third line \n' \
                       'Fourth line \n' \
                       '"test": "test"}} \n' \
                       '- -----BEGIN PGP SIGNATURE-----\n' \
                       'Eighth line \n' \
                       'Nineth line'
        self.assertEqual(self.orders.get_offer_json(raw_contract, state), {'Seller': {'test': 'test'}})

    def test_get_offer_json_with_wrong_raw_contract(self):
        """
        Test Orders.get_offer_json() with notarized order
        """
        state = Orders.State.RECEIVED
        raw_contract = 'AHAHAHAHJOKE!'
        self.assertEqual(self.orders.get_offer_json(raw_contract, state), '')
