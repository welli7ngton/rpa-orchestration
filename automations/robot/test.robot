*** Settings ***
Resource    ./resources/browser_utils.resource
*** Variables ***
${USER}

*** Test Cases ***
Main
    Log To Console    Iniciando script robotframework
    Log To Console    ${USER}
    Prepara Browser Remoto    https://github.com/welli7ngton    firefox    http://localhost:4444
    Sleep    100s
    Log To Console    Finalizando script robotframework
    Close Browser

Bain
    Open Browser    https://github.com/welli7ngton    chrome    http://localhost:4444    remote_url=http://localhost:4444
    Sleep    600s