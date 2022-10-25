applyTextValidator("#nombres", validateName);
applyTextValidator("#apellidos", validateName);
applyTextValidator("#contraseña", validatePassword);
applyDateValidation("#nac");

/** @type HTMLInputElement */
const avatar = document.querySelector("#avatar")

const avatars = [
    document.querySelector("#avatar1"),
    document.querySelector("#avatar3"),
]

const selectAvatar = (selector) => {
    const avatarId = selector == "#avatar1" ? 1 :
                     selector == "#avatar3" ? 3 :
                     1;

    avatar.value = avatarId;
    avatars.forEach((a) => a.classList.remove("selected"));
    document.querySelector(selector).classList.add("selected")
}

avatars.forEach((a) => a.addEventListener("click", () => {
    selectAvatar(`#${a.id}`)
}))
