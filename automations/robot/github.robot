*** Settings ***
Library    SeleniumLibrary    run_on_failure=${None}
*** Variables ***
${USER}

*** Test Cases ***
Main
    Log To Console    Iniciando script robotframework
    Log To Console    ${USER}
    Open Browser    url=https://github.com/welli7ngton    browser=firefox
    Sleep    10s
    Log To Console    Finalizando script robotframework
    Close Browser
