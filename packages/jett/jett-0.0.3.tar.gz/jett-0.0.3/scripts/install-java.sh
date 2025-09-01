#!/bin/zsh

# A script to install a compatible Java version for PySpark on macOS using Homebrew.
# This script is specifically for users of the zsh shell.
#
# Usage:
#   1. Make it executable: chmod +x ./scripts/install-java.sh
#   2. Run it: ./scripts/install-java.sh

# --- Configuration ---
# You can change this to "openjdk@11" if needed for older projects.
# Spark 3.x works well with Java 11 and 17.
JAVA_FORMULA="openjdk@11"
SHELL_PROFILE="$HOME/.zshrc"

# Exit script if any command fails
set -e

# --- Main execution ---

echo "--- Starting Java Installation for PySpark ---"

check_prerequisites() {
  # 1. Check for Homebrew
  echo "1. Checking for Homebrew..."
  if ! command -v brew &> /dev/null; then
      echo "[ERROR] Homebrew is not installed."
      echo "Please install it first by running the command from https://brew.sh"
      echo "Then, run this script again."
      exit 1
  fi
  echo "   - Homebrew found."
}

install_by_homebrew() {
  # 2. Install OpenJDK using Homebrew
  echo "2. Installing ${JAVA_FORMULA} using Homebrew..."
  echo "   - This may take a few minutes."
  if brew list $JAVA_FORMULA &>/dev/null; then
      echo "   - ${JAVA_FORMULA} is already installed. Skipping installation."
  else
      brew install "$JAVA_FORMULA"
  fi
  echo "   - Installation complete."
}

setup_environment() {
  # 3. Configure .zshrc with JAVA_HOME
  echo "3. Configuring your shell profile: ${SHELL_PROFILE}"

  # Get the installation path from brew
  JAVA_HOME_PATH=$(brew --prefix "$JAVA_FORMULA")
  START_MARKER="# BEGIN Java Environment (Managed by script)"
  END_MARKER="# END Java Environment"

  # 3a. Remove any existing managed block to ensure a clean state.
  # The -i.bak flag creates a backup of your original .zshrc file.
  if grep -q "$START_MARKER" "$SHELL_PROFILE"; then
      echo "   - Found old Java configuration. Removing it before adding the new one."
      sed -i.bak "/${START_MARKER}/,/${END_MARKER}/d" "$SHELL_PROFILE"
  fi

  # Add JAVA_HOME to the profile if it's not already there
  if ! grep -q "export JAVA_HOME=" "$SHELL_PROFILE"; then
      echo "   - Adding updated JAVA_HOME to your profile..."
      {
          echo ''
          echo "$START_MARKER"
          echo '# Set JAVA_HOME for Spark/PySpark'
          echo "export JAVA_HOME=\"${JAVA_HOME_PATH}\""
          # shellcheck disable=SC2016
          echo 'export PATH="$JAVA_HOME/bin:$PATH"'
          echo "$END_MARKER"
      } >> "$SHELL_PROFILE"
      echo "   - JAVA_HOME has been set."
  else
      echo "   - Your profile already contains JAVA_HOME. Please verify it is set correctly."
      echo "   - Current setting: $(grep 'export JAVA_HOME=' "${SHELL_PROFILE}")"
  fi
}

main() {
  echo "--- Starting Java Installation ---"
  check_prerequisites
  install_by_homebrew
  setup_environment
  echo ""
  echo "4. Linking Java for all applications on macOS..."
  echo "   - This requires administrator privileges to create a system-wide link."
  sudo ln -sfn "${JAVA_HOME_PATH}/libexec/openjdk.jdk" "/Library/Java/JavaVirtualMachines/openjdk.jdk"
  echo "   - System link created successfully."

  echo ""
  echo "--- Java Installation Complete! ---"
  echo ""
  echo "IMPORTANT: You must now reload your shell for the changes to take effect."
  echo "Run this command:"
  echo "  source ${SHELL_PROFILE}"
  echo ""
  echo "Or simply open a new terminal window."
  echo "After that, verify the installation by running the commands below."
}

main
