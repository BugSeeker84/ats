#!/usr/bin/env bash
# Bind a global GNOME shortcut to the ATS clipboard launcher (~/.local/bin/ats-clip).
# Run this in YOUR desktop session (a normal terminal), not over SSH.
#
#   ./setup-hotkey.sh                  # binds Ctrl+1 (default)
#   ./setup-hotkey.sh '<Primary><Alt>j'  # binds Ctrl+Alt+J (use if Ctrl+1 conflicts)
set -e

BINDING="${1:-<Primary>1}"
LAUNCHER="/home/phoenix/.local/bin/ats-clip"
BASE="org.gnome.settings-daemon.plugins.media-keys"
KP="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/ats/"

cur="$(gsettings get "$BASE" custom-keybindings 2>/dev/null || echo '@as []')"
case "$cur" in
  *"$KP"*)         new="$cur" ;;                 # already registered
  '@as []'|'[]')   new="['$KP']" ;;              # empty list
  *)               new="${cur%]}, '$KP']" ;;     # append, keep existing
esac
gsettings set "$BASE" custom-keybindings "$new"

S="$BASE.custom-keybinding:$KP"
gsettings set "$S" name "ATS Resume"
gsettings set "$S" command "$LAUNCHER"
gsettings set "$S" binding "$BINDING"

echo "Bound '$BINDING' -> $LAUNCHER"
echo "  command: $(gsettings get "$S" command)"
echo "  binding: $(gsettings get "$S" binding)"
echo "Now copy a JD and press the key. If it still does the app default, re-run with a"
echo "non-conflicting combo, e.g.:  ./setup-hotkey.sh '<Primary><Alt>j'"
