#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
#
#  Copyright 2018 Bruce Schubert <bruce@emxsys.com>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

def format_phone_no(number, config):
    '''
    Returns a formatted the phone number based on the PHONE_DISPLAY_FORMAT configuration setting.
    '''
    template = config.get("PHONE_DISPLAY_FORMAT")
    separator = config.get("PHONE_DISPLAY_SEPARATOR")
    if separator == "" or template == "":
        return number

    # Get the template and split into reverse ordered parts for processing
    tmpl_parts = template.split(separator)
    tmpl_parts.reverse()

    # Piece together the phone no from right to left to handle variable len numbers
    number_len = len(number)
    end = number_len
    total_digits = 0
    phone_parts = []
    for tmpl in tmpl_parts:
        # Assemble parts from right to left
        start = max(0, end - len(tmpl))
        digits = number[start: end]
        phone_parts.insert(0, digits)
        # Prepare for next part
        end = start
        total_digits += len(digits)
        # if number is shorter than template then exit loop
        if start == 0:
            break
    # If number is longer then template, then capture remaining digits
    if total_digits < number_len:
        # Prepend remaining digits to parts
        phone_parts.insert(0, number[0: number_len - total_digits])
    # Return the formatted number
    return separator.join(phone_parts)


def query_db(db, query, args=(), one=False):
    """Executes the given query on the supplied db and returns the result(s)."""
    cur = db.execute(query, args)
    results = cur.fetchall()
    cur.close()
    return (results[0] if results else None) if one else results
