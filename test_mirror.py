import json
import unittest
from unittest.mock import patch
import mirror

DIGEST = 'sha256:' + 'a' * 64
RAW = json.dumps({'manifests': [{'platform': {'architecture': a}} for a in ['amd64', 'arm64']]})
VERSION = '0.2.37-remix.138.1'

class MirrorTests(unittest.TestCase):
    def test_source_failure_never_writes(self):
        with patch('mirror.run', side_effect=RuntimeError('indisponible')) as run:
            with self.assertRaises(RuntimeError): mirror.mirror()
            self.assertEqual(run.call_count, 1)

    def test_rejects_missing_architecture_before_login(self):
        with patch('mirror.run', side_effect=[DIGEST, '{"manifests": []}']) as run:
            with self.assertRaises(RuntimeError): mirror.mirror()
            self.assertEqual(run.call_count, 2)

    def test_pins_and_verifies_both_tags(self):
        copied = []
        def run(*args, **kwargs):
            if '--format' in args: return DIGEST
            if args[1] == 'login': return ''
            if args[1] == 'copy':
                self.assertIn('docker://' + mirror.SOURCE + '@' + DIGEST, args)
                self.assertIn('--all', args)
                self.assertIn('--preserve-digests', args)
                copied.append(args[-1]); return ''
            if '--raw' in args:
                if mirror.TARGET in args[-1] and args[-1] not in copied: return '{}'
                return RAW
            return json.dumps({'Labels': {'org.opencontainers.image.version': VERSION}})
        with patch('mirror.run', side_effect=run), patch.dict('os.environ', {'GHCR_USER':'test', 'GHCR_TOKEN':'test-only'}):
            mirror.mirror()
        self.assertEqual(copied, ['docker://' + mirror.TARGET + ':' + VERSION, 'docker://' + mirror.TARGET + ':latest'])

if __name__ == '__main__': unittest.main()
