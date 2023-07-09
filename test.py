import argostranslate.package
import argostranslate.translate

from_code = "zh"
to_code = "en"

# Download and install Argos Translate package
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(
        lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
    )
)
argostranslate.package.install_from_path(package_to_install.download())

# Translate
translatedText = argostranslate.translate.translate("每个人都有他的作战策略，直到脸上中了一拳。这首歌使我想起了我年轻的时候。", from_code, to_code)
print(translatedText)
# '¡Hola Mundo!'