from openpecha.utils import (
    adjust_segment_num_for_chapter,
    chunk_strings,
    get_chapter_for_segment,
    parse_alignment_index,
)


def test_parse_root_mapping():
    input = "1"
    assert parse_alignment_index(input) == [1]

    input = "1,2,3,4"
    assert parse_alignment_index(input) == [1, 2, 3, 4]

    input = "1-4"
    assert parse_alignment_index(input) == [1, 2, 3, 4]

    input = "1-4,5-8"
    assert parse_alignment_index(input) == [1, 2, 3, 4, 5, 6, 7, 8]


def test_chunk_strings():
    # Less than chunk_size
    strings = ["1", "2", "3", "4", "5"]
    chunk_size = 10
    expected = [["1", "2", "3", "4", "5"]]
    assert chunk_strings(strings, chunk_size) == expected

    # More than chunk_size
    strings = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    chunk_size = 3
    expected = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["10"]]
    assert chunk_strings(strings, chunk_size) == expected

    # Equal to chunk_size
    strings = ["1", "2", "3", "4", "5"]
    chunk_size = 5
    expected = [["1", "2", "3", "4", "5"]]
    assert chunk_strings(strings, chunk_size) == expected

    # Empty list
    strings = []
    chunk_size = 5
    expected = []
    assert chunk_strings(strings, chunk_size) == expected

    # Evenly divisible
    strings = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    chunk_size = 2
    expected = [["1", "2"], ["3", "4"], ["5", "6"], ["7", "8"], ["9", "10"]]
    assert chunk_strings(strings, chunk_size) == expected


def test_get_chapter_num_from_segment_num():
    segment_num = 1
    no_of_chapter_segment = 100
    assert get_chapter_for_segment(segment_num, no_of_chapter_segment) == 1

    segment_num = 100
    no_of_chapter_segment = 100
    assert get_chapter_for_segment(segment_num, no_of_chapter_segment) == 1

    segment_num = 101
    no_of_chapter_segment = 100
    assert get_chapter_for_segment(segment_num, no_of_chapter_segment) == 2

    segment_num = 200
    no_of_chapter_segment = 100
    assert get_chapter_for_segment(segment_num, no_of_chapter_segment) == 2

    segment_num = 893
    no_of_chapter_segment = 100
    assert get_chapter_for_segment(segment_num, no_of_chapter_segment) == 9


def test_process_segment_num_for_chapter():
    segment_num = 1
    no_of_chapter_segment = 100
    assert adjust_segment_num_for_chapter(segment_num, no_of_chapter_segment) == 1

    segment_num = 100
    no_of_chapter_segment = 100
    assert adjust_segment_num_for_chapter(segment_num, no_of_chapter_segment) == 100

    segment_num = 101
    no_of_chapter_segment = 100
    assert adjust_segment_num_for_chapter(segment_num, no_of_chapter_segment) == 1

    segment_num = 200
    no_of_chapter_segment = 100
    assert adjust_segment_num_for_chapter(segment_num, no_of_chapter_segment) == 100

    segment_num = 893
    no_of_chapter_segment = 100
    assert adjust_segment_num_for_chapter(segment_num, no_of_chapter_segment) == 93
