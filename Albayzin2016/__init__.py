#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2017 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


import os.path as op
from pyannote.database import Database
from pyannote.database.protocol import SpeakerDiarizationProtocol
from pyannote.parser import MDTMParser

# this protocol defines a speaker diarization protocol: as such, a few methods
# needs to be defined: trn_iter, dev_iter, and tst_iter.



def read_rttm_file(file):
    # load whole file
    df = read_table(file,
    delim_whitespace=True,
    header=None, names=['type', 'uri', 'channel', 'start', 'duration', 'modality', 'confidence', 'label', 'gender'],
    keep_default_na=False, na_values=[])

    # remove comment lines
    # (i.e. lines for which all fields are either None or NaN)
    #keep = [not all(pandas.isnull(item) for item in row[3:4])
    #        for row in df.itertuples()]
    #df = df[keep]
    df = df.loc[~df['type'].str.contains('-INFO')]
    return df

class TVRadio(SpeakerDiarizationProtocol):
    """My first speaker diarization protocol """

    def __init__(self, preprocessors={}, **kwargs):
        super(TVRadio, self).__init__(
            preprocessors=preprocessors, **kwargs)

    def _subset(self, subset):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')

        # load annotations
        #path = op.join(data_dir, '{protocol}.{subset}.mdtm'.format(subset=subset, protocol=protocol))
        #rttms = self.rttm_parser_.read(path)

        path = op.join(data_dir, '{subset}.lst'.format(subset=subset))
        with open(path) as f:
            uris = f.readlines()
        uris = [x.strip() for x in uris]

        rttms = {}
        for file in listdir(op.join(data_dir, 'rttm',subset)):
            rttm = read_rttm_file(op.join(data_dir, 'rttm', subset, file))
            uri = rttm['uri'].iloc[0]
            annotation = Annotation()
            for index, row in rttm.iterrows():
                annotation[Segment(float(row['start']), float(row['start']) + float(row['duration']))] = row['label']
            rttms[uri] = annotation

        #By default it take all the file time
        path = op.join(data_dir, '{subset}.time'.format(subset=subset))
        with open(path) as f:
            rows = f.readlines()
        times = {}
        for row in rows:
            kv = row.split(' ')
            times[kv[0]] = Segment(0, float(kv[1]))

        for uri in uris:
            annotated = times[uri]
            annotation = rttms[uri]
            current_file = {
                'database': 'Albayzin2016',
                'uri': uri,
                'annotated': annotated,
                'annotation': annotation}
            yield current_file

    def trn_iter(self):
        return self._subset('trn')

    def dev_iter(self):
        return self._subset('dev')

    def tst_iter(self):
        return self._subset('tst')

            # optionally, an 'annotated' field can be added, whose value is
            # a pyannote.core.Timeline instance containing the set of regions
            # that were actually annotated (e.g. some files might only be
            # partially annotated).

            # this field can be used later to only evaluate those regions,
            # for instance. whenever possible, please provide the 'annotated'
            # field even if it trivially contains segment [0, file_duration].

# this is where we define each protocol for this database.
# without this, `pyannote.database.get_protocol` won't be able to find them...

class Albayzin2016(Database):
    """MyDatabase database"""

    def __init__(self, preprocessors={}, **kwargs):
        super(Albayzin2016, self).__init__(preprocessors=preprocessors, **kwargs)

        # register the first protocol: it will be known as
        # MyDatabase.SpeakerDiarization.MyFirstProtocol
        self.register_protocol(
            'SpeakerDiarization', 'TVRadio', TVRadio)
