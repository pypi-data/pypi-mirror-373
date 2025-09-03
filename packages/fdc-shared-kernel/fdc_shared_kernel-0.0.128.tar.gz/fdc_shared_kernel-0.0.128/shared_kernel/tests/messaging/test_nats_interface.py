# import pytest
# from asynctest import CoroutineMock, patch
# from shared_kernel.messaging import NATSInterface
#
# @pytest.fixture
# async def nats_interface():
#     nats = NATSInterface(servers=None)
#     await nats.connect()
#     yield nats
#     await nats.close()
#
# @pytest.mark.asyncio
# @patch('shared_kernel.messaging.NATSInterface.connect', new_callable=CoroutineMock)
# @patch('shared_kernel.messaging.NATSInterface.close', new_callable=CoroutineMock)
# async def test_connect_and_close(mock_connect, mock_close, nats_interface):
#     await nats_interface.connect()
#     mock_connect.assert_called_once()
#
#     await nats_interface.close()
#     mock_close.assert_called_once()
#
# @pytest.mark.asyncio
# @patch('shared_kernel.messaging.NATSInterface.publish', new_callable=CoroutineMock)
# async def test_publish(mock_publish, nats_interface):
#     await nats_interface.connect()
#     await nats_interface.publish("test_subject", "Hello, NATS!")
#     mock_publish.assert_called_once_with("test_subject", b"Hello, NATS!")
#     await nats_interface.close()
#
# @pytest.mark.asyncio
# @patch('shared_kernel.messaging.NATSInterface.subscribe', new_callable=CoroutineMock)
# async def test_subscribe(mock_subscribe, nats_interface):
#     await nats_interface.connect()
#
#     async def mock_callback(msg):
#         return None
#
#     await nats_interface.subscribe("test_subject", mock_callback)
#     mock_subscribe.assert_called_once_with("test_subject", cb=mock_callback)
#     await nats_interface.close()
