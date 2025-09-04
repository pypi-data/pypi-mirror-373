#!/bin/bash
#
# do the necessary things to build and publish python project
#



function yes_or_no {
    while true; do
        read -p "$* [y/n]: " yn
        case $yn in
            [Yy]*) echo 0; return 0  ;;
            [Nn]*) echo 1 ; return  1 ;;
        esac
    done
}

echo "---------------------------------------------------------------"
echo "____ speed up publishing to pypi ______________________________"
echo "---------------------------------------------------------------"




#if [ -e README.org ]; then
#    pandoc -i README.org -o README.md
#
#fi
# ---------- README
if [ -f README.org ]; then
echo "Q... Convert README.org to README.md?"
YN=$(yes_or_no)
echo ... $YN ...
if [ "$YN" = "0" ]; then
    echo i... converting org to md by force
    pandoc README.org -o README.md
fi
fi

git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ] ;

if [  "$?" != "0" ]; then
    echo x... git is not clean... do something about it
    YN=$(yes_or_no)
    echo ... $YN ...
    if [ "$YN" = "0" ]; then
	echo x... AUTOCOMMIT .............
	sleep 1
	echo x... AUTOCOMMIT .............
	sleep 1
	git commit -a -m "debug with automatic commit"
    fi
fi



if [ -d "dist" ]; then
    echo i...  dist/ exists
else
    echo x... folder dist/ doesnt exist
    echo i... continuing...
    sleep 1
    #exit 1
fi

echo "Q... delete all prepared things for IN dist?"
YN=$(yes_or_no)
echo ... $YN ...
if [ "$YN" = "0" ]; then
    rm dist/*
fi


echo "Q... increase version by PATCH?"
YN=$(yes_or_no)
echo ... $YN ...
if [ "$YN" = "0" ]; then

    if [ ! -f .bumpversion.cfg ]; then
	echo i... creating .bumpversion ... should be 0.1.0 initially to conform pytoml
	cat <<EOF > .bumpversion.cfg
[bumpversion]
current_version = 0.1.0
commit = True
tag = True

[bumpversion:file:pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"
EOF
    fi

    bumpversion patch
    # rm dist/*

    echo "Q... git push all tags ??"
    YN=$(yes_or_no)
    echo ... $YN ...
    if [ "$YN" = "0" ]; then
	git push origin --all && git push origin --tags
    fi

fi


echo "Q... uv build ?"
YN=$(yes_or_no)
echo ... $YN ...
if [ "$YN" = "0" ]; then
    uv build
    # rm dist/*
fi



echo "Q... uv publish with __token__ ?"
YN=$(yes_or_no)
echo ... $YN ...
if [ "$YN" = "0" ]; then

#    Set a PyPI token with --token or  UV_PUBLISH_TOKEN
#    , or set a username with --username or
#    UV_PUBLISH_USERNAME
#    and password with --password or
    #    UV_PUBLISH_PASSWORD

    tok=`cat ~/.pypirc | grep pass | awk '{print$3}'`
    uv publish --username __token__ --password "$tok"
    # rm dist/*
fi
