python3 -m grpc_tools.protoc -Iprotos --python_out=protos --pyi_out=protos --grpc_python_out=protos service.proto

# Fix imports to be relative
sed -i '' 's/import \([^ ]*\)_pb2/from . import \1_pb2/g' protos/service_pb2_grpc.py
