import tempfile
import unittest
from pathlib import Path
from scripts.validate_page_links import validate

class ProjectLinks(unittest.TestCase):
    def site(self, href):
        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root=Path(temporary.name)
        (root/'index.html').write_text('<html>Magazine home</html>')
        issue=root/'morning/001/index.html'
        issue.parent.mkdir(parents=True)
        issue.write_text(f'<a href="{href}">杂志首页</a>')
        return root

    def test_two_levels_return_to_project_home(self):
        validate(self.site('../../index.html'))

    def test_three_levels_escape_project_on_github_pages(self):
        with self.assertRaisesRegex(AssertionError,'escapes project'):
            validate(self.site('../../../index.html'))

    def test_missing_local_destination_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Missing local link'):
            validate(self.site('../../missing.html'))

if __name__=='__main__': unittest.main()
