from labcas.workflow.manager import DataStore

def process_collection(in_bucket, in_prefix, out_bucket, out_prefix, fun, kwargs):
    # Use a breakpoint in the code line below to debug your script.

    in_datastore = DataStore(in_bucket, in_prefix)
    out_datastore = DataStore(out_bucket, out_prefix)

    for obj in in_datastore.get_inputs():
        in_key = obj['Key']
        print(in_key)
        fun(
            in_datastore,
            out_datastore,
            in_key,
            **kwargs
        )
