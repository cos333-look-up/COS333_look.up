const isNumericInput = (event) => {
    const key = event.keyCode;
    return ((key >= 48 && key <= 57) || // Allow number line
        (key >= 96 && key <= 105) // Allow number pad
    );
};

const isModifierKey = (event) => {
    const key = event.keyCode;
    return (event.shiftKey === true || key === 35 || key === 36) || // Allow Shift, Home, End
        (key === 8 || key === 9 || key === 13 || key === 46) || // Allow Backspace, Tab, Enter, Delete
        (key > 36 && key < 41) || // Allow left, up, right, down
        (
            // Allow Ctrl/Command + A,C,V,X,Z
            (event.ctrlKey === true || event.metaKey === true) &&
            (key === 65 || key === 67 || key === 86 || key === 88 || key === 90)
        )
};

const enforceFormat = (event) => {
    // Input must be of a valid number format or a modifier key, and not longer than ten digits
    if(!isNumericInput(event) && !isModifierKey(event)){
        event.preventDefault();
    }
};

const formatToPhone = (event) => {
    if(isModifierKey(event)) {return;}

    const input = event.target.value.replace(/\D/g,'')
    let areaCode = input.substring(0, 3);
    let middle = input.substring(3, 6);
    let last = input.substring(6, 10);
    
    if(input.length > 10)
    {
        let countryCode = input.substring(0, input.length - 10);
        let areaCode = input.substring(input.length - 10, input.length - 7);
        let middle = input.substring(input.length - 7, input.length - 4);
        let last = input.substring(input.length - 4, input.length);
        event.target.value = `+${countryCode} (${areaCode}) ${middle}-${last}`;
    }
    else if(input.length > 6){event.target.value = `(${areaCode}) ${middle}-${last}`;}
    else if(input.length > 3){event.target.value = `(${areaCode}) ${middle}`;}
    else if(input.length > 0){event.target.value = `(${areaCode}`;}
};

const formatToSocial = (event) => {
    if(isModifierKey(event)) {return;}

    const firstChar = event.target.value.charAt(0);

    if(firstChar !== "@"){event.target.value = `@${event.target.value}`;}
};

const phoneInput = document.getElementById('phone');
phoneInput.addEventListener('keydown',enforceFormat);
phoneInput.addEventListener('keyup',formatToPhone);

const instagramInput = document.getElementById('instagram');
instagramInput.addEventListener('keyup',formatToSocial);

const snapchatInput = document.getElementById('snapchat');
snapchatInput.addEventListener('keyup',formatToSocial);