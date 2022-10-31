import argparse

from tesseract_ocr.tesseract import *

if __name__ == '__main__':
    try:
        # create parser object
        parser = argparse.ArgumentParser()

        # Adding arguments
        parser.add_argument("--input", "-i", help="Input Image File Path", required=True)
        parser.add_argument("--psm", help="Page Segmentation Method", type=int, default=1)
        parser.add_argument("--oem", help="Engine Type", type=int, default=1)
        parser.add_argument("--output_format", nargs='+', help="List possible output formats needed", default=['txt'])
        parser.add_argument("--char_wise_extraction", help="Set True for Character Level Extraction", type=bool,
                            default=False)

        # Read arguments from command line
        args = parser.parse_args()

        lstr_input_image_path = args.input
        lint_oem = args.oem
        lint_psm = args.psm

        # Set Default values
        lbool_generate_text_output = False
        lbool_generate_box_output = False
        lbool_generate_tsv_output = False
        lbool_char_wise_extraction = False
        lbool_generate_hocr_output = False

        # Change as per input received
        if 'txt' in args.output_format:
            lbool_generate_text_output = True
        if 'box' in args.output_format:
            lbool_generate_box_output = True
        if 'tsv' in args.output_format:
            lbool_generate_tsv_output = True
        if 'hocr' in args.output_format:
            lbool_generate_hocr_output = True
            if args.char_wise_extraction:
                lbool_char_wise_extraction = True

        ldict_output = run_tesseract_ocr(pstr_input_img_path=lstr_input_image_path,
                                         pint_psm=lint_psm, pint_oem=lint_oem,
                                         pbol_generate_tsv_output=lbool_generate_tsv_output,
                                         pbol_generate_text_output=lbool_generate_text_output,
                                         pbol_generate_box_output=lbool_generate_box_output,
                                         pbol_generate_hocr_output=lbool_generate_hocr_output,
                                         pbol_char_wise_extraction=lbool_char_wise_extraction)

        # print(ldict_output)
    except Exception as e:
        logger.error(str(e))
