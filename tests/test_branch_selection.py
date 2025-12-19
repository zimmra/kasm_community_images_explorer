import unittest
from unittest import mock

import search_github


class DummyResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data


class TestBranchSelection(unittest.TestCase):
    def test_parse_repo_uses_target_branch(self):
        call_params = []
        target_branch = search_github.TARGET_BRANCH

        def fake_make_request(url, params=None):
            call_params.append((url, params))
            if url.endswith("/contents/workspaces"):
                return DummyResponse([
                    {'type': 'dir', 'url': 'folder-url', 'name': 'example-workspace'}
                ])
            if url == 'folder-url':
                return DummyResponse([
                    {
                        'type': 'file',
                        'name': 'workspace.json',
                        'download_url': 'workspace-download'
                    }
                ])
            if url == 'workspace-download':
                return DummyResponse({
                    'compatibility': [
                        {'image': 'example/image', 'version': '1.0'}
                    ]
                })
            return DummyResponse({}, status_code=404)

        with mock.patch('search_github.make_request', side_effect=fake_make_request):
            with mock.patch('search_github.skopeo_inspect', return_value=True):
                result = search_github.parse_repo("owner/repo")

        self.assertTrue(result)
        ref_calls = [(url, params) for url, params in call_params if params is not None]
        self.assertGreaterEqual(len(ref_calls), 2)
        for _, params in ref_calls:
            self.assertEqual({'ref': target_branch}, params)


if __name__ == '__main__':
    unittest.main()
