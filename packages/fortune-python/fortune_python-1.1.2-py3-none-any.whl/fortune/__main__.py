# Copyright 2025 fortune-python contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from . import fortune as _fortune

"""
fortune [-acefilsw] [-n length] [ -m pattern] [[n%] file/dir/all]
Description

When fortune is run with no arguments it prints out a random epigram. Epigrams are divided into several categories.

Options

The options are as follows:
-a

Choose from all lists of maxims.

-c

Show the cookie file from which the fortune came.

-e

Consider all fortune files to be of equal size (see discussion below on multiple files).

-f

Print out the list of files which would be searched, but don't print a fortune.

-l

Long dictums only. See -n on how ''long'' is defined in this sense.
-m pattern
    Print out all fortunes which match the basic regular expression pattern. The syntax of these expressions depends on how your system defines re_comp(3) or regcomp(3), but it should nevertheless be similar to the syntax used in grep(1). 
    The fortunes are output to standard output, while the names of the file from which each fortune comes are printed to standard error. Either or both can be redirected; if standard output is redirected to a file, the result is a valid fortunes database file. If standard error is also redirected to this file, the result is still valid, but there will be ''bogus'' fortunes, i.e. the filenames themselves, in parentheses. This can be useful if you wish to remove the gathered matches from their original files, since each filename-record will precede the records from the file it names. 
-n length
    Set the longest fortune length (in characters) considered to be ''short'' (the default is 160). All fortunes longer than this are considered ''long''. Be careful! If you set the length too short and ask for short fortunes, or too long and ask for long ones, fortune goes into a never-ending thrash loop. 
-s

Short apothegms only. See -n on which fortunes are considered ''short''.

-i

Ignore case for -m patterns.

-w

Wait before termination for an amount of time calculated from the number of characters in the message. This is useful if it is executed as part of the logout procedure to guarantee that the message can be read before the screen is cleared.
The user may specify alternate sayings. You can specify a specific file, a directory which contains one or more files, or the special word all which says to use all the standard databases. Any of these may be preceded by a percentage, which is a number n between 0 and 100 inclusive, followed by a %. If it is, there will be a n percent probability that an adage will be picked from that file or directory. If the percentages do not sum to 100, and there are specifications without percentages, the remaining percent will apply to those files and/or directories, in which case the probability of selecting from one of them will be based on their relative sizes.

As an example, given two databases funny and not-funny, with funny twice as big (in number of fortunes, not raw file size), saying
    fortune funny not-funny 
will get you fortunes out of funny two-thirds of the time. The command
    fortune 90% funny 10% not-funny 
will pick out 90% of its fortunes from funny (the ''10% not-funny'' is unnecessary, since 10% is all that's left).

The -e option says to consider all files equal; thus
    fortune -e funny not-funny 
is equivalent to
    fortune 50% funny 50% not-funny 
"""


def fortune():
    print(_fortune())
