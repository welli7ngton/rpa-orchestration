*** Settings ***
Library    SeleniumLibrary
Library    ./libraries/browser_utils/browser_utils.py
Library    ./libraries/remote_file_handler/remote_file_handler.py

*** Keywords ***
Prepara Browser Remoto
    [Arguments]    ${url}    ${browser}    ${remote_url}

    ${BROWSER_OPTIONS}=    Get Default Browser Options    browser_name=${BROWSER}
    ${BROWSER_OPTIONS}=    Set DownloadsEnabled Option    ${BROWSER_OPTIONS}

    Open Browser    url=${url}    browser=${browser}    remote_url=${remote_url}    options=${BROWSER_OPTIONS}
