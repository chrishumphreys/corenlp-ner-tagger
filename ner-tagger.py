#!/bin/python

# A simple curses console app to label each word for CoreNLP NER
# Use to preparing tok files for training CoreNLP NER classifier.
# Assumes input has been pre-processed to one token per line
# Currently accepts labelling as ORGANISATION, PERSON or defaults to O

__author__ = "Chris Humphreys"
__version__ = "1.0.0"
__license__ = "GPL3"

import argparse
import curses
from curses import wrapper

class TokEntry:
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.label = 'O'

    def label_person(self):
        self.label = 'PERSON'

    def label_organisation(self):
        self.label = 'ORGANISATION'

    def label_other(self):
        self.label = 'O'

    def padded_label(self):
        return f" {self.label.ljust(20)}"

class Editor:

    def __init__(self, tok_lines : list, stdscr):
        super().__init__()
        self.screen_line = 0
        self.screen_offset = 0
        self.tok_lines = tok_lines
        screen_rows, screen_cols = stdscr.getmaxyx()
        self.title_window = stdscr.subwin(3, screen_cols, 0, 0)
        self.editor_window = stdscr.subwin(screen_rows-6, screen_cols, 3, 0)
        self.msg_window = stdscr.subwin(3, screen_cols, screen_rows-3, 0)
        self.msg_window.box()
        self.rows, self.cols = self.editor_window.getmaxyx()
        self.title_window.addstr(1,1, f"Press 'o' for ORGANISATION, 'p' for PERSON, 'backspace' for Other, 'w' to write and exit, 'q' to quit...")
        self.title_window.border()
        self.editor_window.move(0,0)
        #self.editor_window.refresh()
        self.editor_window.scrollok(True)

    def next_line(self):
        cursor_y, cursor_x = self.editor_window.getyx()
        if cursor_y < self.rows-1:
            new_y = cursor_y+1
            self.editor_window.move(new_y, 0)
        else:
            if self.screen_offset < len(self.tok_lines) - self.rows:
                self.screen_offset +=1
                self.editor_window.scroll()
                self.editor_window.addstr(self.get_text_for_cursor())
                self.editor_window.move(cursor_y, 0)
        self.display_progress()

    def display_progress(self):
        cursor_y, cursor_x = self.editor_window.getyx()
        start_ofset = self.screen_offset
        end_offset = self.rows-1 + self.screen_offset
        percent = (end_offset / (len(self.tok_lines)-1)) * 100
        self.msg("{:.0f}% (lines {}-{})                       ".format(percent, start_ofset+1, end_offset+1))

    def previous_line(self):
        cursor_y, cursor_x = self.editor_window.getyx()
        if cursor_y > 0:
            new_y = cursor_y-1
            self.editor_window.move(new_y, cursor_x)        
        elif self.screen_offset > 0:
            self.screen_offset -= 1
            self.editor_window.insertln()
            self.editor_window.move(cursor_y, 0)
            self.editor_window.addstr(self.get_text_for_cursor())
            self.editor_window.move(cursor_y, 0)
        self.display_progress()

    def current_data_offset(self):
        cursor_y, cursor_x = self.editor_window.getyx()
        return cursor_y + self.screen_offset

    def get_text_for_cursor(self):
        data_line = self.current_data_offset()
        return "{} {}".format(self.tok_lines[data_line].padded_label(), self.tok_lines[data_line].text.strip())

    def display_page(self):
        self.editor_window.move(0,0)
        cursor_y, cursor_x = self.editor_window.getyx()
        
        for y in range(0, self.rows+1):
            data_line = y + self.screen_offset
            text = self.get_text_for_cursor()
            self.editor_window.addstr(text)
            if y < self.rows:
                self.editor_window.move(y,0)
        self.editor_window.move(0,0)
        self.display_progress()

    def refresh(self):
        self.editor_window.refresh()

    def msg(self, msg : str):
        self.msg_window.addstr(1,1, msg)
        self.msg_window.refresh()

    def current_tok_entry(self):
        return self.tok_lines[self.current_data_offset()]

    def redraw_current_line(self):
        self.editor_window.addstr(self.get_text_for_cursor())
        cursor_y, cursor_x = self.editor_window.getyx()
        self.editor_window.move(cursor_y, 0)

def read_input_file(input_file):
    with open(input_file, newline='\n') as in_file:
        all_lines = in_file.readlines()
    return [TokEntry(x.strip()) for x in all_lines]

def write_output_file(tok_lines):
    with open(output_file, 'w') as out_file:
        for line in tok_lines:
            out_file.write(line.text.strip())
            out_file.write('\t')
            out_file.write(line.label)
            out_file.write('\n')
    
def main(stdscr, tok_entries, output_file):
    screen_rows, screen_cols = stdscr.getmaxyx()
    finished = False
    editor = Editor(tok_entries, stdscr)
    editor.display_page()
    write = False

    while not finished:
        c = stdscr.getch()
        if c:
            if c == ord('o'):
                editor.current_tok_entry().label_organisation()
                editor.redraw_current_line()
                editor.next_line()
            elif c == ord('p'):
                editor.current_tok_entry().label_person()
                editor.redraw_current_line()
                editor.next_line()
            elif c == curses.KEY_BACKSPACE:
                editor.current_tok_entry().label_other()
                editor.redraw_current_line()
                editor.next_line()
            elif c == curses.KEY_UP:
                editor.previous_line()
            elif c == curses.KEY_DOWN:
                editor.next_line()  
            elif c == ord('q'):
                write = False
                finished = True
            elif c == ord('w'):
                write = True
                finished = True
            editor.refresh()

    if write:
        write_output_file(editor.tok_lines)            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Console app to label tok training file')
    parser.add_argument('input', metavar='input', type=str, help='input tok file')
    parser.add_argument('output', metavar='output', type=str, help='output tok file')
    parser.add_argument('--verbose', action="store_true", help='be verbose')
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output
    verbose=False
    if args.verbose:
        verbose = True

    tok_entries = read_input_file(input_file)
    wrapper(main, tok_entries, output_file)