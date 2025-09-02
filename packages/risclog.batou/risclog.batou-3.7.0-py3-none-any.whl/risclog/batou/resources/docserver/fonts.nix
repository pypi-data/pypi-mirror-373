{ pkgs, lib, ... }:
{
  nixpkgs.config.allowUnfree = true;
  fonts.packages = with pkgs; [
      kochi-substitute
      xorg.fontbhlucidatypewriter75dpi
      xorg.fontbhlucidatypewriter100dpi
      ipafont
      corefonts
      liberation_ttf
      junicode
      wqy_microhei
      wqy_zenhei
      source-code-pro
  ];
  # Make Zertifikatsportal certificates look pretty
  fonts.fontconfig.localConf = "
<alias>
    <family>Lucida Sans Typewriter</family>
    <prefer>
        <family>Liberation Mono</family>
    </prefer>
</alias>
";
}
