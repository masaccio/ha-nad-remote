#! /bin/bash
REMOTE_HOST="hass"

directories="custom_components/nad_remote/nad_receiver custom_components/nad_remote/translations"

echo $(tput setaf 2)rmdir /config/custom_components/nad_remote$(tput sgr0)
ssh $REMOTE_HOST "rm -rf /config/custom_components/nad_remote"

for dir in $directories; do
  echo $(tput setaf 2)mkdir /config/$dir$(tput sgr0)
  ssh $REMOTE_HOST "mkdir -p /config/$dir"
done

set -o noglob
files="*.py *.json translations/*.json nad_receiver/*.py"
for file in $files; do
  dir="custom_components/nad_remote/"$(dirname "$file")
  dir="${dir/\/./}"
  file=$(basename "$file")
  set +o noglob
  echo $(tput setaf 2)copy "$dir/$file"$(tput sgr0)
  scp -q $dir/$file $REMOTE_HOST:/config/$dir
done

echo $(tput setaf 2)"Restarting HA Core"$(tput sgr0)
ssh $REMOTE_HOST "source /etc/profile.d/homeassistant.sh && ha core restart"
echo $(tput setaf 2)"Done"$(tput sgr0)
