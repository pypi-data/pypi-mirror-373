"""
String utilities for textaur.
"""
import re
from typing import Callable
from collections.abc import Iterable
from pathlib import Path

# arbitrary default number of maximum characters to lint at one time
# 10_000 is about 10 pages of screenplay, or less of scanned book text
MAX_CHUNK_CHAR_COUNT = 10_000

# If a line is converted to uppercase and starts with one of these keywords,
# assume it's a scene heading
SCENE_HEADING_KEYWORDS = [
    "INT.", 
    "INT ", 
    "INT/", 
    "EXT.", 
    "EXT ", 
    "EXT/", 
    "I/E",
    "I./E.", 
    "E/I", 
    "E./I.", 
    "EST.", 
    "EST ", 
    "EST/", 
    "ESTABLISHING", 
    "INTERIOR", 
    "EXTERIOR",
]

# If a line is converted to uppercase and starts with one of these keywords,
# assume it's a scene transition
SCENE_TRANSITION_KEYWORDS=[
    "CUT TO",
    "FADE TO",
    "FADE IN",
    "FADE OUT",
    "SMASH TO",
    "SMASH CUT TO",
    "WHIP PAN TO",
    "DISSOLVE TO",
]

# Fountain scene headings are a "." followed by any alphanumeric character
RE_FOUNTAIN_SCENE_HEADING = re.compile(r"^\.[a-zA-Z0-9]")

# A line that is just a 1-4 digit number with or without a trailing period looks
# like a page number
RE_PAGE_NUMBER = re.compile(r"^\s*(\d{1,4})\.?\s*$")

# A line that is just 1-10 lower case roman numerals with or without a trailing
# period looks like a page number
RE_ROMAN_NUMERAL_PAGE_NUMBER = re.compile(r"^\s*[ivxlc]{1,10}\.?\s*$")


