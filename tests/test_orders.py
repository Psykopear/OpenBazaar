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

    def test_get_buyer_json_with_need_to_pay_order(self):
        """
        Test Orders.get_buyer_json() with need to pay order
        """
        state = Orders.State.NEED_TO_PAY
        raw_contract = '1st line \n' \
                       '2nd line \n' \
                       '3th line \n' \
                       '4th line \n' \
                       '5th line \n' \
                       '6th line \n' \
                       '7th line \n' \
                       '8th line \n' \
                       '-----BEGIN PGP SIGNATURE-----\n' \
                       '"Buyer": "a very honest buyer"} \n' \
                       '- -----BEGIN PGP SIGNATURE'
        self.assertEqual(self.orders.get_buyer_json(raw_contract, state), {'Buyer': 'a very honest buyer'})

    def test_get_buyer_json_with_sent_order(self):
        """
        Test Orders.get_buyer_json() with sent order
        """
        state = Orders.State.SENT
        raw_contract = '1st line \n' \
                       '2nd line \n' \
                       '3th line \n' \
                       '4th line \n' \
                       '5th line \n' \
                       '6th line \n' \
                       '7th line \n' \
                       '-----BEGIN PGP SIGNATURE-----\n' \
                       '"Buyer": "a very honest buyer"}\n' \
                       '-----BEGIN PGP SIGNATURE'
        self.assertEqual(self.orders.get_buyer_json(raw_contract, state), {'Buyer': 'a very honest buyer'})

    def test_get_notary_json_with_notarized_order(self):
        """
        Test Orders.get_notary_json() with notarized order
        """
        state = Orders.State.NOTARIZED
        raw_contract = '1st line \n' \
                       '2nd line \n' \
                       '3th line \n' \
                       '4th line \n' \
                       '5th line \n' \
                       '6th line \n' \
                       '7th line \n' \
                       '8th line \n' \
                       '-----BEGIN PGP SIGNATURE-----\n' \
                       '"Buyer": "a very honest buyer"} \n' \
                       '- -----BEGIN PGP SIGNATURE\n' \
                       '"Notary": "notaaaary"}\n' \
                       '-----BEGIN PGP SIGNATURE'
        self.assertEqual(self.orders.get_notary_json(raw_contract, state), {'Notary': 'notaaaary'})

    def test_get_notary_json_with_sent_order(self):
        """
        Test Orders.get_notary_json() with sent order
        """
        state = Orders.State.SENT
        raw_contract = '1st line \n' \
                       '2nd line \n' \
                       '3th line \n' \
                       '4th line \n' \
                       '5th line \n' \
                       '6th line \n' \
                       '-----BEGIN PGP SIGNATURE-----\n' \
                       '"Buyer": "a very honest buyer"} \n' \
                       '- -----BEGIN PGP SIGNATURE\n' \
                       '"Notary": "notaaaary"}\n' \
                       '-----BEGIN PGP SIGNATURE'
        self.assertEqual(self.orders.get_notary_json(raw_contract, state), {'Notary': 'notaaaary'})

    def test_get_qr_code(self):
        """
        Test Orders.get_qr_code()
        """
        item_title = ''
        address = ''
        total = ''
        self.assertEqual(self.orders.get_qr_code(item_title, address, total),
                         'iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2ykAAACkUlEQVR4nO2bTYrjMBBGX40NvZQh\n'
                         'B8hR5Js1c6S+gXSUPsCAtAzI1Cwkx06gu6fpxGND1SJY1lt8UJRVP4oo37H461s4GG+88cYbb7zx\n'
                         'H/HSrIcofV0SpQfyvDduqMf4B/NeVVUTyAioagFcQUY6VVXVW/7Zeox/MJ+vEeouAvlF5TWBBqAG\n'
                         '9rZ6jH8Wn3tkZBL9PbRw/r96jP8J39+tFaZe4wD4d9lej/HP4Z2qBqBlVXQqo2unbjuON9Vj/GP4\n'
                         'Fr+xhmqH+HQq4tMJyKcCTDdRvDf9xn9u1b/rJqW7CPFcULiI3u7tT7/xX1gtflp91CnQKT6BBtpS\n'
                         'w8xp2Jt+47+wVty6wlLmqqZONbiCBlfAp1YEm3+Pxs/xm1qti1/CuT6VGsnm30Py7fyNQ1fAJQRA\n'
                         'yQP4MPUahz+AS1vpMf6x/Kr+lVbwTr3GsWsVkX/v592whR7jH8tX74nXSTSeS6/k0ypjFv8GAtca\n'
                         'aW/6jf/cbuqj/KKCKwhMgg+dzn6dw3l3+o3/wlredPNELZLqi7JKvCy/OhrfvFoLIqBm0ppAg5uz\n'
                         'aE2Yf4/My8gk8lqnvlpbz/Kaputov7P57zH5uf88dAXyQP2J0pZKPpV1A3pv+o3/J97rRcC1ThY+\n'
                         'TUIbIhWIZ5sfHZRf959rmyq11Kp6GpjPZDt/D8ijt9YmwXX0u3h63jb/HpJf7k9qYBLIIu2bnftV\n'
                         'E2uv+o3/0O7mg7UWqgGbuI4bin2fj80v9ydrLTS1ZRSR+d2Weox/Eh+HebQfz9fEK4t8xD9bj/E/\n'
                         '4u/vTwIg0Jd6k7JOCt8202P8c3h3bT27iyz1b72JFehUxk31GP8YfnUrh6UgWqVbdn/j0LzY/7uN\n'
                         'N9544403fnP+L+ApxaQY9nyeAAAAAElFTkSuQmCC\n')
