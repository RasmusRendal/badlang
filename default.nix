with import <nixpkgs> {};

stdenv.mkDerivation {
  name = "badlang";
  src = ./.;

  buildInputs = [ python38 python38Packages.arpeggio ];

}
