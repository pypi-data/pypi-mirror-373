import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from textaur.core.strutil import Strutil

class TestChunkStrsByCharCount:
    """
    chunk_pages, chunk_screenplay_text, chunk_generic_text are all just wrappers
    around this function.
    """
    strutil = Strutil()

    def test_simple_input(self):
        strs = ["ab", "cd", "ef"]
        # max chars = to account for default join_str of "\n\n"
        chunks = self.strutil.chunk_strs_by_char_count(strs, max_char_count=6)
        assert chunks == ["ab\n\ncd", "ef"]


    def test_with_join_str(self):
        strs = ["ab", "cd", "ef"]
        chunks = self.strutil.chunk_strs_by_char_count(strs, max_char_count=4, join_str="")
        assert chunks == ["abcd", "ef"]
    

    def test_small_max(self):
        strs = ["ab", "cd", "ef"]
        chunks = self.strutil.chunk_strs_by_char_count(strs, max_char_count=1, join_str="")
        assert chunks == ["ab", "cd", "ef"]


    def test_mid_max(self):
        strs = ["ab", "cd", "ef"]
        chunks = self.strutil.chunk_strs_by_char_count(strs, max_char_count=3, join_str="")
        assert chunks == ["ab", "cd", "ef"]


    def test_mid_max_2(self):
        strs = ["abz", "cd", "ef"]
        chunks = self.strutil.chunk_strs_by_char_count(strs, max_char_count=3, join_str="")
        assert chunks == ["abz", "cd", "ef"]


    def test_big_max(self):
        strs = ["ab", "cd", "ef"]
        chunks = self.strutil.chunk_strs_by_char_count(strs, max_char_count=100, join_str="")
        assert chunks == ["abcdef"]


    def test_mid_max_2(self):
        strs = ["abz", "cd", "ef"]
        chunks = self.strutil.chunk_strs_by_char_count(strs, max_char_count=4, join_str="")
        assert chunks == ["abz", "cdef"]


class TestChunkScreenplayText:
    strutil = Strutil()
    scene_heading_input = f"""INT. LOCATION - DAY
My big scene.
EXT. OTHER LOCATION - NIGHT
Something happens.
LARRY
Oh no."""
    scene_heading_output = [
        f"""INT. LOCATION - DAY
My big scene.""",
        f"""EXT. OTHER LOCATION - NIGHT
Something happens.
LARRY
Oh no.""",
        ]
    scene_transition_input = f"""FADE IN:
WILLIAM GOLDMAN
I write without scene headings.
CUT TO:
VIZZINI
Inconceivable!"""
    scene_transition_output = [
        f"""FADE IN:
WILLIAM GOLDMAN
I write without scene headings.""",
        f"""CUT TO:
VIZZINI
Inconceivable!"""
    ]
    mixed_input = f"""Picking up at the end of some scene.
Something more happens.
2.
Now we're on page 2.
INT. NEW SCENE - CONTINUOUS
That was a scene heading. This is a new scene.
CUT TO:
Something exciting."""
    mixed_output = [
        f"""Picking up at the end of some scene.
Something more happens."""
f"""2.
Now we're on page 2."""
f"""INT. NEW SCENE - CONTINUOUS
That was a scene heading. This is a new scene.""",
f"""CUT TO:
Something exciting."""
    ]

    def test_with_normal_scene_headings(self):
        res = self.strutil.chunk_screenplay_text(self.scene_heading_input, max_chunk_chars=10)
        assert res == self.scene_heading_output


    def test_with_scene_transitions(self):
        res = self.strutil.chunk_screenplay_text(self.scene_transition_input, max_chunk_chars=10)
        assert res == self.scene_transition_output


    def text_wth_mixed_output(self):
        res = self.strutil.chunk_screenplay_text(self.mixed_input, max_chunk_chars=10)
        assert res == self.mixed_output


class TestChunkGenericText:
    strutil = Strutil()
    page_numbered_input = f"""End of some previous page.
37
Now the contents of page 37.
38.
Should catch page numbers with or without a period."""
    page_numbered_output = [
        f"""End of some previous page.""",
        f"""37
Now the contents of page 37.""",
        f"""38.
Should catch page numbers with or without a period."""
    ]
    mixed_input = f"""End of some previous page.
37
Now the contents of page 37.

Instead of a page break, an empty line."""
    mixed_output = [
        f"""End of some previous page.""",
        f"""37
Now the contents of page 37.""",
        f"""
Instead of a page break, an empty line."""
    ]

    def test_with_page_numbered_input(self):
        res = self.strutil.chunk_generic_text(self.page_numbered_input, max_chunk_chars=10)
        assert res == self.page_numbered_output

    def test_with_mixed_input(self):
        res = self.strutil.chunk_generic_text(self.mixed_input, max_chunk_chars=10)
        assert res == self.mixed_output


class TestSplitByLineType:
    strutil = Strutil()
    input = f"""1
marker
2
marker
3
marker
marker"""
    output = [
        "1",
        "marker\n2",
        "marker\n3",
        "marker",
        "marker"
    ]

    def test_splits_lines(self):
        res = self.strutil.split_by_line_type(text=self.input, line_matcher=lambda x: x == "marker")
        assert res == self.output


