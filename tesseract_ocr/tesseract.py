import csv
import os
import shutil
from subprocess import Popen, PIPE
from timeit import default_timer as timer

import pandas as pd
from lxml import etree

from tesseract_ocr.exceptions.exceptions import *
from tesseract_ocr.exceptions.logger import logger


# Decorator function for time consumption of methods
def time_it(func):
    def run(*args, **kwargs):
        # start timer
        start_time = timer()

        # runs the function passes as input to decorator function
        result = func(*args, **kwargs)

        # end timer
        end_time = timer()

        # calculate time consumed
        time_taken = end_time - start_time

        # round up time
        round_time = round(time_taken, 2)

        # add log info
        logger.info(f"Time Taken By function {func.__name__}: " + str(round_time))

        # return results
        return result

    # call run  function
    return run


@time_it
def run_tesseract_ocr(pstr_input_img_path, pstr_tesseract_command="tesseract",
                      pstr_model="eng", pint_psm=-1, pint_oem=-1, pbol_keep_output_file=False,
                      pbol_generate_tsv_output=False, pbol_generate_text_output=False,
                      pbol_generate_box_output=False, pbol_generate_hocr_output=False,
                      pbol_char_wise_extraction=False):
    ldict_ocr_output = {"txt": None, "box": None, "tsv": None, "hocr": None}
    try:
        if pstr_input_img_path and os.path.exists(pstr_input_img_path):
            # ===================================================================
            # set psm and oem
            # ===================================================================
            if pint_psm is None or not (isinstance(pint_psm, int)):
                pint_psm = -1
            elif -1 > pint_psm > 13:
                logger.info("Provided psm: " + str(pint_psm) + " is invalid. Please provide psm between 0-13."
                            + "\nCurrently using defualt psm")
                pint_psm = -1

            if pint_oem is None or not (isinstance(pint_oem, int)):
                pint_oem = -1
            elif -1 > pint_oem > 3:
                logger.info("Provided oem: " + str(pint_oem) + " is invalid. Please provide oem between 0-3."
                            + "\nCurrently using default oem")
                pint_oem = -1

            # ===================================================================
            # create command
            # ===================================================================
            lstr_command = None
            lstr_input_image_name_with_abs_path, _ = os.path.splitext(pstr_input_img_path)
            lstr_output_file_path_without_ext = lstr_input_image_name_with_abs_path

            if pint_psm == -1 and pint_oem == -1:
                lstr_command = pstr_tesseract_command + ' "' + pstr_input_img_path + '"' \
                               + ' "' + lstr_output_file_path_without_ext + '" -l "' + pstr_model + '" quiet'
            elif pint_psm != -1 and pint_oem != -1:
                lstr_command = pstr_tesseract_command + ' "' + pstr_input_img_path + '"' \
                               + ' "' + lstr_output_file_path_without_ext + '" -l "' + pstr_model + '"' \
                               + ' --psm ' + str(pint_psm) + ' --oem ' + str(pint_oem) + ' quiet'
            elif pint_psm == -1 and pint_oem != -1:
                lstr_command = pstr_tesseract_command + ' "' + pstr_input_img_path + '"' \
                               + ' "' + lstr_output_file_path_without_ext + '" -l "' + pstr_model + '"' \
                               + ' --oem ' + str(pint_oem) + ' quiet'
            elif pint_psm != -1 and pint_oem == -1:
                lstr_command = pstr_tesseract_command + ' "' + pstr_input_img_path + '"' \
                               + ' "' + lstr_output_file_path_without_ext + '" -l "' + pstr_model + '"' \
                               + ' --psm ' + str(pint_psm) + ' quiet'

            lstr_command += ' -c tessedit_do_invert=0'

            # ===================================================================
            # Add Expected Output Format
            # ===================================================================
            if pbol_char_wise_extraction:
                lstr_command += ' -c hocr_char_boxes=1'
            if pbol_generate_hocr_output:
                lstr_command += ' hocr'
            if pbol_generate_box_output:
                lstr_command += ' makebox'
            if pbol_generate_text_output:
                lstr_command += ' txt'
            if pbol_generate_tsv_output:
                lstr_command += ' tsv'

            # ===================================================================
            # executing command using subprocess
            # ===================================================================
            try:
                lobj_process = Popen(lstr_command, env={'OMP_THREAD_LIMIT': '1'}, stderr=PIPE, stdout=PIPE, shell=True)
            except Exception:
                raise

            # ===================================================================
            # check return code of process
            # if return code = 0 then process executed with no errors
            # otherwise process is failed
            # ===================================================================
            lbyt_output, lbyt_error = lobj_process.communicate()
            if lobj_process.returncode != 0:
                lstr_info = "Error: " \
                            + "\n1. tesseract command is not properly formed." \
                            + "\n2. tesseract is not installed \n" \
                            + "\nCommand: \n" + lstr_command \
                            + "\nInfo: \ntesseract failed with error code: %d and error: %s" % (
                                lobj_process.returncode, lbyt_error.decode("utf-8"))
                raise ConfigurationError(lstr_info)

            # ===================================================================
            # create result to return
            # ===================================================================
            if pbol_generate_text_output:
                lstr_ocr_file = lstr_output_file_path_without_ext + '.txt'
                # ===========================================================================
                # read output file created by tesseract and return predicted text
                # ===========================================================================

                lobj_file = open(lstr_ocr_file, "r")
                lstr_predicted_text = lobj_file.read()
                lobj_file.close()

                lstr_predicted_text = lstr_predicted_text.strip("\n").strip()
                ldict_ocr_output["txt"] = lstr_predicted_text

            if pbol_generate_box_output:
                # ===========================================================================
                # read output box file created by tesseract and return predicted text
                # ===========================================================================
                lobj_file = open(lstr_output_file_path_without_ext + '.box', "r")
                lstr_predicted_text = lobj_file.read()
                lobj_file.close()

                lstr_predicted_text = lstr_predicted_text.strip("\n").strip()
                lstr_predicted_text = lstr_predicted_text.split("\n")
                ldict_predicted_chars = dict()
                lstr_word = ""
                llst_temp_symbol = list()

                for lstr_symbol in lstr_predicted_text:
                    try:
                        llst_temp = lstr_symbol.split(" ")
                        lstr_word = lstr_word + str(llst_temp[0])
                        llst_temp_symbol.append({"symbol": llst_temp[0],
                                                 "position": [llst_temp[1], llst_temp[2], llst_temp[3],
                                                              llst_temp[4]]})
                        lint_page_no = llst_temp[4]
                    except IndexError:
                        logger.warning("Skipping symbol due to IndexError on : ", str(llst_temp))
                        continue
                ldict_predicted_chars["SegmentedWord"] = llst_temp_symbol
                ldict_predicted_chars["Word"] = lstr_word

                ldict_ocr_output["box"] = ldict_predicted_chars

            if pbol_generate_tsv_output:
                lstr_ocr_file = lstr_output_file_path_without_ext + ".tsv"
                # ===========================================================================
                # read output tsv file created by tesseract and return predicted text
                # ===========================================================================
                ldf_tsv = pd.read_csv(lstr_ocr_file, sep='\t', quoting=csv.QUOTE_NONE,
                                      encoding='utf-8')
                ldict_ocr_output["tsv"] = ldf_tsv

            if pbol_generate_hocr_output:
                lstr_ocr_file = lstr_output_file_path_without_ext + '.hocr'
                # ===========================================================================
                # read output hocr file created by tesseract and return predicted text
                # ===========================================================================
                llst_lines = []
                llst_words = []
                llst_word_details = []
                llst_char_details = []
                lobj_file = lstr_ocr_file
                line_num = 0
                ldict_line_details = {}
                doc = etree.parse(lobj_file)

                for path in doc.xpath('//*'):
                    if path.values():
                        if path.values()[1].find("line") != -1 and not ('ocr-capabilities' in path.values()):
                            line_num = path.values()[1].split("_")[2]
                            ldict_line_details[line_num] = path.values()[2].split()[1:5]

                        elif 'ocrx_word' in path.values():
                            llst_char_details.append([])
                            word_detailsplit = path.values()[2].split('x_wconf')
                            conf = word_detailsplit[1]
                            word_coords = word_detailsplit[0].split()[1:]
                            word_coords.append(conf)
                            llst_word_details.append(word_coords)
                            llst_lines.append(line_num)
                            if not pbol_char_wise_extraction:
                                llst_words.append(path.text)

                        elif 'ocrx_cinfo' in path.values():
                            llst_char_conf = path.values()[1].split()
                            llst_char_conf.append(path.text)
                            llst_char_details[-1].append(llst_char_conf)

                if pbol_char_wise_extraction:
                    for word_list in llst_char_details:
                        word_char_list = [x[-1] for x in word_list]
                        word = ''.join(word_char_list)
                        llst_words.append(word)

                llst_hocr_data = []
                for line, word, word_details, char_details in zip(llst_lines, llst_words, llst_word_details,
                                                                  llst_char_details):
                    if pbol_char_wise_extraction:
                        ldict_word = {
                            'LineX1': int(ldict_line_details[line][0]),
                            'LineY1': int(ldict_line_details[line][1]),
                            'LineX2': int(ldict_line_details[line][2]),
                            'LineY2': int(ldict_line_details[line][3].split(";")[0]),
                            'WordX1': int(word_details[0]),
                            'WordY1': int(word_details[1]),
                            'WordX2': int(word_details[2]),
                            'WordY2': int(word_details[3].split(";")[0]),
                            'Word': word,
                            'WordConf': int(word_details[-1]),
                            'CharDetails': [
                                {'Character': x[-1], 'CharPosition': num,
                                 'char_x1': int(x[1]), 'char_y1': int(x[2]), 'char_x2': int(x[3]),
                                 'char_y2': int(x[4].split(";")[0]),
                                 'char_conf': float(x[-2])} for num, x in enumerate(char_details)]
                        }
                    else:
                        ldict_word = {
                            'LineX1': int(ldict_line_details[line][0]),
                            'LineY1': int(ldict_line_details[line][1]),
                            'LineX2': int(ldict_line_details[line][2]),
                            'LineY2': int(ldict_line_details[line][3].split(";")[0]),
                            'WordX1': int(word_details[0]),
                            'WordY1': int(word_details[1]),
                            'WordX2': int(word_details[2]),
                            'WordY2': int(word_details[3].split(";")[0]),
                            'Word': word,
                            'WordConf': int(word_details[-1])}
                    llst_hocr_data.append(ldict_word)
                ldict_ocr_output["hocr"] = llst_hocr_data

        else:
            raise ValidationError("Provided pstr_input_img_path: " + pstr_input_img_path + " is not proper/ not exist")

        if not pbol_keep_output_file:
            if lstr_output_file_path_without_ext and os.path.exists(lstr_output_file_path_without_ext):
                shutil.rmtree(lstr_output_file_path_without_ext, ignore_errors=False, onerror=None)

    except Exception as e:

        logger.error("Input Parameter:"
                     + "\n\tpstr_input_img_path: " + str(pstr_input_img_path)
                     + "\n\tpstr_tesseract_command:" + str(pstr_tesseract_command)
                     + "\n\tpstr_model: " + pstr_model
                     + "\n\tpint_psm: " + str(pint_psm)
                     + "\n\tpint_oem: " + str(pint_oem)
                     + "\n\tpbol_keep_output_file: " + str(pbol_keep_output_file)
                     + "\n\tpbol_generate_tsv_output: " + str(pbol_generate_tsv_output)
                     + "\n\tpbol_generate_box_output: " + str(pbol_generate_box_output)
                     + "\n\tpbol_generate_text_output: " + str(pbol_generate_text_output)
                     + "\n\tpbol_generate_hocr_output: " + str(pbol_generate_hocr_output)
                     + "\n Error:" + str(e))
        raise

    finally:
        return ldict_ocr_output