class Strutil:
    """
    String utility class for handling textaur string operations.
    """
    def __init__(self, log: Callable = print):
        self.log = log


    def chunk_pages(
        self,
        pages: list[str],
        max_chunk_chars: int=MAX_CHUNK_CHAR_COUNT,
        join_str: str="\n\n",
    ) -> list[str]:
        """
        Takes a list of strings, concatenates them together, maintaining order
        and keeping each concatenated string no longer than max_chunk_chars
        long, and returns the new list.

        ["ab", "cd", "ef"], 4, "" -> ["abcd", "ef"]
        ["ab", "cd", "ef"], 3, "" -> ["ab", "cd", "ef"]
        ["abc", "d", "e", "f"], 2, "" -> ["abc", "de", "f"]

        :param pages
        List of strings to chunk together.

        :param max_chunk_chars
        Target max length of each string in returned array. Note that any 
        strings in the input array that are longer than this max will be kept in 
        order and returned as-is.

        :param join_str
        String to use to connect chunks. Does count towards number of charcters
        in each chunk. Default is "\\n\\n"
        """
        return self.chunk_strs_by_char_count(
            strs=pages,
            max_char_count=max_chunk_chars,
            join_str=join_str,
        )


    def chunk_screenplay_text(
        self,
        text: str,
        max_chunk_chars: int = MAX_CHUNK_CHAR_COUNT,
        join_str="\n\n",
    ) -> list[str]:
        """
        Takes screenplay text as an input string and returns a list of strings
        where each string will *NORMALLY* be no longer than max_chunk_chars. For
        unusual input (no parseable scene headings/transitions/page numbers) the
        algorithm will stop trying to create shorter strings, and the length of
        the strings in the output array may be longer than max_chunk_chars.

        :param text
        Screenplay as a string.

        :max_chunk_chars
        Target max number of characters in each string in return array.
        """

        # split screenplay into scenes - this will cover most cases
        chunks = self.split_by_scene_heading(text)

        # if any chunk is still too long (no scene headings, like a William
        # Goldman script or something) try to split by transitions
        chunks = [s for s in self.flatten([
            c if len(c) <= max_chunk_chars else self.split_by_scene_transition(c)
            for c in chunks
        ])]

        # if any chunk is still too long (no headings or transitions) try to
        # split by page number
        chunks = [s for s in self.flatten([
            c if len(c) <= max_chunk_chars else self.split_by_page_number(c)
            for c in chunks
        ])]

        # if any chunk is still too long at this point, give up
        return self.chunk_strs_by_char_count(
            strs=chunks,
            max_char_count=max_chunk_chars,
            join_str=join_str,
        )


    def chunk_generic_text(
        self,
        text: str,
        max_chunk_chars: int = MAX_CHUNK_CHAR_COUNT,
        join_str="\n\n",
    ) -> list[str]:
        """
        Takes generic text as an input string and returns a list of strings
        where each string will *NORMALLY* be no longer than max_chunk_chars. For
        unusual input (no parseable page numbers, no empty lines) the algorithm
        will stop trying to create shorter strings and the length of the strings
        in the output array may be longer than max_chunk_chars.

        :param text
        Generic text as a string.

        :max_chunk_chars
        Target max number of characters in each string in return array.
        """
        # try to split by page number
        chunks = self.split_by_page_number(text)

        # if any chunks are too long after page numbers, try blank lines
        # note that this is specifically splitting by emptyish lines, and there
        # are edge cases where the assumptions about what an emptyish line is
        # could be wrong... but at that point the text may require some manual
        # clean up.
        chunks = [s for s in self.flatten([
            c if len(c) <= max_chunk_chars else self.split_by_emptyish_lines(c)
            for c in chunks
        ])]

        # if any chunk is still too long at this point, give up
        return self.chunk_strs_by_char_count(
            strs=chunks,
            max_char_count=max_chunk_chars,
            join_str=join_str,
        )


    def chunk_strs_by_char_count(
        self,
        strs: list[str],
        max_char_count: int = MAX_CHUNK_CHAR_COUNT,
        join_str: str = "\n\n",
    ) -> list[str]:
        """
        Takes an array of strings and, maintaining order, concatenates them to
        make them as long as possible without going over the max_char_count. If
        a string in the input array is longer than the max_char_count it will be
        left as-is in order and included in the return array.

        ["ab", "cd", "ef"], 4, "" -> ["abcd", "ef"]
        ["ab", "cd", "ef"], 3, "" -> ["ab", "cd", "ef"]
        ["abc", "d", "e", "f"], 2, "" -> ["abc", "de", "f"]

        :param strs
        Array of strinsg to chunk together.

        :param max_char_count
        Target max characters per string in output array.

        :param join_str
        String to use to join strings together. "\\n\\n" by default.
        """
        res, buff, buff_chars = [], [], 0

        for s in strs:
            s_len = len(s)

            # if the string itself is longer than allowed
            if s_len > max_char_count:
                if buff:
                    res.append(join_str.join(buff))
                    buff, buff_chars = [], 0
                self.log(f"single string length ({s_len}) exceeds max_char_count ({max_char_count})")
                res.append(s)
                continue

            # if adding this string would overflow the buffer
            if buff_chars + (len(join_str) if buff else 0) + s_len > max_char_count:
                res.append(join_str.join(buff))
                buff, buff_chars = [], 0

            buff.append(s)
            buff_chars += s_len + (len(join_str) if buff_chars > 0 else 0)

        if buff:
            res.append(join_str.join(buff))

        return res


    def split_by_line_type(self, text: str, line_matcher: Callable)->list[str]:
        """
        Splits a string into an array of strings, where each string is a
        substring of the input string that is separated by one or more lines
        that match a given line matching function.

        Line matcher: lamda x: x == "br"
        Input: "line 1\\nline2\\nbr\\nline3\\nbr\\nline4"
        Returns: ["line 1\\nline2", "br\\nline3", "br\\nline4"]

        :param text
        Text as a string.

        :param line_matcher
        Function to match the first line of each substring.
        """
        buff = []
        lines = text.split("\n")
        start, end = 0, 1
        while end <= len(lines):
            # if it gets to the last line, add whatever the last chunk is
            if end == len(lines):
                buff.append("\n".join(lines[start:len(lines)]))
            # if the last line matches, add up to but not including that line
            elif line_matcher(lines[end]):
                buff.append("\n".join(lines[start:end]))
                start = end
            # in all cases (including both ifs above) increment end
            end += 1
        return buff


    def split_by_scene_heading(self, text: str) -> list[str]:
        """
        Splits a string into an array of strings, where each string is a
        substring of the input string that is separated by one or more scene
        headings.

        :param text
        The string to split.
        """
        return self.split_by_line_type(
            text=text,
            line_matcher=self.line_is_scene_heading,
        )


    def split_by_scene_transition(self, text: str) -> list[str]:
        """
        Splits a string into an array of strings, where each string is a
        substring of the input string that is separated by one or more scene
        transitions.

        :param text
        The string to split.
        """
        return self.split_by_line_type(
            text=text,
            line_matcher=self.line_is_transition,
        )


    def split_by_page_number(self, text: str) -> list[str]:
        """
        Splits a string into an array of strings, where each string is a
        substring of the input string that is separated by one or more page
        numbers.

        :param text
        The string to split.
        """
        return self.split_by_line_type(
            text=text,
            line_matcher=self.line_is_page_number,
        )


    def split_by_emptyish_lines(self, text: str) -> list[str]:
        """
        Splits a string into an array of strings, where each string is a
        substring of the input string that is separated by one or more emptyish
        lines.

        :param text
        The string to split.
        """
        return self.split_by_line_type(
            text=text,
            line_matcher=self.line_is_emptyish,
        )


    def line_is_scene_heading(self, line: str) -> bool:
        """
        Returns true if a string looks like a scene heading (ie, starts with a
        list of scene heading keywords). Works with fountain formatting where a
        leading period followed by an alphaneumeric character denotes a scene
        heading.

        :param line
        String to check.
        """
        l = line.lstrip().upper()
        # if the line matches the keywords, it's a scene heading
        for k in SCENE_HEADING_KEYWORDS:
            # fountain scene headings don't have to be all caps
            if l.startswith(k):
                return True

        # in fountain, a period immediately followed by any aphanumeric
        # character forces a scene heading (ie ".ext" or ".some scene" but
        # not "...some scene") assume a match is a scene heading
        return bool(RE_FOUNTAIN_SCENE_HEADING.match(l))


    def line_is_transition(self, line: str) -> bool:
        """
        Returns true if a string looks like a scene transition (ie, starts with 
        one of a list of scene transition keywords). Works for fountain where
        anything that ends with "TO:" is a transition.

        :param line
        String to check.
        """
        l = line.strip().upper()
        # if the line matches the keywords, it's a scene heading
        for k in SCENE_TRANSITION_KEYWORDS:
            # fountain scene headings don't have to be all caps
            if l.startswith(k):
                return True

        # in fountain, anything that ends with "TO:" is a transition
        return line.rstrip().upper().endswith(" TO:") # strip only right side


    def line_is_page_number(self, line: str) -> bool:
        """
        Returns true if a string looks like a page number.

        :param line
        String to check.
        """
        l = line.strip()
        return bool(RE_PAGE_NUMBER.match(l) or RE_ROMAN_NUMERAL_PAGE_NUMBER.match(l))


    def line_is_emptyish(self, line: str) -> bool:
        """
        Returns true if a line is empty, or empty-ish (one non-alphanumeric 
        character).

        OCR scans frequently hallucinate a single character. If it's not
        alphanumeric it's very likely this can be ignored. 
        
        :param line
        String to check.
        """
        l = line.strip()
        return l == "" or (len(l) == 1 and not l.isalnum())


    def subarrayify(self, arr: list, subarray_length: int) -> list[str]:
        """
        Takes an array and a subarray length and returns an array of arrays 
        where each subarray is of length subarray_length (the last one can be 
        shorter). For example: subarrayify([1, 2, 3, 4, 5], subarray_length=2) 
        would return [[1, 2], [3, 4], [5]]

        :param arr
        Array of items to turn into subarrays

        :param subarray_length 
        Length of each subarray. 
        """
        if subarray_length < 2:
            raise ValueError("Subarray length must be at least 2")
        return [arr[i:i+subarray_length] for i in range(0, len(arr), subarray_length)]


    def remove_consecutive_blank_lines(self, text: str) -> str:
        """
        Replace runs of two or more blank lines with a single blank line
        """
        lines = text.split("\n")
        res = []
        i = 0
        while i < len(lines):
            l = lines[i]
            # if the line isn't blank, just append it to result
            if not l.strip() == "":
                res.append(l)
                i += 1
            else:
                # if the line is blank but the next one isn't, append both
                if i < len(lines) - 1 and not lines[i+1].strip() == "":
                    res.append(l)
                    res.append(lines[i+1])
                    i += 2
                # if the line is blank and the next one is also blank, skip
                # the line to repeat this process for the next line
                else:
                    i += 1
        return "\n".join(res)

    def flatten(self, lst):
        """
        Flattens a nested list of lists into a single list.

        :param lst
        List to flatten.
        """
        for item in lst:
            if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                yield from self.flatten(item)
            else:
                yield item

    @staticmethod
    def write_file(path: Path, text: str) -> None:
        """
        Writes text to a file.

        :param path
        Path to write the file to.

        :param text
        Text to write to the file.
        """ 
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

