from blissoda.demo.id31_streamline import streamline_scanner


def streamline_demo(with_autocalibration=False):
    # Nothing loaded and 2 holders in the tray:
    streamline_scanner.eject()
    streamline_scanner.sample_changer.fill_tray(2)

    # Initialize workflow with or without calibration
    streamline_scanner.init_workflow(with_autocalibration=with_autocalibration)
    if with_autocalibration:
        streamline_scanner.calib(0.1)

    # Measure all holders
    streamline_scanner.run(0.1)
