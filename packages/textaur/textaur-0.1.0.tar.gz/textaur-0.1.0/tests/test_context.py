import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from textaur.core.context import (
    Context,
    Mode,
    DEFAULT_MODE,
    DEFAULT_LINTED_SUFFIX,
    DEFAULT_EXTRACTED_SUFFIX,
    mode_string_to_enum_map,
)
from unittest.mock import patch

def ret_true():
    return True

def ret_false():
    return False

def dummy_log(msg):
    pass

def dummy_progress(msg):
    pass

def test_context_valid(tmp_path):
    input_fn = "input"
    input_ext = ".txt"
    input_file = tmp_path / f"{input_fn}{input_ext}"
    context = Context(
        input_file=str(input_file),
        output_path=None,
        extracted_text_path=None,
        use_ocr=None,
        no_lint=None,
        mode=None,
        custom_prompt_path=None,
        progress_fn=dummy_progress,
        log=dummy_log,
        confirm=lambda x: True,
    )
    assert context.is_valid_context() == True
    assert context.log == dummy_log
    assert context.progress_fn == dummy_progress
    assert context.input_file == Path(input_file)
    output_file = context.output_file
    assert isinstance(output_file, Path) == True
    assert output_file.name.endswith(f"{input_fn}{DEFAULT_LINTED_SUFFIX}")
    extracted_file = context.extracted_text_file
    assert isinstance(extracted_file, Path)
    assert extracted_file.name.endswith(f"{input_fn}{DEFAULT_EXTRACTED_SUFFIX}")
    assert context.use_ocr == False
    assert context.mode == DEFAULT_MODE
    prompt_text = context.prompt_text
    assert isinstance(prompt_text, str)
    assert prompt_text.strip() != ""


def test_context_invalid(tmp_path):
    with patch.object(Path, "is_file", return_value=True):
        input_fn = "input"
        input_ext = ".txt"
        input_file = tmp_path / f"{input_fn}{input_ext}"
        context = Context(
            input_file=str(input_file),
            output_path=None,
            extracted_text_path=None,
            use_ocr=None,
            no_lint=None,
            mode=None,
            custom_prompt_path=None,
            progress_fn=dummy_progress,
            log=dummy_log,
            confirm=lambda x: False,
        )
        # because confirm is ret_false, 
        assert context.is_valid_context() == False
        assert context.output_file == None
        assert context.extracted_text_file == None


def test_with_options(tmp_path):
    input_fn = "input"
    input_ext = ".txt"
    input_file = tmp_path / f"{input_fn}{input_ext}"
    linted_path = "linted.txt"
    extracted_path = "extracted.txt"
    provided_mode = "sp"
    context = Context(
        input_file=str(input_file),
        output_path=linted_path,
        extracted_text_path=extracted_path,
        use_ocr=True,
        no_lint=True,
        mode=provided_mode,
        custom_prompt_path=None,
        progress_fn=dummy_progress,
        log=dummy_log,
        confirm=lambda x: True,
    )
    assert context.is_valid_context() == True
    assert context.log == dummy_log
    assert context.progress_fn == dummy_progress
    assert context.input_file == Path(input_file)
    output_file = context.output_file
    assert isinstance(output_file, Path) == True
    assert output_file.name.endswith(linted_path)
    extracted_file = context.extracted_text_file
    assert isinstance(extracted_file, Path)
    assert extracted_file.name.endswith(extracted_path)
    assert context.use_ocr == True
    assert context.mode == mode_string_to_enum_map[provided_mode] 
    # because no lint is True, the mode that's set will be ignored and the
    # prompt text will be an empty string
    prompt_text = context.prompt_text
    assert isinstance(prompt_text, str)
    assert prompt_text.strip() == ""
