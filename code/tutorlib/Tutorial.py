
## A Python Tutorial System
## Copyright (C) 2009,2010  Peter Robinson <pjr@itee.uq.edu.au>
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
## 02110-1301, USA.

## The frame in which the problem description is rendered as HTML
## The possible HTML tags are
## h1, h2, h3, h4, h5, it, tt, b, br, p, pre, ul, li, img
## and span as long as <span style='color:c'> where c is red, blue or green

from tkinter import *
from html.parser import HTMLParser
import os
import tkinter.messagebox

FONTS_INFO = [('h1', 8, 'bold'),
              ('h2', 6, 'bold'),
              ('h3', 4, 'bold'),
              ('h4', 2, 'bold'),
              ('h5', 0, 'bold'),
              ('it', 0, 'normal'),
              ('b',  0, 'bold'),
              ('tt', 1, 'normal')]

HEADERS = ['h1', 'h2', 'h3', 'h4', 'h5']
INDENT = ['indent0', 'indent1', 'indent2', 'indent3', 'indent4', 'indent5']
COLOURS = ['red', 'green', 'blue']

INTRO_TEXT = """
<p>
<p>
<h3>Welcome to MyPyTutor %s</h3>

The Problems menu contains the
collection of problems to choose from.
"""

ONLINE_TEXT = """
<p>
Use the Online menu to interact with your online information.
</p>
"""


class Tutorial(Frame):
    def __init__(self, master, fontinfo, textlen):
        Frame.__init__(self, master)
        font_name = fontinfo[0]
        font_size = int(fontinfo[1])
        self.text = Text(self, height=textlen, wrap=WORD)
        #family = self.text.config('font')[3][0]
        self.text.config(state=DISABLED, font=(font_name,
                                               str(font_size),
                                               'normal', 'roman'))
        self.text.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text.yview)
        self.update_fonts(font_name, font_size)
        for i, tag in enumerate(INDENT):
            self.text.tag_config(tag, lmargin1=40*i, lmargin2=40*i+14)
        for tag in COLOURS:
            self.text.tag_config(tag, foreground=tag)
        self.parser = TutorialHTMLParser(self.text, self)
        self.tut_directory = None

    def splash(self, online, version):
        if online:
            self.add_text((INTRO_TEXT % version) + ONLINE_TEXT)
        else:
            self.add_text(INTRO_TEXT % version)

    def update_text_length(self, lines):
        self.text.config(height=lines)

    def update_fonts(self, font_name, font_size):
        for name, font_delta, weight in FONTS_INFO:
            if name == 'tt':
                self.text.tag_config(name,
                                     font=('courier',
                                           str(font_size+font_delta),
                                           'normal', 'roman'))
            elif name == 'it':
                self.text.tag_config(name,
                                     font=(font_name,
                                           str(font_size+font_delta),
                                           weight, 'italic'))
            else:
                self.text.tag_config(name,
                                     font=(font_name,
                                           str(font_size+font_delta),
                                           weight, 'roman'))
        self.text.config(font=(font_name,
                               str(font_size),
                               'normal', 'roman'))

    def set_directory(self, directory):
        self.tut_directory = directory

    def add_text(self, text):
        self.text.config(state=NORMAL)
        self.text.delete(1.0, END)
        self.text.insert(END, '\n')
        self.parser.reset()
        self.parser.feed(text)
        self.text.config(state=DISABLED)

    def show_hint(self, text):
        self.text.config(state=NORMAL)
        self.parser.reset()
        self.parser.feed(text)
        self.text.yview(MOVETO, 1)
        self.text.config(state=DISABLED)


class TutorialHTMLParser(HTMLParser):

    def __init__(self, textobj, parent=None):
        super().__init__(self)
        self.header = ''
        self.textobj = textobj
        self.indent = 0
        self.active_tags = []
        self.do_lstrip = False
        self.end_ul = False
        self.parent = parent

    def reset(self):
        self.indent = 0
        self.active_tags = []
        self.do_lstrip = False
        self.end_ul = False
        HTMLParser.reset(self)

    def handle_starttag(self, tag, attrs):
        self.do_lstrip = False
        if tag == 'span':
            if len(attrs) == 1 and len(attrs[0]) == 2 \
                    and attrs[0][0] == 'style':
                style = attrs[0][1].split(':')
                if len(style) == 2 and style[0].strip() == 'color':
                    self.active_tags.append(style[1].strip())
                else:
                    self.active_tags.append(tag)
            else:
                self.active_tags.append(tag)
        elif tag == 'br':
            self.do_lstrip = True
            self.textobj.insert(END, '\n')
        elif tag == 'p':
            self.do_lstrip = True
            self.textobj.insert(END, '\n\n')
        elif tag == 'img':
            img_file = attrs[0][1]
            self.img_obj = \
                PhotoImage(file=os.path.join(self.parent.tut_directory,
                                             img_file))
            img_label = Label(self.textobj, image=self.img_obj)
            self.textobj.window_create(END, window=img_label)
            self.active_tags.append(tag)
        else:
            if tag == 'ul':
                self.textobj.insert(END, '\n')
                self.indent += 1
                self.active_tags.append(tag)
            elif tag == 'li':
                self.active_tags.append(INDENT[self.indent])
                self.do_lstrip = True
                if not self.end_ul:
                    self.textobj.insert(END, '\n')
                self.textobj.insert(END, '* ', tuple(self.active_tags))
            else:
                self.active_tags.append(tag)
        self.end_ul = False

    def handle_endtag(self, tag):
        if tag == 'ul':
            self.textobj.insert(END, '\n\n')
            self.indent -= 1
            self.do_lstrip = True
            self.end_ul = True
        elif tag == 'li':
            self.do_lstrip = True
        elif tag == 'p':
            self.do_lstrip = True
            return
        elif tag in HEADERS:
            self.textobj.insert(END, '\n\n')
            self.do_lstrip = True
        self.active_tags.pop(-1)

    def _compress_data(self, data):
        data = data.replace('\n', ' ')
        if len(data) > 1:
            first = data[0]
            last = data[-1]
        elif data == ' ':
            first = ' '
            last = ' '
        else:
            first = ''
            last = ''
        data = ' '.join(data.split())
        if self.do_lstrip:
            self.do_lstrip = False
            if data and last == ' ':
                data = data + last
        else:
            if first == ' ':
                data = first+data
            if data != ' ' and last == ' ':
                data = data + last
        return data

    def handle_data(self, data):
        if self.active_tags:
            tag = self.active_tags[-1]
            if tag == 'ul':
                return
            if tag == 'pre':
                self.textobj.insert(END, data, ('tt',))
                return
            data = self._compress_data(data)
            for tag in self.active_tags:
                if 'indent' not in tag:
                    self.textobj.tag_raise(tag)
            self.textobj.insert(END, data, tuple(self.active_tags))
        else:
            data = self._compress_data(data)
            self.textobj.insert(END, data)


