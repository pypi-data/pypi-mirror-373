echo "📥 Add files from ../assets-docs"
cp -R ../assets-docs/docs/assets/ docs/assets/
cp -R ../assets-docs/includes/ includes/
cp -R ../assets-docs/overrides/ overrides/

echo "📥 Add files from ../assets-branding"
mkdir -p docs/assets/images/
cp ../assets-branding/easydiffraction/hero/dark.png docs/assets/images/hero_dark.png
cp ../assets-branding/easydiffraction/hero/light.png docs/assets/images/hero_light.png
cp ../assets-branding/easydiffraction/logos/dark.svg docs/assets/images/logo_dark.svg
cp ../assets-branding/easydiffraction/logos/light.svg docs/assets/images/logo_light.svg
cp ../assets-branding/easydiffraction/icons/color.png docs/assets/images/favicon.png

mkdir -p overrides/.icons/
cp ../assets-branding/easydiffraction/icons/bw.svg overrides/.icons/easydiffraction.svg
cp ../assets-branding/easyscience-org/icons/eso-icon_bw.svg overrides/.icons/easyscience.svg
