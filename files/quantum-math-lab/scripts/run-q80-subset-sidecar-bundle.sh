#!/usr/bin/env bash
set -euo pipefail

# Legacy compatibility alias.
# The q20 subset-sidecar bundle was originally misnamed as a q80 script because
# it was part of the wider Phase 3 scale-up narrative. Keep this shim so older
# docs and commands still work, but route all new use through the canonical q20
# entrypoint.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT_DIR/run-q20-subset-sidecar-bundle.sh" "$@"