# Storing info about each tutorial

class TutorialInfo(object):
    class TutInfo(object):
        def __init__(self, name):
            self.name = name
            self.problems_info = {}
            self.problems_list = []
            self.menuobj = None

        def set_menuobj(self, menuobj):
            self.menuobj = menuobj

        def get_menuobj(self):
            return self.menuobj

        def add_problem(self, problem):
            name = problem.name
            self.problems_list.append(name)
            self.problems_info[name] = problem

        def set_problem_status(self, name, status):
            self.problems_info[name].set_status(status)

        def get_problem(self, name):
            return self.problems_info[name]

        def get_max_len(self):
            max_len = 0
            for key in self.problems_info:
                max_len = max(max_len, len(self.problems_info[key].name))
            return max_len

    class ProblemInfo(object):
        def __init__(self, name, tut):
            self.name = name
            self.tut = tut
            self.status = '-'

        def set_status(self, status):
            self.status = status

    def __init__(self, tut_dir):
        try:
            fullname = os.path.join(tut_dir, 'tutorials.txt')
            f = open(fullname, 'U')
        except:
            tkinter.messagebox.showerror('Tutorial Error',
                                         'Cannot open master file '+fullname)
            return None

        lines = [line.strip() for line in f]
        f.close()
        self.tut_list = []
        self.tut_dict = {}
        current_tut = ''
        for line in lines:
            if line:
                if line[0] == '[':
                    tut = line[1:-1]
                    tut_info = TutorialInfo.TutInfo(tut)
                    self.tut_list.append(tut)
                    self.tut_dict[tut] = tut_info
                    current_tut = tut
                else:
                    parts = line.split(':')
                    tut_info.add_problem(TutorialInfo.ProblemInfo(*parts))
        self.all_problems = [(t, p) for t in self.tut_list
                             for p in self.tut_dict[t].problems_list]

    def get_tutorial(self, name):
        return self.tut_dict[name]

    def get_tutorial_by_index(self, index):
        return self.get_tutorial(self.tut_list[index])

    def set_menu(self, tut_name, menuobj):
        self.tut_dict[tut_name].set_menuobj(menuobj)

    def get_menu(self, tut_name):
        return self.tut_dict[tut_name].get_menuobj()

    def get_problem(self, tut_name, problem_name):
        return self.tut_dict[tut_name].get_problem(problem_name)

    def set_problem_status(self, tut_name, problem_name, status):
        self.tut_dict[tut_name].set_problem_status(problem_name, status)

    def next_tutorial(self, tut_name, problem_name):
        if (tut_name, problem_name) == (None, None):
            # User hasn't opened a problem yet. Move to the first unsolved one.
            # If all are solved, move to the first one.
            for t, p in self.all_problems:
                if self.get_problem(t, p).status == '-':
                    return (t, p)
            return self.all_problems[0]

        index = self.all_problems.index((tut_name, problem_name))
        if index+1 < len(self.all_problems):
            return self.all_problems[index+1]
        return (tut_name, problem_name)

    def previous_tutorial(self, tut_name, problem_name):
        index = self.all_problems.index((tut_name, problem_name))
        if index > 0:
            return self.all_problems[index-1]
        return (tut_name, problem_name)

    def __str__(self):
        max_len = 0
        for key in self.tut_dict:
            max_len = max(max_len, self.tut_dict[key].get_max_len())

        string = ''
        for key in self.tut_list:
            tut = self.tut_dict[key]
            string += tut.name+'\n'
            for pkey in tut.problems_list:
                prob = tut.problems_info[pkey]
                name = prob.name
                spaces = max_len + 5 - len(name)
                string += '    ' + name + spaces*' ' + prob.status + '\n'
        return string
