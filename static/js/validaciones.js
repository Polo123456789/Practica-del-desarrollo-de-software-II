/*
 * NOTA: No contiene validaciones para el email, de esas se encarga el navegador
 * 
 * Uso:
 *  Para los campos de texto, aplique la validacion utilizando la funcion
 *  `applyTextValidator`. EL primer argumento es el selector del input a
 *  validar, el segundo es la funcion de validacion a utilizar.
 * 
 *  Para el campo de fecha puede utilizar la funcion `applyDateValidation`.
 *  Como unico argumento recibe el selector de el input que recibe la fecha.
 *      
 * Ejemplo:
 * 
 *      applyTextValidator("#idCampoNombres", validateName);
 *      applyTextValidator("#idCamposApellidos", validateName);
 *      applyTextValidator("#idCampoContraseña", validatePassword);
 *      applyDateValidation("#idCampoFecha");
 */

/**
 * @param {string} selector 
 * @param {(event: Event) => void} validator 
 */
const applyTextValidator = (selector, validator) => {
    const element = document.querySelector(selector);
    element?.addEventListener("keyup", validator);
}


/**
 * @param {HTMLInputElement} element 
 */
const setValid = (element) => {
    element.setCustomValidity("");
    element.reportValidity();
}


/**
 * @param {HTMLInputElement} element 
 * @param {string} errorMsg 
 */
const setInvalid = (element, errorMsg) => {
    element.setCustomValidity(errorMsg);
    element.reportValidity();
}


const isSpace = (char) => {
    return char.trim() === "";
}


const isNumber = (char) => {
    if (isSpace(char)) {
        return false;
    }
    return !isNaN(char)
}


const isAlphabetic = (char) => {
    // De esta forma para que acepte los caracteres con tildes
    return char.toLowerCase() != char.toUpperCase();
}


const specialCharacters = ".,¿?!#$";

const isSpecial = (char) => {
    for (const s of specialCharacters) {
        if (char === s) {
            return true;
        }
    }
    return false;
}


const validateName = (event) => {
    /** @type HTMLInputElement */
    const element = event.target;
    /** @type string */
    const text = element.value;
    setValid(element);

    if (text.length < 2) {
        setInvalid(element,
                   `Los nombres/apellidos tienen que tener minimo 2 caracteres `
                   + `(Actualmente ${text.length})`)
        return;
    }

    if (text.length > 30) {
        setInvalid(element,
                   `Los nombres/apellidos tienen que tener maximo 30 caracteres`
                   + ` (Actualmente ${text.length})`)
        return;
    }

    for (const c of text) {
        if (!isAlphabetic(c) && !isSpace(c)) {
            setInvalid(element,
                       `Los nombres/apellidos unicamente pueden contener letras`
                       + ` del alfabeto y espacios ('${c}' es un caracter`
                       + ` invalido)`)
        }
    }
}


const validatePassword = (event) => {
    /** @type HTMLInputElement */
    const element = event.target;
    /** @type string */
    const text = element.value;
    setValid(element);

    if (text.length < 6) {
        setInvalid(element,
                   `La contraseña tiene que tener minimo 6 caracteres `
                   + `(Actualmente ${text.length})`);
        return;
    }

    if (text.length > 12) {
        setInvalid(element,
                   `La contraseña tiene que tener maximo 12 caracteres `
                   + `(Actualmente ${text.length})`);
        return;
    }

    let hasNumber = false;
    let hasSpecial = false;
    let hasAlphabetic = false;
    let hasSpaces = false;

    for (const c of text) {
        if (isNumber(c)) {
            hasNumber = true;
        } else if (isSpecial(c)) {
            hasSpecial = true;
        } else if (isAlphabetic(c)) {
            hasAlphabetic = true;
        } else if (isSpace(c)) {
            hasSpaces = true;
        } else {
            setInvalid(element,
                       `'${c}' No es un caracter valido para las contraseñas`)
            return;
        }
    }

    if (!hasNumber) {
        setInvalid(element, 
                   `Las contraseñas tienen que tener minimo un numero`);
        return;
    }
    if (!hasSpecial) {
        setInvalid(element, 
                   `Las contraseñas tienen que tener minimo un caracter `
                   + `especial (${specialCharacters})`);
        return;
    }
    if (!hasAlphabetic) {
        setInvalid(element, 
                   `Las contraseñas tienen que tener minimo un caracter `
                   + `alfabetico`);
        return;
    }
    if (hasSpaces) {
        setInvalid(element,
                   `Las contraseñas no pueden contener espacios`)
    }
}


const applyDateValidation = (selector) => {
  /** @type HTMLInputElement */
  const element = document.querySelector(selector);

  const today = new Date();
  today.setUTCHours(0, 0, 0, 0);
  const minimum = new Date("1922-01-01");

  element.addEventListener("change", () => {
    const selected = new Date(element.value);
    setValid(element);

    if (minimum.getTime() > selected.getTime()) {
        setInvalid(element,
                   `La fecha tiene que ser mayor al 1 de enero de 1922`);
        return;
    }

    if (today.getTime() <= selected.getTime()) {
        setInvalid(element,
                   `La fecha tiene que ser anterior a el dia de hoy`);
        return;
    }
  });
}
