applyTextValidator("#nombres", validateName);
applyTextValidator("#apellidos", validateName);
applyTextValidator("#contraseña", validatePassword);
applyDateValidation("#nac");

/** @type HTMLImageElement */
const selected = document.querySelector("#selectedAvatar");
/** @type HTMLInputElement */
const selectedInput = document.querySelector("#selectedAvatarInput");
/** @type HTMLImageElement[] */
const avatars = [
    document.querySelector("#avatar1"),
    document.querySelector("#avatar2"),
    document.querySelector("#avatar3"),
    document.querySelector("#avatar4"),
];

const getUrlForAvatar = (id) => {
    return `/static/img/avatars/${id}/normal.gif`;
}

avatars.forEach((a, index) => {
    a.addEventListener("click", () => {
        const id = index + 1;

        selected.src = getUrlForAvatar(id);
        selectedInput.value = id;
    });
});

