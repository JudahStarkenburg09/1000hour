[app]
title = 1000 Hour Challenge
package.name = thousandhour
package.domain = org.yourdomain

# Source code where the main.py file is located
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Application version
version = 1.0

# Requirements
requirements = python3,kivy,plyer,pyjnius

# Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Orientation and fullscreen
orientation = portrait
fullscreen = 0

# Android specific settings
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b
android.arch = arm64-v8a
android.skip_update = False
android.accept_sdk_license = True
android.logcat_filters = *:S python:D

# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

# Optional: Uncomment and customize if needed
# android.icon.filename = %(source.dir)s/data/icon.png
# presplash.filename = %(source.dir)s/data/presplash.png
# source.exclude_patterns = license,images/*/*.jpg
# requirements.source.kivy = ../../kivy
