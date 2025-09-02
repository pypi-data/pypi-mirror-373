"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from ..requests import add_book_instance_pb2 as requests_dot_add__book__instance__pb2
from ..requests import remove_book_instance_pb2 as requests_dot_remove__book__instance__pb2
from ..requests import retrieve_book_pb2 as requests_dot_retrieve__book__pb2
from ..requests import retrieve_book_procedures_pb2 as requests_dot_retrieve__book__procedures__pb2
from ..requests import retrieve_books_pb2 as requests_dot_retrieve__books__pb2
from ..requests import retrieve_tags_pb2 as requests_dot_retrieve__tags__pb2
from ..requests import test_connection_pb2 as requests_dot_test__connection__pb2
from ..responses import add_book_instance_pb2 as responses_dot_add__book__instance__pb2
from ..responses import remove_book_instance_pb2 as responses_dot_remove__book__instance__pb2
from ..responses import retrieve_book_pb2 as responses_dot_retrieve__book__pb2
from ..responses import retrieve_book_procedures_pb2 as responses_dot_retrieve__book__procedures__pb2
from ..responses import retrieve_books_pb2 as responses_dot_retrieve__books__pb2
from ..responses import retrieve_tags_pb2 as responses_dot_retrieve__tags__pb2
from ..responses import test_connection_pb2 as responses_dot_test__connection__pb2

