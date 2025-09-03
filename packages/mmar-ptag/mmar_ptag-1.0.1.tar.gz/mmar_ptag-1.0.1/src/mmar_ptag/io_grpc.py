from concurrent import futures

import grpc


def grpc_server(max_workers: int, port: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    server.add_insecure_port(f"[::]:{port}")
    return server
