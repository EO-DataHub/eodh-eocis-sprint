

from datacube.drivers.netcdf.driver import NetcdfReaderDriver, NetcdfWriterDriver
from ._rio_x import RasterDatasetDataSource
PROTOCOL = 'file'
FORMAT = 'NetCDFX'


class NetcdfReaderDriverX(object):
    def __init__(self):
        print("NetcdfReaderDriverXXX")
        self.name = 'NetcdfReader'
        self.protocols = [PROTOCOL]
        self.formats = [FORMAT]

    def supports(self, protocol, fmt):
        return fmt.lower() == "netcdfx"

    def new_datasource(self, band):
        return RasterDatasetDataSource(band)


def reader_driver_init():
    return NetcdfReaderDriverX()

def writer_driver_init():
    return NetcdfWriterDriver()
