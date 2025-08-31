# textaur 
textaur takes an input document (plain text or pdf), extracts the text, prompts an LLM to lint/reformat/clean up, and saves the result.

It automagically turns this noisy OCR scan:
```
48

49
50
50a
ASL

51
AS2
52

REVISED 11/1/2017
-- 33-36.

David dives headfirst onto the small bed. He grabs the
pillow and hugs it tightly. A single tear runs down
his cheek.
DISSOLVE TO:
OMIT 43
OMIT 49
OMIT 50
OMIT SOA
EXT. HOTEL - MORNING ASL
David and Steve walk out of the hotel onto the sunny
street. David looks tired.
STEVE

It's not that big a city, David.

I'll bet there's an arcade at

every corner.
The boys look up the block then turn and look down
the other way.

STEVE
Let's try the next street.
cur To:

OMIT 51
OMIT AS2
```
into this properly formatted screenplay:
```
David dives headfirst onto the small bed. He grabs the pillow and hugs it tightly. A single tear runs down his cheek.

DISSOLVE TO:

EXT. HOTEL - MORNING

David and Steve walk out of the hotel onto the sunny street. David looks tired.

STEVE
It's not that big a city, David. I bet there's an arcade at every corner.

The boys look up the block then turn and look down the other way.

STEVE
Let's try the next street.

CUT TO:
```

The textaur pipeline was originally created to reformat messy text into proper (fountain) screenplay format but the same process (with a much simpler linting prompt) works for general text. Textaur also lets you use your own linting prompt if you have some special use case.


# Installation
```
pip install textaur 
```

## OpenAI API Key
textaur requires an OpenAI API key to use the LLM to lint text. (Text extraction will work without it.) Set the key in your environment:

```
OPENAI_API_KEY="very secret key"
```

## Optional Dependencies
If you want to use optical character recognition to extract text from pdfs, textaur requires binaries for ```tesseract``` and ```poppler``` to be installed on your system. These binaries are not included in textaur itself and you'll need to install them separately:

```
# macOS
brew install tesseract poppler

# Ubuntu/Debian
sudo apt install tesseract-ocr poppler-utils

# Windows
lol
```
OCR is noticeably slower than direct text extraction, but is usually necessary if you're starting with a scanned file. If you don't know whether you need to use OCR you can always try to extract the text without linting it using the ```--no-lint``` flag and then review that output manually to see if it's any good.

# Usage
To extract and lint general text from a pdf or text file:
```
textaur ./path/to/my.pdf
```
This will extract the text and save it to ```./path/to/my_extracted_text.txt``` and lint the text and save it to ```./path/to/my_linted_text.txt```. The extracted text will only be saved as a separate file if the input file is a pdf, not if it's plain text.

If it's a screenplay and you want to use OCR:
```
textaur ./path/to/my_scanned_screenplay.pdf --mode screenplay --ocr
```
## Options
- `-m, --mode <text|t|screenplay|sp>`: Type of input text (generic or screenplay). Generic by default/if omitted.
- `-o, --output <file>`: Save linted output to this file instead of default
- `--extracted-text <file>`: Save extracted unlinted text to this file instead of default
- `--ocr`: Use optical character recognition to extract text if it's a PDF (false by default; textaur will try to simply pull out the text if the input is a PDF)
- `--no-lint`: Extract and save text only, without AI linting
- `--prompt <file>`: File to use as custom AI linting prompt

## Additional Notes

- Input files must exist and be readable.
- Output and extracted text files will be created in the same directory as the input unless specified.


# TODO
- Support more LLMs
- More prompts for other kinds of text input/formatting
- Set of evals for existing and new prompts
- Config to set:
    - Default mode (text, screenplay, other text types)
    - Preferred LLM once supported
    - LLM API key
