import asyncio
import grpc
import pickle
import itertools
import logging
import stadle.lib.grpc_handler.comm_pb2 as comm_pb2
import stadle.lib.grpc_handler.comm_pb2_grpc as comm_pb2_grpc

import base64
import uuid

from stadle.lib.logging.logger import Logger

log = Logger("GRPC Client")

class GRPCClient:
    def __init__(self, protocol, cert_path=None, max_retries=10, retry_base_delay=2, chunk_size=1024 * 1024):
        self.protocol = protocol

        self.ssl = (protocol == 'https')
        self.client_credentials = None

        # if cert_path is not None:
        #     self.cert_path = cert_path
        #     self.ssl = True

        #     with open(self.cert_path, 'rb') as f:
        #         trusted_certs = f.read()

        #     self.client_credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)

        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.chunk_size = chunk_size

        self.address_channels = {}

        self.sending_cnt = 0

        if (self.ssl):
            with open(cert_path, 'rb') as f:
                self.tls_cert = f.read()

    async def _get_channel_and_stub(self, address):
        if (address not in self.address_channels):
            # print(self.address_channels)
            log.logger.debug(f"Creating new gRPC channel ({address})")

            if (self.ssl):
                log.logger.debug('Using secure channel')
                channel = grpc.aio.secure_channel(
                    address,
                    grpc.ssl_channel_credentials(
                        root_certificates=self.tls_cert
                    ),
                    options=[
                        ("grpc.max_send_message_length", 100 * 1024 * 1024),
                        ("grpc.max_receive_message_length", 100 * 1024 * 1024),
                        ('grpc.ssl_target_name_override', 'tieset.com')
                    ]
                )
            else:
                channel = grpc.aio.insecure_channel(
                    address,
                    options=[
                        ("grpc.max_send_message_length", 100 * 1024 * 1024),
                        ("grpc.max_receive_message_length", 100 * 1024 * 1024),
                    ]
                )
            stub = comm_pb2_grpc.CommServiceStub(channel)
            self.address_channels[address] = (channel, stub)

            log.logger.debug('Channel created')

            # TODO robustness checking
            # try:
            #     await grpc.channel_ready_future(channel).result(timeout=30)
            #     logging.debug(f"Channel to {address} is ready.")
            # except grpc.FutureTimeoutError:
            #     logging.warning(f"Channel to {address} was cancelled or closed, recreating.")
            #     del self.address_channels[address]
            #     return await self._get_channel_and_stub(address)
            # except Exception as e:
            #     logging.error(f"Error waiting for channel connection to {address}: {e}", exc_info=True)
            #     if address in self.address_channels:
            #         await self.address_channels[address][0].close()
            #         del self.address_channels[address]
            #     raise

        return self.address_channels[address]

    def _chunk_data(self, message_id, data):
        chunks = [data[i:i + self.chunk_size] for i in range(0, len(data), self.chunk_size)]
        total = len(chunks)
        for i, chunk in enumerate(chunks):
            yield comm_pb2.ChunkMessage(
                message_id=message_id,
                chunk_index=i,
                total_chunks=total,
                chunk_data=chunk
            )

    def is_sending(self):
        return self.sending_cnt > 0

    async def send(self, msg, address):
        data = pickle.dumps(msg)
        message_id = f"msg-{str(uuid.uuid4())}"
        
        #print(f'Sending:\n{msg}')
        
        retries = 0

        self.sending_cnt += 1

        while retries < self.max_retries:
            try:
                channel, stub = await self._get_channel_and_stub(address)

                stub = comm_pb2_grpc.CommServiceStub(channel)

                async def req_stream():
                    for chunk in self._chunk_data(message_id, data):
                        yield chunk

                call = stub.ChunkedMessageStream(req_stream(), wait_for_ready=False)

                chunks = {}
                total = None
                async for resp in call:
                    if resp.message_id != message_id:
                        continue
                    chunks[resp.chunk_index] = resp.chunk_data
                    total = resp.total_chunks
                    if len(chunks) == total:
                        break

                full = b''.join(chunks[i] for i in range(total))

                self.sending_cnt -= 1

                resp = pickle.loads(full)
                
                # print(f'Received:\n{resp}')

                return resp

            except grpc.aio.AioRpcError as e:
                retries += 1
                log.logger.warning(f"Retry {retries}/{self.max_retries} after gRPC error: {e.code()} - {e.details()}")
                await asyncio.sleep(self.retry_base_delay * retries)

        raise RuntimeError(f"Failed to send message after {self.max_retries} retries.")
