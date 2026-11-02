[app]
title = Aether AI
package.name = aether
package.domain = org.aether.ai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.1
requirements = python3,kivy,requests,plyer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,RECORD_AUDIO
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
icon.filename = logo.png
presplash.filename = logo.png

[buildozer]
log_level = 2
warn_on_root = 1
