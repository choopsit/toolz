#!/usr/bin/env bash

set -e

__description__="Install 'chromium' and 'libwidevine.so' (for Netflix), and Fix annoying gnome-keyring spawn"
__author__="Choops <choopsbd@gmail.com>"

usage() {
    echo -e "\e[36m${__description__}\e[0m"
    echo -e "\e[36mUsage\e[0m:"
    echo "  $(basename "$0") [OPTION]"
    echo -e "\e[36mOptions\e[0m:"
    echo -e "  -h,--help: Print this help\n"
    exit $1
}

error() {
    echo -e "\e[31mE\e[0m: $1"
    exit 1
}

ok() {
    echo -e "\e[32mOK\e[0m: $1"
}

install_chromium() {
    if ! (dpkg -l | grep -q "^ii  chromium"); then
        echo "Installing 'chromium'..."
        sudo apt-get -qq install chromium >/dev/null && ok "'chromium' installed"
    else
        echo -e "\e[36mNFO\e[0m: 'chromium' already installed"
    fi
}

libwidevine_patch() {
    chrome_ver=$(chromium --version | awk '{print $2}')

    url_base=https://dl.google.com/linux/deb/pool/main/g/google-chrome-stable
    chrome_deb="google-chrome-stable_${chrome_ver}-1_amd64.deb"
    # For chromium-unstable, uncomment the 2 following lines
    #url_base=https://dl.google.com/linux/deb/pool/main/g/google-chrome-unstable
    #chrome_deb="google-chrome-unstable_${chrome_ver}-1_amd64.deb"

    chrome_url="${url_base}/${chrome_deb}"

    target_dir=/usr/lib/chromium/WidevineCdm
    tmp_folder=/tmp/chromium_widevine

    echo "Downloading '${chrome_deb}'..."

    mkdir -p "${tmp_folder}"
    pushd "${tmp_folder}" >/dev/null

    # Support resuming partially downloaded (or skipping re-download) with -c flag
    wget -cq "${chrome_url}" && ok "'${chrome_deb}' downloaded"

    echo "Extracting '${chrome_deb}'..."
    unpack_dir="${tmp_folder}/unpack_deb"
    rm -r "${unpack_dir}" 2>/dev/null || true
    mkdir "${unpack_dir}"

    dpkg-deb --raw-extract "${chrome_deb}" "${unpack_dir}" && \
        ok "'${chrome_deb}' extracted"

    echo "Deploying 'libwidevinecdm.so'..."
    libwidevine_so="${unpack_dir}/opt/google/chrome/WidevineCdm/_platform_specific/linux_x64/libwidevinecdm.so"
    sudo rm -r "${target_dir}" 2>/dev/null || true
    sudo mv "${libwidevine_so}" "${target_dir}" && ok "'libwidevinecdm.so' deployed"
    sudo chown -R root:root "${target_dir}"

    popd >/dev/null
    rm -r "${tmp_folder}"
}

launcher_patch() {
    chromium_desktop="/usr/share/applications/chromium.desktop"
    chromium_user="$HOME/.local/share/applications/chromium.desktop"

    echo "Creating new launcher..."
    base_line="Exec=/usr/bin/chromium"
    options=" --password-store=basic --oauth2-client-id=77185425430.apps.googleusercontent.com --oauth2-client-secret=OTJgUOQcT7lO7GsGZq2G4IlT %U"

    sed "s|${base_line} %U|${base_line}${options}|" "${chromium_desktop}" > "${chromium_user}" && \
        ok "Options to 'avoid gnome-keyring' and 'permit google sing-in' added to launcher"
}


if [[ $1 =~ ^-(h|-help)$ ]]; then
    usage 0
elif [[ $1 ]]; then
    error "Bad argument"
fi

if [[ $(whoami) = root ]]; then
    error "must be run as simple user"
fi

if (groups | grep -q "sudo"); then
    install_chromium
    libwidevine_patch
else
    error "'$USER' has not 'sudo' rights (needed to install 'chromium' and deploy 'libwidevine.so')"
fi

if (dpkg -l | grep -q "^ii  chromium"); then
    launcher_patch
else
    error "'chromium' not instaled"
fi
