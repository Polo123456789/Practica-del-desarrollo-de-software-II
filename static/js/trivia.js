let done = false;

const answers = [
    document.querySelector("#r1"),
    document.querySelector("#r2"),
    document.querySelector("#r3"),
];

const result = document.querySelector("#result"); 

/**
 * @param {HTMLElement} answer
 * @return {boolean}
 */
const isCorrect = (answer) => {
    return answer.getAttribute("tg-is-correct") == '1';
}

/** @param {boolean} correct */
const sendResponse = async (correct) => {
    const response = await fetch(window.location.href, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({correct: correct})
    });
    const content = await response.json();
    console.log(content)
}

/** @param {boolean} correct */
const showResult = (correct) => {
    const texto = result.querySelector("span");
    const link = result.querySelector("a")
    if (correct) {
        texto.innerText = "Respuesta Correcta";
        link.innerText = "Continuar";
        link.href = "/dashboard";
    } else {
        texto.innerText = "Respuesta Incorrecta";
        link.innerText = "Regresar";
        link.href = "/dashboard";
    }
}


for (const answer of answers) {
    answer.addEventListener("click", () => {
        if (done) {
            return;
        }
        result.removeAttribute("hidden")
        const correct = isCorrect(answer);
        sendResponse(correct);
        showResult(correct);
        done = true;
    })
}