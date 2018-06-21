def _push_state(self):
    self._state_stack.append({
        self._SK_TXT: self._txt,
        self._SK_ROW: self._row,
        self._SK_COL: self._col,
        self._SK_OCC: 0,
    })


def _pop_state(self):
    res = self._state_stack.pop()
    self._txt = res[self._SK_TXT]
    self._row = res[self._SK_ROW]
    self._col = res[self._SK_COL]
    return res


def _save_state(self):
    self._state_stack[-1][self._SK_TXT] = self._txt
    self._state_stack[-1][self._SK_ROW] = self._row
    self._state_stack[-1][self._SK_COL] = self._col
    self._state_stack[-1][self._SK_OCC] += 1


def _or(self, succ=None):
    if succ is None:
        self._or_beg()
    else:
        self._or_end(succ)


def _or_beg(self):
    self._scan_eis_prev = self._scan_eis

    self._scan_eis = []


def _or_end(self, succ):
    if not succ:
        self._error()


def _ori(self, succ=None):
    # `_ori` means OR item.

    if succ is None:
        self._ori_beg()
    else:
        self._ori_end(succ)


def _ori_beg(self):
    self._push_state()


def _ori_end(self, succ):
    if succ:
        self._save_state()

    self._pop_state()

    if succ:
        raise ScanOk()


def _o01(self, succ=None):
    # `o01` means occurrence 0 or 1.

    if succ is None:
        self._o01_beg()
    else:
        self._o01_end(succ)


def _o01_beg(self):
    self._scan_eis_prev = self._scan_eis

    self._scan_eis = []

    self._push_state()


def _o01_end(self, succ):
    if succ:
        self._save_state()

    self._pop_state()


def _o0m(self, succ=None):
    # `o0m` means occurrence 0 or more.

    if succ is None:
        self._o0m_beg()
    elif succ:
        self._save_state()
    else:
        self._o0m_end()


def _o0m_beg(self):
    self._scan_eis_prev = self._scan_eis

    self._scan_eis = []

    self._push_state()


def _o0m_end(self):
    self._pop_state()


def _o1m(self, succ=None):
    # `o1m` means occurrence 1 or more.

    if succ is None:
        self._o1m_beg()
    elif succ:
        self._save_state()
    else:
        self._o1m_end()


def _o1m_beg(self):
    self._scan_eis_prev = self._scan_eis

    self._scan_eis = []

    self._push_state()


def _o1m_end(self):
    res = self._pop_state()

    if res[self._SK_OCC] == 0:
        self._error()
