const puzzlePiece = document.querySelector(".puzzle-piece");
const puzzleContainer = document.querySelector(".puzzle-container");

const addHiddenInputs = () => {
    const form = document.querySelector("form");

    ["pos_x_answer", "pos_y_answer"].forEach((name) => {
        const input = document.createElement("input");
        input.type = "text";
        input.name = name;
        input.id = `puzzle_${name}`;
        input.placeholder = name
            .replace(/_/g, " ")
            .replace(/\b\w/g, (c) => c.toUpperCase());
        input.style.display = "none";
        form.appendChild(input);
    });
};
addHiddenInputs();

const inputPosX = document.querySelector('input[id="puzzle_pos_x_answer"]');
const inputPosY = document.querySelector('input[id="puzzle_pos_y_answer"]');

let isDragging = false;
let offsetX = 0;
let offsetY = 0;

const fillInput = (e = undefined) => {
    const pieceRect = puzzlePiece.getBoundingClientRect();
    const containerRect = puzzleContainer.getBoundingClientRect();
    const pieceWidth = puzzlePiece.offsetWidth;
    const pieceHeight = puzzlePiece.offsetHeight;

    const clientX = e === undefined ? pieceRect.left : e.clientX;
    const clientY = e === undefined ? pieceRect.top : e.clientY;

    let x = clientX - containerRect.left - offsetX;
    let y = clientY - containerRect.top - offsetY;

    x = Math.max(0, Math.min(x, containerRect.width - pieceWidth));
    y = Math.max(0, Math.min(y, containerRect.height - pieceHeight));

    puzzlePiece.style.left = `${x}px`;
    puzzlePiece.style.top = `${y}px`;

    inputPosX.value = Math.round(x);
    inputPosY.value = Math.round(y);
};
fillInput();

puzzlePiece.addEventListener("mousedown", (e) => {
    isDragging = true;
    document.body.style.userSelect = "none";

    const pieceRect = puzzlePiece.getBoundingClientRect();

    offsetX = e.clientX - pieceRect.left;
    offsetY = e.clientY - pieceRect.top;
});

puzzleContainer.addEventListener("mousemove", (e) => {
    if (isDragging) {
        fillInput(e);
    }
});

puzzleContainer.addEventListener("mouseup", (e) => {
    if (isDragging) {
        isDragging = false;
        document.body.style.userSelect = "auto";
    }
});
