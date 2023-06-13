#set -ex
username=$(whoami)
echo "Installing some system packages: gcc, sqlite3" #, cargo."
sudo apt install gcc sqlite3 libsqlite3-dev unzip curl # cargo # cargo --> rust

echo "Setting up python env..."
echo "Your python version is: "
python3 --version
echo "If it is not 3.9+, you may experience issues running CB2."
echo "Additionally, there may be issues running 3.11+."

echo "Installing poetry for you. Activate an environment using 'poetry shell'"
curl -sSL https://install.python-poetry.org | python3 -

while true; do
    echo "you are currently in:"
    python3 -c "import sys; print(sys.prefix)"
    read -p "Are you running an appropriate virtual environment already? If not, please quit and activate it before running this script. > " yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no. ";;
    esac
done

# python3 -m venv venv
# . ./venv/bin/activate
poetry install
python3 -m pip install -r requirements.txt

echo "Downloading WebGL client..."
cd server/www/
# wget https://github.com/lil-lab/cb2/releases/download/deployed-march-2023/WebGL.zip
wget https://github.com/lil-lab/cb2/releases/download/dev-june-2023/WebGL.zip
echo "Decompressing client."
unzip WebGL
cd -

echo "Downloading kmonad binary for keyboard remapping"
cd drivercb2
wget https://github.com/kmonad/kmonad/releases/download/0.4.1/kmonad-0.4.1-linux
chmod +x ./kmonad-0.4.1-linux
echo "done"
cd -

echo "Running local self-play as a test..."
sleep 1
python3 -m py_client.demos.local_self_play --num_games=10 --config_filepath="server/config/local-covers-config.yaml"
echo "DONE"
