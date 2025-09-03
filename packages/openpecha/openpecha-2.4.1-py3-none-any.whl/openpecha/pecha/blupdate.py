from diff_match_patch import diff_match_patch


class DiffMatchPatch:
    def __init__(self, old_base: str, new_base: str):
        self.dmp = diff_match_patch()
        self.dmp.Diff_Timeout = 60
        self.diffs = self.dmp.diff_main(old_base, new_base, checklines=False)

    def get_updated_coord(self, coordinate: int):
        return self.dmp.diff_xIndex(self.diffs, coordinate)
