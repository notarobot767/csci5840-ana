cd "$(dirname "$0")" || exit 1
cd ..
# ensure script will always set working dir to script location

ssh-keygen -t ed25519 -N "" -f ./secrets/guac_id_ed25519
ssh-keygen -t ecdsa -b 256 -N "" -f ./secrets/guac_id_ecdsa
ssh-keygen -t rsa -b 2048 -N "" -f ./secrets/guac_id_rsa