class TestLineIsSceneHeading:
    strutil = Strutil()

    should_match = [
        # realistic ones
        "INT. SCENE HEADING - DAY",
        "int. scene heading - day",
        "INT SCENE HEADING - DAY",
        "int scene heading - day",
        "INT/EXT SCENE HEADING - DAY",
        "int/ext scene heading - day",
        "EXT. SCENE HEADING - DAY",
        "ext. scene heading - day",
        "EXT SCENE HEADING - DAY",
        "ext scene heading - day",
        "EXT/ SCENE HEADING - DAY",
        "ext/ scene heading - day",
        "EXT/INT SCENE HEADING - DAY",
        "ext/int scene heading - day",
        "E/I SCENE HEADING - DAY",
        "e/i scene heading - day",
        "I/E SCENE HEADING - DAY",
        "i/e scene heading - day",
        "E./I. SCENE HEADING - DAY",
        "e./i. scene heading - day",
        "I./E. SCENE HEADING - DAY",
        "i./e. scene heading - day",
        "EST. SCENE HEADING - DAY",
        "est. scene heading - day",
        "EST SCENE HEADING - DAY",
        "est scene heading - day",
        "EST/ SCENE HEADING - DAY",
        "est/ scene heading - day",
        "ESTABLISHING SOMETHING",
        "establishing something",
        "INTERIOR SOMETHING",
        "interior something",
        "EXTERIOR SOMETHING",
        "exterior something",
        " iNt ",
        " Int ",
        " exT ",
        " Ext ",
        " esT ",
        " Est ",
        # in fountain "." followed by alphanumeric char forces scene heading
        " .fountain scene heading",
        " .1 other fountain scene heading",
    ]

    should_not_match = [
        "INTIMATE MOMENT - something something",
        "EXTERNAL something something",
        "intimidating description",
        "exterminator assassin from the future",
        ".",
        ". ",
        "...",
        "./",
        "aslkdfjas",
        "   ",
        "",
    ]

    def test_matches_should_match(self):
        for sh in self.should_match:
            assert self.strutil.line_is_scene_heading(sh) == True


    def test_matches_should_not_match(self):
        for sh in self.should_not_match:
            assert self.strutil.line_is_scene_heading(sh) == False


class TestLineIsTransition:
    strutil = Strutil()

    should_match = [
        "CUT TO",
        "cut to",
        " CuT tO: "
        "FADE TO",
        " fade to: ",
        "FADE IN",
        "fAdE in :",
        "FADE OUT",
        "  fade out "
        "DISSOLVE TO",
        "smash to",
        "   dissolve to: ",
        " TO:",
        " in fountain anything that ends with to: ",
    ]

    should_not_match = [
        "aslkdfja;sldkfjasdklfj",
        "TO",
        " TO ",
        "to",
        " to ",
        "TO :", # space before colon
        "  ",
        "",
    ]

    def test_should_match(self):
        for st in self.should_match:
            assert self.strutil.line_is_transition(st) == True


    def test_should_not_match(self):
        for st in self.should_not_match:
            assert self.strutil.line_is_transition(st) == False


class TestLineIsPageNumber:
    strutil = Strutil()

    should_match = [
        "1",
        "01", # leading zeroes are allowed even though that might be dumb
        "10",
        " 123. ",
        "  9999  ",
        "0000.",
        " i ",
        "ii",
        "iviviviviv.",
        "  ivxlcvxcl  ",
        "   v.   ",
    ]

    should_not_match = [
        "",
        "   ",
        "12345",
        "12345.",
        "1,231",
        "1,231.",
        "1)",
        "10..",
        "i..",
        "..v",
        "ivixclcvlvixixixix",
    ]

    def test_should_match(self):
        for pn in self.should_match:
            assert self.strutil.line_is_page_number(pn) == True


    def test_should_not_match(self):
        for pn in self.should_not_match:
            assert self.strutil.line_is_page_number(pn) == False


class TestLineIsEmptyish:
    strutil = Strutil()

    should_match = [
        "",
        "\n",
        "\t",
        " ",
        "      ",
        ".",
        "  ,  ",
        "    ;    ",
    ]

    should_not_match = [
        "    a      ",
        "1",
        "0",
    ]

    def test_should_match(self):
        for el in self.should_match:
            assert self.strutil.line_is_emptyish(el) == True


    def test_should_not_match(self):
        for el in self.should_not_match:
            assert self.strutil.line_is_emptyish(el) == False


class TestRemoveConsecutiveBlankLines:
    strutil = Strutil()

    input = "\n\n\n1\n\n\n2\n\n\n3\n\n\n"
    output = "\n1\n\n2\n\n3"
    
    def test_in_out(self):
        assert self.strutil.remove_consecutive_blank_lines(self.input) == self.output


class TestFlatten:
    strutil = Strutil()
    input = [1, [2, [3, [4, [5, [6, 7]]]]]]
    output = [1, 2, 3, 4, 5, 6, 7]

    def test_in_out(self):
        res = self.strutil.flatten(self.input)
        for idx, itm in enumerate(res):
            assert self.output[idx] == itm