class LibraryServiceStub(object):
    """
    LibraryService provides read-only operations for discovering and inspecting books
    in the BDK (Book Development Kit) ecosystem. This service is designed for
    library management and book metadata retrieval without executing book procedures.

    Use cases:
    - Browsing available books and their metadata
    - Discovering book capabilities and procedures
    - Testing book connectivity before execution
    - Retrieving book categorization tags
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RetrieveBooks = channel.unary_unary('/protocol.LibraryService/RetrieveBooks', request_serializer=requests_dot_retrieve__books__pb2.RetrieveBooksRequest.SerializeToString, response_deserializer=responses_dot_retrieve__books__pb2.RetrieveBooksResponse.FromString, _registered_method=True)
        self.RetrieveBook = channel.unary_unary('/protocol.LibraryService/RetrieveBook', request_serializer=requests_dot_retrieve__book__pb2.RetrieveBookRequest.SerializeToString, response_deserializer=responses_dot_retrieve__book__pb2.RetrieveBookResponse.FromString, _registered_method=True)
        self.RetrieveBookProcedures = channel.unary_unary('/protocol.LibraryService/RetrieveBookProcedures', request_serializer=requests_dot_retrieve__book__procedures__pb2.RetrieveBookProceduresRequest.SerializeToString, response_deserializer=responses_dot_retrieve__book__procedures__pb2.RetrieveBookProceduresResponseV2.FromString, _registered_method=True)
        self.TestConnection = channel.unary_unary('/protocol.LibraryService/TestConnection', request_serializer=requests_dot_test__connection__pb2.TestConnectionRequest.SerializeToString, response_deserializer=responses_dot_test__connection__pb2.TestConnectionResponse.FromString, _registered_method=True)
        self.RetrieveTags = channel.unary_unary('/protocol.LibraryService/RetrieveTags', request_serializer=requests_dot_retrieve__tags__pb2.RetrieveTagsRequest.SerializeToString, response_deserializer=responses_dot_retrieve__tags__pb2.RetrieveTagsResponse.FromString, _registered_method=True)
        self.AddBookInstance = channel.unary_unary('/protocol.LibraryService/AddBookInstance', request_serializer=requests_dot_add__book__instance__pb2.AddBookInstanceRequest.SerializeToString, response_deserializer=responses_dot_add__book__instance__pb2.AddBookInstanceResponse.FromString, _registered_method=True)
        self.RemoveBookInstance = channel.unary_unary('/protocol.LibraryService/RemoveBookInstance', request_serializer=requests_dot_remove__book__instance__pb2.RemoveBookInstanceRequest.SerializeToString, response_deserializer=responses_dot_remove__book__instance__pb2.RemoveBookInstanceResponse.FromString, _registered_method=True)

class LibraryServiceServicer(object):
    """
    LibraryService provides read-only operations for discovering and inspecting books
    in the BDK (Book Development Kit) ecosystem. This service is designed for
    library management and book metadata retrieval without executing book procedures.

    Use cases:
    - Browsing available books and their metadata
    - Discovering book capabilities and procedures
    - Testing book connectivity before execution
    - Retrieving book categorization tags
    """

    def RetrieveBooks(self, request, context):
        """
        Retrieves a list of all available books in the library.

        This endpoint returns metadata for all books that are currently available
        in the runtime, including their names, versions, descriptions, authentication
        requirements, and capabilities.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RetrieveBook(self, request, context):
        """
        Retrieves detailed information about a specific book version.

        This endpoint provides comprehensive metadata about a particular book,
        including its description, author, icon, authentication mechanisms,
        configuration parameters, and capabilities.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RetrieveBookProcedures(self, request, context):
        """
        Retrieves all available procedures for the specified book version.

        This endpoint returns a list of all procedures (functions/operations) that
        can be invoked on the specified book, along with their signatures, input/output
        parameters, and metadata such as descriptions and examples.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TestConnection(self, request, context):
        """
        Tests the connectivity and authentication for a specific book.

        This endpoint validates that the provided authentication credentials work
        correctly with the specified book. It's used to verify book connectivity
        before attempting to invoke procedures that require authentication.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RetrieveTags(self, request, context):
        """
        Retrieves all available tags from all books in the library.

        This endpoint returns a consolidated list of all tags used across all books
        in the library. Tags are used for categorizing and organizing books by
        functionality, domain, or other characteristics.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddBookInstance(self, request, context):
        """
        Adds a new instance of a book to the library.

        This endpoint adds a new instance of a book, which can be used to invoke
        procedures on the book.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveBookInstance(self, request, context):
        """
        Removes an instance of a book from the library.
        This endpoint removes an instance of a book from the library.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_LibraryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'RetrieveBooks': grpc.unary_unary_rpc_method_handler(servicer.RetrieveBooks, request_deserializer=requests_dot_retrieve__books__pb2.RetrieveBooksRequest.FromString, response_serializer=responses_dot_retrieve__books__pb2.RetrieveBooksResponse.SerializeToString), 'RetrieveBook': grpc.unary_unary_rpc_method_handler(servicer.RetrieveBook, request_deserializer=requests_dot_retrieve__book__pb2.RetrieveBookRequest.FromString, response_serializer=responses_dot_retrieve__book__pb2.RetrieveBookResponse.SerializeToString), 'RetrieveBookProcedures': grpc.unary_unary_rpc_method_handler(servicer.RetrieveBookProcedures, request_deserializer=requests_dot_retrieve__book__procedures__pb2.RetrieveBookProceduresRequest.FromString, response_serializer=responses_dot_retrieve__book__procedures__pb2.RetrieveBookProceduresResponseV2.SerializeToString), 'TestConnection': grpc.unary_unary_rpc_method_handler(servicer.TestConnection, request_deserializer=requests_dot_test__connection__pb2.TestConnectionRequest.FromString, response_serializer=responses_dot_test__connection__pb2.TestConnectionResponse.SerializeToString), 'RetrieveTags': grpc.unary_unary_rpc_method_handler(servicer.RetrieveTags, request_deserializer=requests_dot_retrieve__tags__pb2.RetrieveTagsRequest.FromString, response_serializer=responses_dot_retrieve__tags__pb2.RetrieveTagsResponse.SerializeToString), 'AddBookInstance': grpc.unary_unary_rpc_method_handler(servicer.AddBookInstance, request_deserializer=requests_dot_add__book__instance__pb2.AddBookInstanceRequest.FromString, response_serializer=responses_dot_add__book__instance__pb2.AddBookInstanceResponse.SerializeToString), 'RemoveBookInstance': grpc.unary_unary_rpc_method_handler(servicer.RemoveBookInstance, request_deserializer=requests_dot_remove__book__instance__pb2.RemoveBookInstanceRequest.FromString, response_serializer=responses_dot_remove__book__instance__pb2.RemoveBookInstanceResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('protocol.LibraryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('protocol.LibraryService', rpc_method_handlers)

class LibraryService(object):
    """
    LibraryService provides read-only operations for discovering and inspecting books
    in the BDK (Book Development Kit) ecosystem. This service is designed for
    library management and book metadata retrieval without executing book procedures.

    Use cases:
    - Browsing available books and their metadata
    - Discovering book capabilities and procedures
    - Testing book connectivity before execution
    - Retrieving book categorization tags
    """

    @staticmethod
    def RetrieveBooks(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/protocol.LibraryService/RetrieveBooks', requests_dot_retrieve__books__pb2.RetrieveBooksRequest.SerializeToString, responses_dot_retrieve__books__pb2.RetrieveBooksResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def RetrieveBook(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/protocol.LibraryService/RetrieveBook', requests_dot_retrieve__book__pb2.RetrieveBookRequest.SerializeToString, responses_dot_retrieve__book__pb2.RetrieveBookResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def RetrieveBookProcedures(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/protocol.LibraryService/RetrieveBookProcedures', requests_dot_retrieve__book__procedures__pb2.RetrieveBookProceduresRequest.SerializeToString, responses_dot_retrieve__book__procedures__pb2.RetrieveBookProceduresResponseV2.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def TestConnection(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/protocol.LibraryService/TestConnection', requests_dot_test__connection__pb2.TestConnectionRequest.SerializeToString, responses_dot_test__connection__pb2.TestConnectionResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def RetrieveTags(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/protocol.LibraryService/RetrieveTags', requests_dot_retrieve__tags__pb2.RetrieveTagsRequest.SerializeToString, responses_dot_retrieve__tags__pb2.RetrieveTagsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def AddBookInstance(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/protocol.LibraryService/AddBookInstance', requests_dot_add__book__instance__pb2.AddBookInstanceRequest.SerializeToString, responses_dot_add__book__instance__pb2.AddBookInstanceResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def RemoveBookInstance(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/protocol.LibraryService/RemoveBookInstance', requests_dot_remove__book__instance__pb2.RemoveBookInstanceRequest.SerializeToString, responses_dot_remove__book__instance__pb2.RemoveBookInstanceResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)