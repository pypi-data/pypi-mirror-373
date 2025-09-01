#!/bin/bash

# A script to automate the local installation of Apache Spark.
#
# Usage:
#   1. Make it executable: chmod +x ./scripts/install-spark.sh
#   2. Run it: ./scripts/install-spark.sh

# --- Configuration ---
# You can change these versions if needed.
SPARK_VERSION="3.4.4"
HADOOP_VERSION="3"
INSTALL_PREFIX="$HOME/opt"
SPARK_HOME="$INSTALL_PREFIX/spark"
SHELL_PROFILE="$HOME/.zshrc"

# Exit script if any command fails
set -e

# Function to check for required commands like java and wget/curl
check_prerequisites() {
    echo "1. Checking for prerequisites..."
    if ! command -v java &> /dev/null; then
        echo "[ERROR] Java is not installed. Please install a compatible Java version (8, 11, or 17) and try again."
        exit 1
    fi
    # Check for either wget or curl for downloading
    if ! command -v wget &> /dev/null && ! command -v curl &> /dev/null; then
        echo "[ERROR] 'wget' or 'curl' is required to download Spark. Please install one of them."
        exit 1
    fi
    echo "   - Java found: $(java -version 2>&1 | head -n 1)"
    echo "   - Prerequisite check passed."
}

# Function to download and extract Spark
download_and_extract() {
    # NOTE: Construct the download URL
    local spark_tgz="spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz"
    local archive_url="https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/${spark_tgz}"

    echo "2. Downloading Spark ${SPARK_VERSION}..."
    # NOTE: Create the installation directory if it doesn't exist
    mkdir -p "$INSTALL_PREFIX"

    if command -v wget &> /dev/null; then
        wget -q --show-progress -O "/tmp/${spark_tgz}" "${archive_url}"
    else
        curl -L -o "/tmp/${spark_tgz}" "${archive_url}"
    fi

    echo "   - Download complete."
    echo "3. Extracting Spark to ${SPARK_HOME}..."

    # Remove existing installation to ensure a clean slate
    if [ -d "$SPARK_HOME" ]; then
        echo "   - Found existing installation. Removing it for a clean install."
        rm -rf "$SPARK_HOME"
    fi

    # Extract the downloaded archive to a temporary name, then rename it
    local temp_extract_dir="$INSTALL_PREFIX/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}"
    tar -xzf "/tmp/${spark_tgz}" -C "$INSTALL_PREFIX"
    mv "$temp_extract_dir" "$SPARK_HOME"

    echo "   - Extraction complete."

    # Clean up the downloaded file
    rm "/tmp/${spark_tgz}"
    echo "   - Cleaned up downloaded archive."
}

# Function to set up environment variables in shell profile
setup_environment() {
    echo "4. Setting up environment variables..."
#    local SHELL_PROFILE=""
#    # Detect the user's shell profile file
#    if [ -n "$ZSH_VERSION" ]; then
#        SHELL_PROFILE="$HOME/.zshrc"
#    elif [ -n "$BASH_VERSION" ]; then
#        SHELL_PROFILE="$HOME/.bashrc"
#    else
#        # Fallback for other shells, might need manual configuration
#        SHELL_PROFILE="$HOME/.profile"
#    fi

    echo "   - Updating shell profile: ${SHELL_PROFILE}"

    # Ensure the profile file exists
    touch "$SHELL_PROFILE"
    local START_MARKER="# BEGIN Spark Environment (Managed by script)"
    local END_MARKER="# END Spark Environment"

    # Remove the old block if it exists, creating a backup file
    if grep -q "$START_MARKER" "$SHELL_PROFILE"; then
        echo "   - Found old Spark configuration. Removing it first."
        sed -i.bak "/${START_MARKER}/,/${END_MARKER}/d" "$SHELL_PROFILE"
    fi

    # Add environment variables if they aren't already there to prevent duplicates
    if ! grep -q "export SPARK_HOME=" "$SHELL_PROFILE"; then
        echo "   - Adding SPARK_HOME and updating PATH..."
        {
            echo ''
            echo "$START_MARKER"
            echo '# Spark environment'
            echo "export PYSPARK_HADOOP_VERSION=${HADOOP_VERSION}"
            echo "export SPARK_HOME=\"${SPARK_HOME}\""
            # shellcheck disable=SC2016
            echo 'export PATH="$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH"'
            echo "$END_MARKER"
        } >> "$SHELL_PROFILE"
        echo "   - SPARK_HOME has been set."
    else
        echo "   - Spark environment variables already exist in profile. Skipping."
        echo "   - Current setting: $(grep 'export SPARK_HOME=' "${SHELL_PROFILE}")"
    fi
}

main() {
    echo "--- Starting Apache Spark Local Installation ---"
    check_prerequisites
    download_and_extract
    setup_environment
    echo ""
    echo "--- Installation Complete! ---"
    echo ""
    echo "IMPORTANT: You must now reload your shell for the changes to take effect."
    echo "Run this command:"
    echo "  source ${SHELL_PROFILE:-~/.bashrc or ~/.zshrc}"
    echo ""
    echo "Or simply open a new terminal window."
    echo "After that, verify the installation by running:"
    echo "  spark-submit --version"
}

main
