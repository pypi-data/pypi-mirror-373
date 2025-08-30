import numpy as np
import os
import io
import logging
import tempfile
from skimage.exposure import rescale_intensity, equalize_adapthist, adjust_sigmoid
from skimage.util import img_as_bool, view_as_windows, img_as_ubyte
from skimage.io import imread, imsave
from .utils import pad_to_n
from .utils import bw_watershed
from .utils import plot_contours
from .utils import extract_regionprops
from dask.distributed import Client
from dask.distributed import print
import dask.array as da
from dask.diagnostics import ProgressBar

from labcas.workflow.manager import DataStore

logger = logging.getLogger(__name__)


class NucleiDetectorUnet:
    def __init__(self, tile_size):
        from keras.models import load_model
        model_dir = os.path.join(
            os.path.dirname(__file__),
            'models'
        )
        self.model = load_model(os.path.join(model_dir, f'unet_{tile_size}.raw'))
        self.logger = logger
        self.logger.info('model loaded')

    def predict(self, img: np.ndarray):
        os.environ["OMP_NUM_THREADS"] = '1'
        p = self.model.predict(img)
        print(type(p))
        return p


def decode_img(data):
    data = io.BytesIO(data)
    return imread(data)


def process_img(in_datastore: DataStore, out_datastore: DataStore, key: str, tile_size=64, csv=True):
    # Read the file content
    img_data = in_datastore.get_input_content(key, decode_img)

    print('rescaling intensity')
    im = rescale_intensity(1.0 * img_data)
    print('adjusting sigmoid')
    im = adjust_sigmoid(equalize_adapthist(im))

    # store image shape before padding
    sh = im.shape
    print('padding')
    im = pad_to_n(im, w=tile_size)

    # print('tiling the images')
    # bw = np.zeros_like(im)

    # Convert image and mask to dask arrays with chunking based on tile_size
    imw = da.from_array(im, chunks=(tile_size, tile_size))

    print('launch predictions 2')

    def process_tile(tile) -> np.ndarray:
        img = np.expand_dims(tile, axis=[0, 3])
        p = NucleiDetectorUnet(tile_size).predict(img)[0, :, :, 0]
        return p > 0.5

    # Apply function across chunks
    results = imw.map_blocks(lambda tile: process_tile(tile), dtype=bool)

    # Compute the results
    with ProgressBar():
        bw = results.compute()

    print('stitching together')
    # revert back to original image shape
    im = im[:sh[0], :sh[1]]
    bw = bw[:sh[0], :sh[1]]
    bw = img_as_bool(bw)

    print('running watershed postprocessing')
    # postprocess
    bw = bw_watershed(bw)

    in_filename = key.split("/")[-1]
    name = in_filename.split(".")[0]
    ext = in_filename.split(".")[1]
    bw_filename = name + "_bw." + ext
    contour_filename = name + "_ov." + ext

    print('saving BW image.')
    temp_bw_file = tempfile.NamedTemporaryFile(suffix='.png')
    imsave(temp_bw_file.name, img_as_ubyte(bw), check_contrast=False)
    temp_bw_file.seek(0)
    out_datastore.write_output(bw_filename, temp_bw_file)

    print('plotting contours')
    temp_contours_file = tempfile.NamedTemporaryFile(suffix='.png')
    plot_contours(bw, im, temp_contours_file)
    temp_contours_file.seek(0)
    out_datastore.write_output(contour_filename, temp_contours_file)

    if csv:
        print('extracting region props')
        csv_filename = name + ".csv"
        image_df = extract_regionprops(img_data, temp_bw_file)
        csv_buffer = io.StringIO()
        image_df.to_csv(csv_buffer)
        out_datastore.write_output(csv_filename, csv_buffer.getvalue(), content_type="text/csv")


def process_img_local(client: Client, in_datastore: DataStore, out_datastore: DataStore, key: str, tile_size=64, ):
    # Read the file content
    img_data = in_datastore.get_input_content(key, decode_img)

    print('rescaling intensity')
    im = rescale_intensity(1.0 * img_data)
    print('adjusting sigmoid')
    im = adjust_sigmoid(equalize_adapthist(im))

    # store image shape before padding
    sh = im.shape
    print('padding')
    im = pad_to_n(im, w=tile_size)

    print('tiling the images')
    bw = np.zeros_like(im)
    imw = view_as_windows(im, (tile_size, tile_size), (tile_size, tile_size))
    imb = view_as_windows(bw, (tile_size, tile_size), (tile_size, tile_size))

    print('launch predictions')
    model_instance = NucleiDetectorUnet64()

    for i in range(imb.shape[0]):
        print('i:', i, imb.shape[0])
        for j in range(imb.shape[1]):
            img = np.expand_dims(imw[i, j, ...], axis=[0, 3])
            p = model_instance.predict(img)
            p = p[0, :, :, 0]
            b = p > 0.5
            imb[i, j, ...] = b

    print('stitching together')
    # revert back to original image shape
    im = im[:sh[0], :sh[1]]
    bw = bw[:sh[0], :sh[1]]
    bw = img_as_bool(bw)

    print('running watershed postprocessing')
    # postprocess
    bw = bw_watershed(bw)

    in_filename = key.split("/")[-1]
    name = in_filename.split(".")[0]
    ext = in_filename.split(".")[1]
    bw_filename = name + "_bw." + ext
    csv_filename = name + ".csv"
    contour_filename = name + "_ov." + ext

    print('saving BW image.')
    temp_bw_file = tempfile.NamedTemporaryFile(suffix='.png')
    imsave(temp_bw_file.name, img_as_ubyte(bw), check_contrast=False)
    temp_bw_file.seek(0)
    out_datastore.write_output(bw_filename, temp_bw_file)

    print('plotting contours')
    temp_contours_file = tempfile.NamedTemporaryFile(suffix='.png')
    plot_contours(bw, im, temp_contours_file)
    temp_contours_file.seek(0)
    out_datastore.write_output(contour_filename, temp_contours_file)

    print('extracting region props')
    image_df = extract_regionprops(img_data, temp_bw_file)
    csv_buffer = io.StringIO()
    image_df.to_csv(csv_buffer)
    out_datastore.write_output(csv_filename, csv_buffer.getvalue(), content_type="text/csv")
