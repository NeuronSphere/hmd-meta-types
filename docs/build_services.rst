Building Services
=================

The ultimate goal of providing classes generated defined by HMD schema files to create and expose different operations on those classes. 
For example, we will want basic CRUD functionality on almost all Nouns defined. 
To accomplish this we must build services on top of a subset of the vocabulary that expose the basic CRUD operations. In addition, we should easily be able to override, add and extend operations of a given service.

In order to simplify development of services, we make the following assumptions:

* A service expose one or more operations
* A service may contain one or more Handlers that provide the context and execution of operations
* A service has one entrypoint that accepts a standard event payload that it uses to call the appropriate Handler
* An operation will only accept as its arguments the event payload and a context object from the service
* The context object will contain at least a map of all generated classes (with appropriate Extensions applied), and a storage engine to handle querying and persisting of class instances
* The context object may contain additional properties as required by the service

Operations are registered to a service instance through a decorator.

.. code-block::

    from hmd_base_service import service

    # Exposes an operation named "search" which requires the Noun to have a classmethod "search_query"
    # It can be accessed via an HTTP POST /api/<class_name>/ through the REST Handler
    # or GraphQL query of search{class_name} through the GraphQL Handler
    @service.operation(
        requires=["search_query"],
        rest_path="/api/<class_name>/",
        rest_methods=["POST"],
        graphql="search{class_name}"
    )
    def search(event, context):
        class_name = evt["class_name"]
        noun = ctx["loader"].get(class_name)
        
        return noun.search_query(ctx["storage"])


The first argument to any operation is an ``event``.  While this may be slightly different depending on the calling Handler, it will always have the following properties.

.. code-block::

    {
        "class_name": "<the name of the generated class to operate on>",
        "payload": "<the data sent in from the initial request>"
    }


The Service will also receive an ``event`` from its entrypoint with the following structure that it must route to the appropriate Handler.

.. code-block::

    {
        "path": "<the path to the Handler, e.g. HTTP URL path>",
        "payload": "<main data payload, e.g. HTTP body>"
    }


A basic Service implementation will look as follows:

.. code-block::

    class BasicService:
        def __init__(self, loader=DefaultLoader(), storage=StorageEngine()):
            self.loader = loader
            self.storage = storage
            self.handlers = {}
            self.operations = {}

        def execute(self, evt, ctx):
            evt_path = evt["path"]
            ctx = {"loader": self.loader, "storage": self.storage, **ctx}
            for h_path, handler in self.handlers.items():
                if h_path in evt_path:
                    handler.execute(evt, ctx)
                    break

        def run(self):
            exts = []
            for _, handler in self.handlers.items():
                handler.setup(self.operations)
                exts.append(handler.extensions)

            self.loader.load(extensions=exts)

        def register_handler(handler, base_path):
            self.handlers[base_path] = handler

        def operation(requires=list(), **kwds):
            def decorator(fn):
                self.operations[fn.__name__] = { "fn": fn, "required":required, **kwds}


Creation of above service in a deployable Docker image would look as follows

.. code-block::

    # service.py
    svc = BasicService()

    class RestHandler:
        extensions = [MariaDBExtension]

        def __init__(self):
            self.routes = {}

        def setup(self, operations):
            for name, op in operations.items():
                if "rest_path" in op:
                    self.routes[op["rest_path"]] = {"methods": op.get("rest_methods", []), "fn": op["fn"]}

        def exectute(self, evt, ctx):
            evt_path = evt["path"]
            evt_method = evt.get("method", None)

            class_name = get_class_name(evt_path) # somehow extract the class name from the path

            op = get_route(evt[path]) # regex or something to grab the correct route, look at how Flask does it
            if evt_method in op["methods"]:
                event = {"class_name": class_name, **evt}
                return op["fn"](event, ctx)


    class GraphQLHandler:
        extensions = [GraphQLExtension, MariaDBExtension]

        def __init__(self):
            self.schema = GraphQLSchema()

        def setup(self, operations):
            # Loop through operations and build GraphQL schema

        def exectute(self, evt, ctx):
            # Extract class name
            # Execute correct query agains schema

    svc.register_handler(RestHandler())
    svc.register_handler(GraphQLHandler())

    @svc.operation(
        requires=["search_query"],
        rest_path="/api/<class_name>/",
        rest_methods=["POST"],
        graphql="search{class_name}"
    )
    def search(event, context):
        class_name = evt["class_name"]
        noun = ctx.get_noun(class_name)
        
        return noun.search_query(ctx["storage"])

    @svc.operation(
        requires=["get_query"],
        rest_path="/api/<class_name>/<id>",
        rest_methods=["POST"],
        graphql="get{class_name}"
    )
    def get(event, context):
        class_name = evt["class_name"]
        noun = ctx.get_noun(class_name)
        
        return noun.get_query(ctx["storage"], evt["parameters"]["id"])

    @svc.operation(
        requires=["put_query"],
        rest_path="/api/<class_name>/",
        rest_methods=["POST"],
        graphql="put{class_name}"
    )
    def put(event, context):
        class_name = evt["class_name"]
        noun = ctx.get_noun(class_name)
        
        return noun.put_query(ctx["storage"], noun(**evt["payload"])

    # Optionally in a Docker image include a user defined operations.py file??
    if os.path.exists("./operations.py"):
        import operations

    # Setups all registered handlers with the exposed operations
    svc.run()

    def main(evt, ctx):
        return svc.execute(evt, ctx):
