function drawMap(fontSize) {
	const canvas = document.createElement("canvas");
	const ctx = canvas.getContext("2d");
	const font = `${fontSize / window.devicePixelRatio}px Lucida Console`;
	ctx.font = font;
	const metrics = ctx.measureText("A");
	const charWidth = (metrics.actualBoundingBoxRight + metrics.actualBoundingBoxLeft);
	const charHeight = metrics.actualBoundingBoxDescent + metrics.actualBoundingBoxAscent;
	ctx.strokeRect(0, 0, charWidth, charHeight);
	const map = treasureMap.split("\n").map((line) => [...line]);
	canvas.height = charHeight * map.length;
	canvas.width = charWidth * map[0].length;
	canvas.style.height = `${canvas.height / window.devicePixelRatio}px`;
	canvas.style.width = `${canvas.width / window.devicePixelRatio}px`;
	ctx.font = font;
	ctx.textBaseline = "middle";
	ctx.textAlign = "center";
	for (let y = 0; y < map.length; y++) {
		for (let x = 0; x < map[y].length; x++) {
			ctx.fillStyle = map[y][x] === "\u2573" ? "red" : "black";
			ctx.fillText(map[y][x], charWidth * (x + 0.5), charHeight * (y + 0.5));
		}
	}
	document.body.appendChild(canvas);
}

{
	let fontSize = 50;
	while (true) {
		try {
			drawMap(fontSize);
			break;
		} catch (e) {
			if (e instanceof DOMException) {
				fontSize *= 0.99;
			} else {
				throw e;
			}
		}
	}
}