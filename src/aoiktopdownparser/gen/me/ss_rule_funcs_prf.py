    @staticmethod
    def _opts_get(arg_group):
        #/
        pair_s = []
        item = arg_group
        while 'arg_item' in item:
            pair_s.append(item.arg_item.res)
            item = item.arg_item
        opts = dict(pair_s)
        return opts

