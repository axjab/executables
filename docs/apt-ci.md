# Automatic APT releases

A push to `master` stages the tracked, non-hidden executables in the repository
root with one `pkg add executable` call per file. The workflow rebuilds the
staged `bin/` in the disposable checkout. Add, update, rename, or delete the
root files in Git. Commit new scripts with their executable bit set.
The existing `link` symlink and `open` file are preserved with their current
file types when present in the source tree.

The workflow builds and publishes `scripts` to `apt.alj.cx`. It appends
`+git<run number>` to the version from `.pkg/packages/scripts/DEBIAN/control`
in the runner checkout. A rerun uses the same version.

## One-time setup

In `axjab/scripts`, create the GitHub Actions environment `apt-production`
and restrict its deployment branches to `master`.

| Name | Kind | Value |
| --- | --- | --- |
| `APT_SSH_TARGET` | Variable | The publishing `user@host`. Use the existing APT account whose home is `/srv/pkg/apt`. |
| `APT_SSH_PORT` | Optional variable | SSH port. Defaults to `22`. |
| `APT_SSH_KNOWN_HOSTS` | Variable | The verified SSH host key entry. Use `[host]:port` for a custom port. |
| `APT_SSH_PRIVATE_KEY` | Secret | A dedicated SSH private key usable without a prompt. Authorize its public key on the publishing account. |

Use `ssh -G apt` where that alias is configured to see the host, user, and
port. The SSH endpoint must be reachable from a GitHub-hosted runner. The
existing APT signing key stays on the server.

After pushing the workflow, check **Actions → Publish scripts to APT**.
On a configured APT client, run `sudo apt update` and
`apt-cache policy scripts` to check the new version.
