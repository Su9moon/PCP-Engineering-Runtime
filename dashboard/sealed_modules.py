"""Immutable, process-local copies of the audited Ruflo JavaScript modules."""
import base64
import fcntl
import hashlib
import json
import os
import tempfile
from contextlib import ExitStack
from pathlib import Path

ROLES = ("launcher", "tool", "core")
SEALS = fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL

BOOTSTRAP = r"""
import {createHash} from 'node:crypto';
import {appendFileSync, readFileSync} from 'node:fs';
import {Session} from 'node:inspector';
import {registerHooks} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const snapshots = new Map(manifest.map(([url, entry]) => [pathToFileURL(fileURLToPath(url)).href, entry]));
const names = new Map([...snapshots.keys()].map(url => [new URL(url).pathname.split('/').pop(), url]));
function expectedPath(specifier) {
    return names.get(specifier.split(/[?#]/, 1)[0].split('/').pop());
}
registerHooks({
    resolve(specifier, context, nextResolve) {
        const result = nextResolve(specifier, context);
        const expected = expectedPath(specifier) ?? expectedPath(result.url);
        if (expected && result.url !== expected) throw new Error('Audited module resolved through an unapproved alias');
        return result;
    },
    load(url, context, nextLoad) {
        const snapshot = snapshots.get(url);
        if (!snapshot) return nextLoad(url, context);
        if (context.format && context.format !== 'module') throw new Error('Audited module format changed');
        return {format: 'module', shortCircuit: true, source: readFileSync('/proc/self/fd/' + snapshot.fd)};
    },
});
const inspector = new Session();
inspector.connect();
inspector.on('Debugger.scriptParsed', ({params}) => {
    const snapshot = snapshots.get(params.url);
    if (!snapshot) return;
    inspector.post('Debugger.getScriptSource', {scriptId: params.scriptId}, (error, result) => {
        const digest = error ? null : createHash('sha256').update(result.scriptSource, 'utf8').digest('hex');
        appendFileSync(proof, JSON.stringify([snapshot.role, digest]) + '\n', {mode: 0o600});
    });
});
await new Promise((resolve, reject) => inspector.post('Debugger.enable', {}, err => err ? reject(err) : resolve()));
"""


class ModuleProofError(RuntimeError):
    pass


class SealedModules:
    def __init__(self, artifacts, contract):
        self.artifacts = artifacts
        self.contract = contract
        self.stack = ExitStack()

    def __enter__(self):
        try:
            directory = self.stack.enter_context(tempfile.TemporaryDirectory(prefix="pcp-ruflo-proof-"))
            self.proof = Path(directory) / "compiled.jsonl"
            records = []
            self.fds = []
            for role in ROLES:
                fd = os.memfd_create(f"pcp-ruflo-{role}", os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
                self.stack.callback(os.close, fd)
                self.fds.append(fd)
                content = self.artifacts[role]
                with os.fdopen(fd, "wb", closefd=False) as handle:
                    handle.write(content)
                    handle.flush()
                fcntl.fcntl(fd, fcntl.F_ADD_SEALS, SEALS)
                verified = os.pread(fd, len(content) + 1, 0)
                if (fcntl.fcntl(fd, fcntl.F_GET_SEALS) != SEALS
                        or hashlib.sha256(verified).hexdigest() != self.contract[role]["sha256"]):
                    raise ModuleProofError("Ruflo 模块封印检查失败。")
                records.append((Path(self.contract[role]["path"]).as_uri(), {"role": role, "fd": fd}))
            bootstrap = f"const manifest = {json.dumps(records)};\nconst proof = {json.dumps(str(self.proof))};\n{BOOTSTRAP}"
            self.import_url = "data:text/javascript;base64," + base64.b64encode(bootstrap.encode()).decode("ascii")
            return self
        except BaseException:
            self.stack.close()
            raise

    def __exit__(self, *args):
        self.stack.close()

    def check_compiled(self):
        try:
            receipts = [json.loads(line) for line in self.proof.read_text().splitlines()]
        except (OSError, ValueError) as exc:
            raise ModuleProofError("缺少实际编译的封印模块回执。") from exc
        expected = {(role, self.contract[role]["sha256"]) for role in ROLES}
        if {tuple(item) for item in receipts} != expected:
            raise ModuleProofError("实际编译的 Ruflo 模块摘要与封印制品不一致。")
        return dict(receipts)
