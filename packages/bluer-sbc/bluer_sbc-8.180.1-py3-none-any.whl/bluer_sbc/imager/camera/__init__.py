from bluer_options import host

if host.is_rpi():
    if host.is_64bit():
        from bluer_sbc.imager.camera.rpi_64_bit import RPI_64_bit_Camera as Camera
    else:
        from bluer_sbc.imager.camera.rpi import RPI_Camera as Camera
else:
    from bluer_sbc.imager.camera.generic import Camera

instance = Camera()
