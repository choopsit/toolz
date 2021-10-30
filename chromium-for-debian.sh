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

    target_dir=/usr/lib/chromium/libwidevinecdm.so
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


libwidevine_original() {
    _chrome_ver=$(chromium --version | awk '{print $2}')
    # Debian's Chromium has a patch to read libwidevinecdm.so in ~/.local/lib
    # However, in 79 and newer, you must use the WidevineCdm directory instead of
    # the libwidevinecdm.so file
    _target_dir=~/.local/lib/WidevineCdm
    _move_type=user_directory
    # To have it accessible by all users, uncomment the below instead
    _target_dir=/usr/lib/chromium/WidevineCdm
    _move_type=system_directory
    
    mkdir -p /tmp/chromium_widevine
    pushd /tmp/chromium_widevine
    
    # Download deb, which has corresponding Widevine version
    # Support resuming partially downloaded (or skipping re-download) with -c flag
    wget -c https://dl.google.com/linux/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${_chrome_ver}-1_amd64.deb
    # Use below link for unstable Chrome versions
    #wget -c https://dl.google.com/linux/deb/pool/main/g/google-chrome-unstable/google-chrome-unstable_${_chrome_ver}-1_amd64.deb
    
    # Unpack deb
    rm -r unpack_deb || true
    mkdir unpack_deb
    dpkg-deb -R google-chrome-stable_${_chrome_ver}-1_amd64.deb unpack_deb
    
    if [[ "$_move_type" == 'shared_obj' ]]; then
    	# Move libwidevinecdm.so to target dir
    	mkdir -p $_target_dir
    	mv unpack_deb/opt/google/chrome/WidevineCdm/_platform_specific/linux_x64/libwidevinecdm.so $_target_dir
    elif [[ "$_move_type" == 'user_directory' ]]; then
    	# Move WidevineCdm to target dir owned by current user
    	rm -r $_target_dir || true
    	mv unpack_deb/opt/google/chrome/WidevineCdm $_target_dir
    elif [[ "$_move_type" == 'system_directory' ]]; then
    	# Move WidevineCdm to target dir in root-owned location
    	sudo rm -r $_target_dir || true
    	sudo mv unpack_deb/opt/google/chrome/WidevineCdm $_target_dir
    	sudo chown -R root:root $_target_dir
    else
    	printf 'ERROR: Unknown value for $_move_type: %s\n' "$_move_type"
    	exit 1
    fi
    
    popd
    rm -r /tmp/chromium_widevine

    exit
}


if [[ $1 =~ ^-(h|-help)$ ]]; then
    usage 0
elif [[ $1 =~ ^-(o|-original) ]]; then
    libwidevine_original
    launcher_patch
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
