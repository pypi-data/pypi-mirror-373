import argparse
from labcas.workflow.manager import process_collection
from labcas.workflow.steps.alphan.process import process_img
from distributed import Client

from distributed.security import Security

# TODO: add ssl certification to access the dask cluster
# sec = Security(
#     tls_ca_file=os.getenv("DASK_TLS_CA"),
#     tls_client_cert=os.getenv("DASK_TLS_CERT"),
#     tls_client_key=os.getenv("DASK_TLS_KEY"),
#     require_encryption=True
# )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='collection-parallel-processor',
        description='This is a wrapper to apply process parallely on collection entries')

    #client = Client('tcp://127.0.0.1:8786')
    client = Client()
    process_collection(
        'edrn-bucket',
        'nebraska_images/',
        'edrn-bucket',
        'nebraska_images_nuclei/',
        process_img,
        dict(tile_size=64)
    )

