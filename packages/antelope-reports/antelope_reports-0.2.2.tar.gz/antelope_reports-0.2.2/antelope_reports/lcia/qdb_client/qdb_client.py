"""
A Qdb interface provider, implemented for now as a google sheet
"""

from xlstools.google_sheet_reader import GoogleSheetReader
from antelope import BaseEntity


INDEX_HEADINGS = ('external_ref', 'Name', 'ShortName', 'Method', 'Category', 'Indicator', 'unit', 'Comment', 'Notes')
FACTOR_HEADINGS = ('flowable', 'context', 'ref_quantity', 'ref_unit', 'locale', 'value')


class QdbQuantity(BaseEntity):
    is_entity = True
    entity_type = 'quantity'

    def __init__(self, origin, external_ref, unit, **kwargs):
        self._origin = origin
        self._external_ref = external_ref
        self._unit = unit
        self._args = kwargs

    @property
    def origin(self):
        """
        Must return a resolvable unique ID, nominally 'origin/external_ref'
        :return:
        """
        return self._origin

    @property
    def external_ref(self):
        return self._external_ref

    @property
    def reference_entity(self):
        """
        Must have a .unit property that returns a string,
        should have .entity_type property that returns 'quantity'
        :return:
        """
        return self._unit

    def properties(self):
        for k in sorted(self._args.keys()):
            yield k

    def get(self, item):
        return self._args.get(item)

    def make_ref(self, query):
        """
        if is_entity is true, entity must return a ref made from the provided query
        :param query:
        :return:
        """
        return NotImplemented


class QdbGSheetClient(object):
    def __init__(self, source, ref, json_credential=None, credential_file=None, **kwargs):
        self._source = source
        self._ref = ref
        cred = json_credential or credential_file
        self._xls = GoogleSheetReader(cred, source)
        self._args = kwargs
        self._qsheet = None
        self._qs = []
        self._qd = dict()
        self.load_all()

    @property
    def static(self):
        return False

    def load_all(self):
        if 'Quantities' not in self._xls.sheet_names():
            self._xls.create_sheet('Quantities')
            self._xls.write_row('Quantities', 0, INDEX_HEADINGS)
        self._qsheet = self._xls.sheet_by_name('Quantities')
        self._qs = [self._qsheet.row_dict(i) for i in range(1, self._qsheet.nrows)]
        self._qd = {k['external_ref']: k for k in self._qs}
