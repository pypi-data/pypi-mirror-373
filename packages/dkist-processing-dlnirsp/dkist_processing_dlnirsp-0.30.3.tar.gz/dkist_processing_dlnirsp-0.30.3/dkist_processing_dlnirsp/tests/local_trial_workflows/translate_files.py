import argparse
import os
import sys
from pathlib import Path

from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_service_configuration.logging import logger


def translate_dir(raw_dir: str | Path, output_dir: str | Path, suffix: str = "FITS") -> None:
    if isinstance(raw_dir, str):
        raw_dir = Path(raw_dir)

    if isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(exist_ok=True)

    for file in raw_dir.glob(f"*.{suffix}"):
        translated_file_name = output_dir / os.path.basename(file)
        logger.info(f"Translating {file} -> {translated_file_name}")
        hdl = fits.open(file)
        # Handle both compressed and uncompressed files...
        if len(hdl) > 1:
            hdl_header = hdl[1].header
            hdl_data = hdl[1].data
        else:
            hdl_header = hdl[0].header
            hdl_data = hdl[0].data
        header = spec122_validator.validate_and_translate_to_214_l0(
            hdl_header, return_type=fits.HDUList
        )[0].header

        comp_hdu = fits.CompImageHDU(header=header, data=hdl_data)
        comp_hdl = fits.HDUList([fits.PrimaryHDU(), comp_hdu])
        comp_hdl.writeto(translated_file_name, overwrite=True)

        hdl.close()
        del hdl
        comp_hdl.close()
        del comp_hdl


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Translate a directory of SPEC-122 files to SPEC-214L0 files"
    )
    parser.add_argument("raw_dir", help="Location of raw SPEC-122 files")
    parser.add_argument("output_dir", help="Location to save SPEC-214L0 files")
    parser.add_argument("--suffix", help="Suffix of raw input files to glob on", default="FITS")

    args = parser.parse_args()

    sys.exit(translate_dir(raw_dir=args.raw_dir, output_dir=args.output_dir, suffix=args.suffix))
