# tesseract_ocr

Tesseract is an optical character recognition engine for various operating systems.It is free software, released under
the Apache License.Originally developed by Hewlett-Packard as proprietary software in the 1980s, it was released as open
source in 2005 and development has been sponsored by Google since 2006.

Here is a simple utility to perform OCR on image documents using Tesseract OCR and extract text from them in formats
offered by Tesseract(txt,box,hocr,tsv)

# Implementation

Run main file either on terminal or your preferred ide. The script accepts following arguments from the user in the form
of command line arguments

* --input  (Input Image File Path, always required)
* --psm    (Page Segmentation Method", default=1)
* --oem    (Engine Type, type=int, default=1)
* --output_format  (list possible output formats needed, can take on multiple values, default=['txt'])
* --char_wise_extraction (Set True for Character Level Extraction, type=bool)

On Terminal, activate virtual env and run :

- for simple text output python3 main.py --input /home/workarea/Gaurav/projects/temp/inputs/image1.png --psm 1 --oem 1
  --output_format txt

- for multiple outformats python3 main.py --input /home/workarea/Gaurav/Projects/temp/inputs/image1.png --psm 1 --oem 1
  --output_format hocr txt tsv box

# Prerequisites

- python 3.6+
- Linux 18.04
- python libraries (can be installed from requirement.txt inside reference material)
- Leptonica (refer installation guide doc Tesseract_Leptonica_InstallationGuide.txt)
- Tesseract (refer installation guide doc Tesseract_Leptonica_InstallationGuide.txt)

# File Structure

```
├── tesseract_ocr
|   ├── main.py
|   ├── tesseract.py
|   ├── data
|   |   └── config.ini
|   ├── core
|   |   └── configuration.py
|   |   └── __init__.py
|   ├── exceptions
|   |   └── exceptions.py
|   |   └── logger.py
|   |   └── __init__.py
|   ├── reference_material
|   |   └── requirement.txt
|   |   └── Tesseract_Leptonica_InstallationGuide.txt
|   |   └── sample_input
|   |   └── sample_outputs
├── README.md
├── MANIFEST.in
└── setup.py
```

- Tesseract offers good extractions on good quality of input documents. In case of poor quality documents, we can make
  use of Character Level Confidence of extractions in identiying error in extraction (advisable to perform extractions
  in HOCR format to get char level extractions with confidence scores)

- To have a further in depth understanding of the workings of Tesseract, please refer
  https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/33418.pdf




